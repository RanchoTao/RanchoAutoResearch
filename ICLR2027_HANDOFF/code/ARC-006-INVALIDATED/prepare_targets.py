"""Create outcome-sanitized ARC-006 block-damage target tables."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


ARC_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ARC_ROOT.parents[1]


def anchor_path(run_id: int) -> Path:
    if run_id <= 5:
        base = REPO_ROOT / "meta_arc05" / "ARC-20260825-5060-002" / "experiments" / "raw"
    else:
        base = REPO_ROOT / "meta_arc05" / "ARC-20260826-5060-003" / "experiments" / "raw"
    return base / f"pythia-160m-seed{run_id}.json"


def extract(runs: list[int], steps: list[int], layers: list[int]) -> pd.DataFrame:
    rows = []
    for run_id in runs:
        payload = json.loads(anchor_path(run_id).read_text(encoding="utf-8"))
        checkpoints = {int(row["step"]): row for row in payload["checkpoints"]}
        for step in steps:
            checkpoint = checkpoints[step]
            by_layer: dict[int, list[dict]] = {layer: [] for layer in layers}
            for evaluation in checkpoint["seed_results"]:
                for row in evaluation["layers"]:
                    layer = int(row["layer"])
                    if layer in by_layer:
                        # Deliberately extract only blinded targeting fields.
                        by_layer[layer].append({
                            "kl": float(row["kl"]),
                            "nll_damage": float(row["nll_damage"]),
                        })
            for layer in layers:
                values = by_layer[layer]
                if len(values) != 3:
                    raise RuntimeError(f"expected 3 anchor selections for r{run_id}s{step}l{layer}")
                rows.append({
                    "target_id": f"r{run_id}_s{step}_l{layer}",
                    "run_id": run_id,
                    "step": step,
                    "progress": step / 143000,
                    "layer": layer,
                    "target_kl": sum(row["kl"] for row in values) / len(values),
                    "target_nll_damage": sum(row["nll_damage"] for row in values) / len(values),
                })
    frame = pd.DataFrame(rows).sort_values(["run_id", "step", "layer"])
    if frame["target_id"].duplicated().any():
        raise RuntimeError("duplicate target IDs")
    return frame


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--set", choices=["pilot", "confirmatory", "all"], default="all")
    args = parser.parse_args()
    target_dir = ARC_ROOT / "targets"
    target_dir.mkdir(parents=True, exist_ok=True)
    sets = []
    if args.set in {"pilot", "all"}:
        sets.append(("pilot", [1, 4], [14000, 143000], [2, 5, 8, 10]))
    if args.set in {"confirmatory", "all"}:
        sets.append(("confirmatory", [2, 3, 5, 6, 8], [14000, 72000, 143000], list(range(1, 11))))
    for name, runs, steps, layers in sets:
        frame = extract(runs, steps, layers)
        path = target_dir / f"{name}_targets.csv"
        frame.to_csv(path, index=False)
        print(f"{name}: {len(frame)} blinded targets -> {path}")


if __name__ == "__main__":
    main()
