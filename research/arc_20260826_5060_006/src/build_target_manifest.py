"""Build the outcome-blinded ARC-006 sealed target manifest and diagnostics."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


ARC_ROOT = Path(__file__).resolve().parents[1]
RUNS = [2, 3, 5, 6, 8]
STEPS = [14000, 72000, 143000]
LAYERS = list(range(1, 11))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=ARC_ROOT / "raw" / "targeting_confirmatory")
    args = parser.parse_args()
    rows = []
    checkpoint_rows = []
    raw_hashes = {}
    for run_id in RUNS:
        path = args.input / f"pythia-160m-seed{run_id}.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        raw_hashes[path.name] = sha256(path)
        if payload.get("blinded_metrics") != ["kl", "nll_damage"]:
            raise RuntimeError(f"blind schema mismatch in {path}")
        for checkpoint in payload["checkpoints"]:
            checkpoint_rows.append({
                "run_id": run_id, "step": checkpoint["step"],
                "runtime_seconds": checkpoint["runtime_seconds"],
                "peak_cuda_bytes": checkpoint["peak_cuda_bytes"],
                "harness_pass": checkpoint["harness_validation"]["pass"],
            })
            for target in checkpoint["targets"]:
                rows.append({key: target[key] for key in [
                    "target_id", "run_id", "step", "progress", "layer",
                    "target_kl", "target_nll_damage", "selected_beta",
                    "match_class", "absolute_kl_error", "relative_kl_error",
                    "absolute_nll_error", "relative_nll_error",
                    "achieved_kl", "achieved_nll_damage",
                    "activation_relative_magnitude", "activation_absolute_rms",
                    "objective", "boundary_selected", "trial_count",
                    "verification_kl_difference", "verification_nll_difference",
                ]})
    frame = pd.DataFrame(rows).sort_values(["run_id", "step", "layer"])
    checkpoints = pd.DataFrame(checkpoint_rows)
    expected = pd.MultiIndex.from_product(
        [RUNS, STEPS, LAYERS], names=["run_id", "step", "layer"]
    )
    actual = pd.MultiIndex.from_frame(frame[["run_id", "step", "layer"]])
    if len(frame) != 150 or frame["target_id"].duplicated().any() or not actual.equals(expected):
        raise RuntimeError("target key coverage is incomplete or duplicated")
    if not np.isfinite(frame.select_dtypes(include="number")).all().all():
        raise RuntimeError("nonfinite targeting metrics")
    class_a = frame["match_class"] == "A"
    class_ab = frame["match_class"].isin(["A", "B"])
    by_run = frame.assign(A=class_a, AB=class_ab).groupby("run_id")[["A", "AB"]].sum()
    by_step = frame.assign(A=class_a, AB=class_ab).groupby("step")[["A", "AB"]].sum()
    by_layer = frame.assign(A=class_a, AB=class_ab).groupby("layer")[["A", "AB"]].sum()
    checks = {
        "class_a_at_least_70": int(class_a.sum()) >= 70,
        "class_ab_at_least_113": int(class_ab.sum()) >= 113,
        "every_run_a_at_least_8": bool((by_run["A"] >= 8).all()),
        "every_run_ab_at_least_20": bool((by_run["AB"] >= 20).all()),
        "every_step_ab_at_least_30": bool((by_step["AB"] >= 30).all()),
        "every_layer_a_at_least_2": bool((by_layer["A"] >= 2).all()),
        "every_layer_ab_at_least_8": bool((by_layer["AB"] >= 8).all()),
        "all_harness_pass": bool(checkpoints["harness_pass"].all()),
        "median_a_relative_kl_error_le_005": bool(
            frame.loc[class_a, "relative_kl_error"].median() <= 0.05
        ),
        "median_a_relative_nll_error_le_005": bool(
            frame.loc[class_a, "relative_nll_error"].median() <= 0.05
        ),
        "verification_exact": bool(
            frame[["verification_kl_difference", "verification_nll_difference"]]
            .abs().max().max() <= 1e-12
        ),
    }
    diagnostics = {
        "targets": len(frame),
        "class_counts": frame["match_class"].value_counts().to_dict(),
        "class_a_coverage": float(class_a.mean()),
        "class_ab_coverage": float(class_ab.mean()),
        "mean_absolute_kl_error": float(frame["absolute_kl_error"].mean()),
        "mean_relative_kl_error": float(frame["relative_kl_error"].mean()),
        "mean_absolute_nll_error": float(frame["absolute_nll_error"].mean()),
        "mean_relative_nll_error": float(frame["relative_nll_error"].mean()),
        "coverage_by_run": by_run.reset_index().to_dict("records"),
        "coverage_by_step": by_step.reset_index().to_dict("records"),
        "coverage_by_layer": by_layer.reset_index().to_dict("records"),
        "boundary_solutions": int(frame["boundary_selected"].sum()),
        "checkpoint_runtime_seconds_sum": float(checkpoints["runtime_seconds"].sum()),
        "peak_cuda_bytes": int(checkpoints["peak_cuda_bytes"].max()),
        "quality_checks": checks,
        "quality_gate_pass": bool(all(checks.values())),
        "raw_sha256": raw_hashes,
    }
    frame.to_csv(ARC_ROOT / "target_manifest.csv", index=False)
    out = ARC_ROOT / "match_diagnostics"
    out.mkdir(exist_ok=True)
    checkpoints.to_csv(out / "targeting_checkpoints.csv", index=False)
    (out / "targeting_quality.json").write_text(
        json.dumps(diagnostics, indent=2), encoding="utf-8"
    )
    print(json.dumps(diagnostics, indent=2))


if __name__ == "__main__":
    main()
