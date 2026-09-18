"""Aggregate the pre-registered ARC-21 MVP without additional model runs."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import numpy as np
from scipy import stats


ROOT = Path(__file__).resolve().parents[1]
INPUTS = [
    ROOT / "experiments" / "mvp_seed11" / "results.json",
    ROOT / "experiments" / "replication" / "results.json",
]
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
ORDER = [
    "outcome_only", "full_process", "random_1", "uniform_1",
    "midpoint_1", "early_1", "late_1",
]
LABELS = {
    "outcome_only": "Outcome only", "full_process": "Full process",
    "random_1": "Random-1", "uniform_1": "Uniform-1",
    "midpoint_1": "Midpoint-1", "early_1": "Early-1", "late_1": "Late-1",
}


def mean_sd(values: list[float]) -> dict[str, float]:
    array = np.asarray(values, dtype=float)
    return {"mean": float(array.mean()), "sd": float(array.std(ddof=1))}


def paired(rows: list[dict], a: str, b: str) -> dict:
    by_seed = {(row["seed"], row["condition"]): row for row in rows}
    seeds = sorted({row["seed"] for row in rows})
    differences = np.asarray([
        by_seed[(seed, a)]["ood_accuracy"] - by_seed[(seed, b)]["ood_accuracy"]
        for seed in seeds
    ])
    test = stats.ttest_rel(
        [by_seed[(seed, a)]["ood_accuracy"] for seed in seeds],
        [by_seed[(seed, b)]["ood_accuracy"] for seed in seeds],
    )
    return {
        "a": a, "b": b, "seeds": seeds,
        "differences": differences.tolist(),
        "mean_difference": float(differences.mean()),
        "sd_difference": float(differences.std(ddof=1)),
        "paired_t": float(test.statistic), "p_two_sided": float(test.pvalue),
    }


def main() -> None:
    rows: list[dict] = []
    for path in INPUTS:
        rows.extend(json.loads(path.read_text(encoding="utf-8")))
    assert len(rows) == 21, f"expected 21 runs, found {len(rows)}"
    assert sorted({row["seed"] for row in rows}) == [11, 23, 37]

    RESULTS.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)

    with (RESULTS / "all_runs.csv").open("w", newline="", encoding="utf-8") as handle:
        fields = ["seed", "condition", "id_accuracy", "ood_accuracy", "runtime_seconds",
                  "peak_cuda_bytes", "depth_2", "depth_3", "depth_4", "depth_5",
                  "depth_6", "depth_7", "depth_8"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in sorted(rows, key=lambda x: (x["seed"], ORDER.index(x["condition"]))):
            writer.writerow({
                "seed": row["seed"], "condition": row["condition"],
                "id_accuracy": row["id_accuracy"], "ood_accuracy": row["ood_accuracy"],
                "runtime_seconds": row["runtime_seconds"],
                "peak_cuda_bytes": row["peak_cuda_bytes"],
                **{f"depth_{depth}": row["accuracy_by_depth"][str(depth)] for depth in range(2, 9)},
            })

    summary = {}
    for condition in ORDER:
        selected = [row for row in rows if row["condition"] == condition]
        summary[condition] = {
            "id_accuracy": mean_sd([row["id_accuracy"] for row in selected]),
            "ood_accuracy": mean_sd([row["ood_accuracy"] for row in selected]),
            "by_seed": {str(row["seed"]): row["ood_accuracy"] for row in selected},
            "by_depth_mean": {
                str(depth): float(np.mean([row["accuracy_by_depth"][str(depth)] for row in selected]))
                for depth in range(2, 9)
            },
        }

    comparisons = {
        "midpoint_vs_random": paired(rows, "midpoint_1", "random_1"),
        "midpoint_vs_uniform": paired(rows, "midpoint_1", "uniform_1"),
        "late_vs_early": paired(rows, "late_1", "early_1"),
        "late_vs_random": paired(rows, "late_1", "random_1"),
        "full_vs_outcome": paired(rows, "full_process", "outcome_only"),
    }
    total_runtime = sum(row["runtime_seconds"] for row in rows)
    output = {
        "n_seeds": 3, "seeds": [11, 23, 37], "summary": summary,
        "paired_comparisons": comparisons,
        "total_training_runtime_seconds": total_runtime,
        "max_peak_cuda_bytes": max(row["peak_cuda_bytes"] for row in rows),
        "label_budget": {"outcome_only": 0, "k1_strategies": 1, "full_process_mean": 2},
    }
    (RESULTS / "aggregate.json").write_text(json.dumps(output, indent=2), encoding="utf-8")

    means = [summary[c]["ood_accuracy"]["mean"] * 100 for c in ORDER]
    sds = [summary[c]["ood_accuracy"]["sd"] * 100 for c in ORDER]
    fig, ax = plt.subplots(figsize=(9.2, 4.8))
    colors = ["#777777", "#4C78A8", "#F58518", "#72B7B2", "#E45756", "#54A24B", "#B279A2"]
    ax.bar(range(len(ORDER)), means, yerr=sds, capsize=4, color=colors)
    ax.set_xticks(range(len(ORDER)), [LABELS[c] for c in ORDER], rotation=25, ha="right")
    ax.set_ylabel("OOD accuracy, depths 5–8 (%)")
    ax.set_title("ARC-21: supervision placement under a fixed one-state budget")
    ax.grid(axis="y", alpha=.25)
    fig.tight_layout()
    fig.savefig(FIGURES / "figure1_strategy_ood_accuracy.png", dpi=180)
    plt.close(fig)

    # Label budget: full-process averages 1, 2, and 3 intermediate labels for train depths 2, 3, 4.
    budget = {"outcome_only": 0.0, "random_1": 1.0, "uniform_1": 1.0,
              "midpoint_1": 1.0, "early_1": 1.0, "late_1": 1.0,
              "full_process": 2.0}
    fig, ax = plt.subplots(figsize=(7.5, 5.0))
    for condition in ORDER:
        ax.scatter(budget[condition], summary[condition]["ood_accuracy"]["mean"] * 100,
                   s=70, label=LABELS[condition])
    ax.set_xlabel("Mean intermediate labels per training example")
    ax.set_ylabel("OOD accuracy (%)")
    ax.set_title("Label budget does not produce a monotonic OOD gain")
    ax.grid(alpha=.25)
    ax.legend(fontsize=8, ncol=2)
    fig.tight_layout()
    fig.savefig(FIGURES / "figure2_budget_efficiency.png", dpi=180)
    plt.close(fig)

    outcome = summary["outcome_only"]["ood_accuracy"]["mean"]
    positions = ["early_1", "midpoint_1", "late_1"]
    marginal = [(summary[c]["ood_accuracy"]["mean"] - outcome) * 100 for c in positions]
    marginal_sd = [summary[c]["ood_accuracy"]["sd"] * 100 for c in positions]
    fig, ax = plt.subplots(figsize=(6.8, 4.8))
    ax.errorbar([1, 2, 3], marginal, yerr=marginal_sd, marker="o", capsize=5, linewidth=2)
    ax.axhline(0, color="black", linewidth=1, linestyle="--")
    ax.set_xticks([1, 2, 3], ["Early", "Midpoint", "Late"])
    ax.set_ylabel("OOD change vs outcome-only (percentage points)")
    ax.set_title("Late-state supervision shows a small, non-diagnostic advantage")
    ax.grid(alpha=.25)
    fig.tight_layout()
    fig.savefig(FIGURES / "figure3_position_marginal_value.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6.5, 5.2))
    for condition in ORDER:
        ax.scatter(summary[condition]["id_accuracy"]["mean"] * 100,
                   summary[condition]["ood_accuracy"]["mean"] * 100,
                   s=70, label=LABELS[condition])
    ax.set_xlabel("ID accuracy, depths 2–4 (%)")
    ax.set_ylabel("OOD accuracy, depths 5–8 (%)")
    ax.set_title("Near-perfect interpolation hides poor depth extrapolation")
    ax.set_xlim(99.95, 100.01)
    ax.xaxis.set_major_formatter(ScalarFormatter(useOffset=False))
    ax.grid(alpha=.25)
    ax.legend(fontsize=8, ncol=2)
    fig.tight_layout()
    fig.savefig(FIGURES / "figure4_id_vs_ood.png", dpi=180)
    plt.close(fig)

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
