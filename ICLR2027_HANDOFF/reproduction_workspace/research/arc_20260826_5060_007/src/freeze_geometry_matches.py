"""Freeze outcome-blind geometry-compatible ARC-006 Class A cells."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd


ARC_ROOT = Path(__file__).resolve().parents[1]
RUNS = [2, 3, 5, 6, 8]
STEPS = [14000, 72000, 143000]


def load_geometry_only() -> pd.DataFrame:
    allowed = [
        "target_id", "run_id", "step", "layer", "match_class", "family",
        "delta_b_mean", "logit_delta_norm_mean", "abs_cosine_alignment_mean",
    ]
    rows = []
    for run_id in RUNS:
        path = ARC_ROOT / "raw" / "geometry" / f"pythia-160m-seed{run_id}.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        for checkpoint in payload["checkpoints"]:
            for row in checkpoint["geometry_rows"]:
                rows.append({field: row[field] for field in allowed})
    frame = pd.DataFrame(rows)
    if len(frame) != 300 or frame.duplicated(["target_id", "family"]).any():
        raise RuntimeError("geometry-only key coverage failure")
    return frame


def main() -> None:
    frame = load_geometry_only()
    primary = frame[frame["match_class"] == "A"].copy()
    if len(primary) != 206:
        raise RuntimeError(f"expected 206 Class A family rows, found {len(primary)}")
    pooled_delta_b_sd = float(primary["delta_b_mean"].std(ddof=0))
    if not np.isfinite(pooled_delta_b_sd) or pooled_delta_b_sd <= 0:
        raise RuntimeError("invalid pooled delta-b scale")
    wide = primary.pivot(index=["target_id", "run_id", "step", "layer"], columns="family")
    wide.columns = [f"{metric}_{family}" for metric, family in wide.columns]
    wide = wide.reset_index()
    wide["delta_b_standardized_difference"] = (
        (wide["delta_b_mean_noise"] - wide["delta_b_mean_block"]).abs()
        / pooled_delta_b_sd
    )
    wide["absolute_log_norm_ratio"] = (
        np.log(wide["logit_delta_norm_mean_noise"] / wide["logit_delta_norm_mean_block"])
    ).abs()
    wide["absolute_cosine_difference"] = (
        wide["abs_cosine_alignment_mean_noise"]
        - wide["abs_cosine_alignment_mean_block"]
    ).abs()
    wide["pass_delta_b"] = wide["delta_b_standardized_difference"] <= 0.50
    wide["pass_norm"] = wide["absolute_log_norm_ratio"] <= math.log(1.25)
    wide["pass_cosine"] = wide["absolute_cosine_difference"] <= 0.10
    wide["geometry_match"] = wide[["pass_delta_b", "pass_norm", "pass_cosine"]].all(axis=1)
    wide["failure_reason"] = wide.apply(
        lambda row: ";".join(
            name for name, passed in [
                ("delta_b", row["pass_delta_b"]),
                ("norm", row["pass_norm"]),
                ("cosine", row["pass_cosine"]),
            ] if not passed
        ), axis=1,
    )
    output_fields = [
        "target_id", "run_id", "step", "layer", "geometry_match",
        "delta_b_standardized_difference", "absolute_log_norm_ratio",
        "absolute_cosine_difference", "pass_delta_b", "pass_norm",
        "pass_cosine", "failure_reason",
    ]
    wide[output_fields].to_csv(ARC_ROOT / "geometry_match_manifest.csv", index=False)

    selected = wide[wide["geometry_match"]]
    by_run = {str(run): int((selected["run_id"] == run).sum()) for run in RUNS}
    by_step = {str(step): int((selected["step"] == step).sum()) for step in STEPS}
    quality = {
        "class_a_cells": int(len(wide)),
        "matched_cells": int(len(selected)),
        "coverage": float(len(selected) / len(wide)),
        "pooled_delta_b_sd": pooled_delta_b_sd,
        "calipers": {
            "delta_b_standardized_difference": 0.50,
            "absolute_log_norm_ratio": math.log(1.25),
            "absolute_cosine_difference": 0.10,
        },
        "coverage_by_run": by_run,
        "coverage_by_step": by_step,
        "support_checks": {
            "at_least_30": bool(len(selected) >= 30),
            "each_run_at_least_3": bool(all(value >= 3 for value in by_run.values())),
            "each_step_at_least_5": bool(all(value >= 5 for value in by_step.values())),
        },
    }
    quality["support_adequate"] = bool(all(quality["support_checks"].values()))
    (ARC_ROOT / "geometry_match_quality.json").write_text(
        json.dumps(quality, indent=2), encoding="utf-8"
    )
    print(json.dumps({
        "class_a_cells": quality["class_a_cells"],
        "matched_cells": quality["matched_cells"],
        "coverage": quality["coverage"],
        "support_adequate": quality["support_adequate"],
    }))


if __name__ == "__main__":
    main()

