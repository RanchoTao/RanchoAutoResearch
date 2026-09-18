"""Outcome-blind solver pilot using only ARC-008 calibration response curves."""

from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARC008 = ROOT.parent / "arc_20260827_5060_008"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def nondecreasing(values: list[float], tolerance: float = 1e-10) -> bool:
    return all(right + tolerance >= left for left, right in zip(values, values[1:]))


def crossings(values: list[float], target: float) -> int:
    shifted = [value - target for value in values]
    return sum(
        left == 0 or right == 0 or left * right < 0
        for left, right in zip(shifted, shifted[1:])
    )


def main() -> None:
    targets = read_csv(ROOT / "sanitized_targets.csv")
    candidates: list[dict[str, str]] = []
    for path in sorted((ARC008 / "raw").glob("calibrate_seed*.csv")):
        candidates.extend(read_csv(path))

    target_by_id = {row["target_id"]: row for row in targets}
    grouped: dict[tuple[int, int], list[dict[str, str]]] = defaultdict(list)
    for row in targets:
        grouped[(int(row["run_id"]), int(row["step"]))].append(row)

    # Ten fixed strata: every run twice and all checkpoints represented.
    requested = [
        (2, 14000), (2, 72000), (3, 72000), (3, 143000), (5, 14000),
        (5, 143000), (6, 72000), (6, 143000), (8, 14000), (8, 72000),
    ]
    pilot = []
    for run_id, step in requested:
        choices = sorted(grouped[(run_id, step)], key=lambda row: (int(row["layer"]), row["target_id"]))
        if not choices:
            raise SystemExit(f"LOCAL_ARTIFACT_MISSING: no pilot cell for run={run_id}, step={step}")
        pilot.append(choices[len(choices) // 2])

    rows = []
    for target in pilot:
        for family in ("block", "noise"):
            curve = sorted(
                [row for row in candidates if row["target_id"] == target["target_id"] and row["family_direction"] == family],
                key=lambda row: float(row["alpha"]),
            )
            if len(curve) != 6:
                raise SystemExit(f"LOCAL_ARTIFACT_MISSING: incomplete ARC-008 curve for {target['target_id']} {family}")
            alphas = [float(row["alpha"]) for row in curve]
            kl = [float(row["kl"]) for row in curve]
            nll = [float(row["nll_damage"]) for row in curve]
            target_kl = float(target_by_id[target["target_id"]]["target_kl"])
            target_nll = float(target_by_id[target["target_id"]]["target_nll_damage"])
            rows.append({
                "target_id": target["target_id"],
                "run_id": int(target["run_id"]),
                "step": int(target["step"]),
                "layer": int(target["layer"]),
                "family": family,
                "finite": all(math.isfinite(value) for value in alphas + kl + nll),
                "kl_nondecreasing": nondecreasing(kl),
                "nll_nondecreasing": nondecreasing(nll),
                "kl_bracketed": min(kl) <= target_kl <= max(kl),
                "nll_bracketed": min(nll) <= target_nll <= max(nll),
                "kl_crossings": crossings(kl, target_kl),
                "nll_crossings": crossings(nll, target_nll),
                "alpha_min": min(alphas),
                "alpha_max": max(alphas),
            })

    with (ROOT / "pilot_curve_diagnostics.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    summary = {
        "outcome_blind": True,
        "pilot_cells": len(pilot),
        "curves": len(rows),
        "finite_curves": sum(row["finite"] for row in rows),
        "kl_nondecreasing": sum(row["kl_nondecreasing"] for row in rows),
        "nll_nondecreasing": sum(row["nll_nondecreasing"] for row in rows),
        "kl_bracketed": sum(row["kl_bracketed"] for row in rows),
        "nll_bracketed": sum(row["nll_bracketed"] for row in rows),
        "multiple_kl_crossings": sum(row["kl_crossings"] > 1 for row in rows),
        "multiple_nll_crossings": sum(row["nll_crossings"] > 1 for row in rows),
        "selected_solver_family": "bracketed_bisection_with_bounded_high_resolution_fallback",
    }
    (ROOT / "pilot_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

