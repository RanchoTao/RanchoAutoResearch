"""Damage-support-only calibration for ARC-005.

This script intentionally never prints or saves S, D_S, or checkpoint-direction
contrasts. Agreement is used only as a hidden catastrophic boolean mandated by
the preregistration.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import yaml


ARC_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ARC_ROOT.parents[1]


def anchor_path(run_id: int) -> Path:
    return (
        REPO_ROOT / "meta_arc05" / "ARC-20260825-5060-002" / "experiments" / "raw"
        / f"pythia-160m-seed{run_id}.json"
    )


def joint_match(noise: dict, block: dict, relative: float = 0.10) -> bool:
    kl_gap = abs(noise["kl"] - block["kl"])
    nll_gap = abs(noise["nll_damage"] - block["nll_damage"])
    kl_caliper = max(0.01, relative * (abs(noise["kl"]) + abs(block["kl"])) / 2)
    nll_caliper = max(
        0.015,
        relative * (abs(noise["nll_damage"]) + abs(block["nll_damage"])) / 2,
    )
    return kl_gap <= kl_caliper and nll_gap <= nll_caliper


def main() -> None:
    config = yaml.safe_load((ARC_ROOT / "configs" / "calibration.yaml").read_text())
    noise_rows = []
    block_rows = []
    for run_id in config["run_ids"]:
        raw = json.loads(
            (ARC_ROOT / config["output_dir"] / f"pythia-160m-seed{run_id}.json").read_text()
        )
        if len(raw["checkpoints"]) != len(config["checkpoint_steps"]):
            raise RuntimeError(f"incomplete calibration run {run_id}")
        for checkpoint in raw["checkpoints"]:
            if not checkpoint["harness_validation"]["pass"]:
                raise RuntimeError(f"harness failure run {run_id} step {checkpoint['step']}")
            for evaluation in checkpoint["evaluation_results"]:
                for row in evaluation["interventions"]:
                    noise_rows.append({
                        "run_id": run_id,
                        "step": checkpoint["step"],
                        "layer": row["layer"],
                        "beta": row["beta"],
                        "direction_id": row["noise_direction_id"],
                        "kl": row["kl"],
                        "nll_damage": row["nll_damage"],
                        "m_rel": row["activation_relative_magnitude"],
                        "intervened_nll": row["intervened_nll"],
                        "catastrophic": bool(
                            row["intervened_nll"] > config["catastrophic_max_nll"]
                            or row["kl"] > config["catastrophic_max_kl"]
                            or row["top1_agreement"] < config["catastrophic_min_agreement"]
                        ),
                    })

        anchor = json.loads(anchor_path(run_id).read_text())
        checkpoints = {row["step"]: row for row in anchor["checkpoints"]}
        for step in config["checkpoint_steps"]:
            checkpoint = checkpoints[step]
            evaluation = next(
                row for row in checkpoint["seed_results"] if row["evaluation_seed"] == 11
            )
            layers = {row["layer"]: row for row in evaluation["layers"]}
            for layer in config["layers"]:
                row = layers[layer]
                block_rows.append({
                    "run_id": run_id,
                    "step": step,
                    "layer": layer,
                    "kl": row["kl"],
                    "nll_damage": row["nll_damage"],
                })

    noise = pd.DataFrame(noise_rows)
    cells = noise.groupby(["run_id", "step", "layer", "beta"], as_index=False).agg(
        kl=("kl", "mean"),
        nll_damage=("nll_damage", "mean"),
        m_rel=("m_rel", "mean"),
        intervened_nll=("intervened_nll", "mean"),
        catastrophic=("catastrophic", "max"),
    )
    blocks = pd.DataFrame(block_rows)
    q_edges = np.quantile(blocks["kl"], [0, 0.25, 0.5, 0.75, 1.0])
    summaries = []
    for beta, group in cells.groupby("beta", sort=True):
        inside = (
            group["kl"].between(config["anchor_kl_q05"], config["anchor_kl_q95"])
            & group["nll_damage"].between(
                config["anchor_nll_damage_q05"], config["anchor_nll_damage_q95"]
            )
        )
        matches = 0
        matched_quartiles = set()
        for block in block_rows:
            candidate = group[
                (group["run_id"] == block["run_id"])
                & (group["step"] == block["step"])
                & (group["layer"] == block["layer"])
            ]
            if len(candidate) != 1:
                raise RuntimeError("calibration cell key is not unique")
            row = candidate.iloc[0].to_dict()
            if joint_match(row, block):
                matches += 1
                quartile = int(np.clip(np.digitize(block["kl"], q_edges[1:-1]), 0, 3))
                matched_quartiles.add(quartile)
        catastrophic_rate = float(group["catastrophic"].mean())
        finite = bool(np.isfinite(group[["kl", "nll_damage", "m_rel"]]).all().all())
        inside_rate = float(inside.mean())
        retain = bool(
            finite and catastrophic_rate <= 0.05 and inside_rate >= 0.20 and matches >= 1
        )
        summaries.append({
            "beta": float(beta),
            "cells": int(len(group)),
            "finite": finite,
            "catastrophic_cells": int(group["catastrophic"].sum()),
            "catastrophic_rate": catastrophic_rate,
            "joint_anchor_inside_cells": int(inside.sum()),
            "joint_anchor_inside_rate": inside_rate,
            "median_measured_relative_magnitude": float(group["m_rel"].median()),
            "median_kl": float(group["kl"].median()),
            "median_nll_damage": float(group["nll_damage"].median()),
            "exact_anchor_matches": matches,
            "matched_anchor_quartiles": sorted(matched_quartiles),
            "median_anchor_kl_quartile": int(
                np.clip(np.digitize(float(group["kl"].median()), q_edges[1:-1]), 0, 3)
            ),
            "retain": retain,
        })

    # The frozen rule also retains a beta needed to cover a different anchor
    # damage quartile. KL is the frozen primary functional-damage variable;
    # NLL remains constrained by the joint-support requirement above. For each
    # uncovered quartile, retain the eligible beta closest to that quartile's
    # KL midpoint, with smaller beta as a stable tie-break.
    covered_by_matches = {
        q for row in summaries if row["retain"] for q in row["matched_anchor_quartiles"]
    }
    for quartile in range(4):
        if quartile in covered_by_matches:
            continue
        center = (q_edges[quartile] + q_edges[quartile + 1]) / 2
        candidates = [
            row for row in summaries
            if row["finite"]
            and row["catastrophic_rate"] <= 0.05
            and row["joint_anchor_inside_rate"] >= 0.20
            and row["median_anchor_kl_quartile"] == quartile
        ]
        if candidates:
            chosen = min(candidates, key=lambda row: (abs(row["median_kl"] - center), row["beta"]))
            chosen["retain"] = True
            chosen["retention_reason"] = "uncovered_anchor_kl_quartile"
            covered_by_matches.add(quartile)
    for row in summaries:
        row.setdefault(
            "retention_reason",
            "exact_cell_match" if row["retain"] else "failed_frozen_inclusion_rule",
        )

    retained = [row["beta"] for row in summaries if row["retain"]]
    quartiles = sorted(
        {q for row in summaries if row["retain"] for q in row["matched_anchor_quartiles"]}
        | {row["median_anchor_kl_quartile"] for row in summaries if row["retain"]}
    )
    feasibility = len(retained) >= 3 and len(quartiles) >= 2
    output = {
        "arc": "ARC-20260826-5060-005",
        "mode": "damage-support-only calibration",
        "agreement_values_revealed": False,
        "candidate_betas": summaries,
        "retained_betas": retained,
        "covered_anchor_quartiles": quartiles,
        "feasibility_pass": feasibility,
        "block_anchor_cells": len(block_rows),
        "noise_aggregated_cells": len(cells),
    }
    target = ARC_ROOT / "processed" / "calibration_support.json"
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
