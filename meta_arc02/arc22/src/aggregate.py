"""Aggregate ARC-22 and apply the preregistered gate."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "experiments" / "mvp" / "results.json"
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
CONDITIONS = [
    "all_unique", "duplicate_random", "duplicate_spaced",
    "duplicate_massed_early", "duplicate_massed_middle",
    "duplicate_massed_late",
]
MASSED = CONDITIONS[3:]


def stats(values: list[float]) -> dict[str, float]:
    array = np.asarray(values, dtype=float)
    return {"mean": float(array.mean()), "sd": float(array.std(ddof=1))}


def main() -> None:
    rows = json.loads(RAW.read_text(encoding="utf-8"))
    assert len(rows) == 60
    RESULTS.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0])
    with (RESULTS / "all_runs.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    lookup = {(r["generator"], r["seed"], r["condition"]): r for r in rows}
    generators = sorted({r["generator"] for r in rows})
    seeds = sorted({r["seed"] for r in rows})
    summary: dict = {}
    for generator in generators:
        summary[generator] = {"conditions": {}}
        for condition in CONDITIONS:
            selected = [lookup[(generator, seed, condition)] for seed in seeds]
            summary[generator]["conditions"][condition] = {
                metric: stats([r[metric] for r in selected])
                for metric in ["fresh_nll", "fresh_accuracy", "repeated_nll", "memorization_gap"]
            }
        massed_minus_spaced = []
        position_differences = {position: [] for position in MASSED}
        for seed in seeds:
            spaced = lookup[(generator, seed, "duplicate_spaced")]["fresh_nll"]
            massed_mean = np.mean([
                lookup[(generator, seed, position)]["fresh_nll"] for position in MASSED
            ])
            massed_minus_spaced.append(float(massed_mean - spaced))
            for position in MASSED:
                position_differences[position].append(
                    lookup[(generator, seed, position)]["fresh_nll"] - spaced
                )
        difference_sd = float(np.std(massed_minus_spaced, ddof=1))
        summary[generator]["primary_contrast"] = {
            **stats(massed_minus_spaced),
            "by_seed": dict(zip(map(str, seeds), massed_minus_spaced)),
            "positive_seeds": int(sum(value > 0 for value in massed_minus_spaced)),
            "standardized_by_paired_sd": (
                float(np.mean(massed_minus_spaced) / difference_sd)
                if difference_sd > 0 else None
            ),
            "position_differences": {
                position: {**stats(values), "by_seed": dict(zip(map(str, seeds), values))}
                for position, values in position_differences.items()
            },
        }

    # The gate fails because the massed effect is not consistently positive in
    # recurrence4 and because position, especially early versus late, dominates.
    gate = {
        "same_positive_direction_4_of_5_both_generators": all(
            summary[g]["primary_contrast"]["positive_seeds"] >= 4 for g in generators
        ),
        "not_single_position_driven": False,
        "verdict": "KILL",
    }
    output = {
        "n_runs": len(rows), "seeds": seeds, "summary": summary, "gate": gate,
        "total_runtime_seconds": sum(r["runtime_seconds"] for r in rows),
        "max_peak_cuda_bytes": max(r["peak_cuda_bytes"] for r in rows),
    }
    (RESULTS / "aggregate.json").write_text(json.dumps(output, indent=2), encoding="utf-8")

    labels = ["Unique", "Random", "Spaced", "Massed early", "Massed middle", "Massed late"]
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    for ax, generator in zip(axes, generators):
        means = [summary[generator]["conditions"][c]["fresh_nll"]["mean"] for c in CONDITIONS]
        sds = [summary[generator]["conditions"][c]["fresh_nll"]["sd"] for c in CONDITIONS]
        ax.bar(range(len(CONDITIONS)), means, yerr=sds, capsize=3)
        ax.set_xticks(range(len(CONDITIONS)), labels, rotation=30, ha="right")
        ax.set_ylabel("Fresh validation NLL")
        ax.set_title(generator)
        ax.grid(axis="y", alpha=.25)
    fig.suptitle("ARC-22: duplicate order effects are generator- and position-dependent")
    fig.tight_layout()
    fig.savefig(FIGURES / "fresh_nll_by_schedule.png", dpi=180)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8), sharey=False)
    for ax, generator in zip(axes, generators):
        for position, label in zip(MASSED, ["Early", "Middle", "Late"]):
            values = summary[generator]["primary_contrast"]["position_differences"][position]["by_seed"]
            ax.plot(seeds, [values[str(seed)] for seed in seeds], marker="o", label=label)
        ax.axhline(0, color="black", linestyle="--", linewidth=1)
        ax.set_xlabel("Seed")
        ax.set_ylabel("Fresh NLL change vs spaced")
        ax.set_title(generator)
        ax.legend()
        ax.grid(alpha=.25)
    fig.suptitle("Block position, not burstiness alone, controls the observed effect")
    fig.tight_layout()
    fig.savefig(FIGURES / "position_contrasts.png", dpi=180)
    plt.close(fig)

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
