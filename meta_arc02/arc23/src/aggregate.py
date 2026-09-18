"""Aggregate ARC-23 and apply its preregistered decision gate."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import spearmanr


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "experiments" / "mvp" / "results.json"
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
COHORTS = {"order12": 12, "order24": 24}


def stats(values: list[float]) -> dict[str, float]:
    array = np.asarray(values, dtype=float)
    return {
        "mean": float(array.mean()),
        "sd": float(array.std(ddof=1)),
        "min": float(array.min()),
        "max": float(array.max()),
    }


def correlation(x: list[float], y: list[float]) -> dict[str, float]:
    result = spearmanr(x, y)
    return {"rho": float(result.statistic), "p_value_descriptive": float(result.pvalue)}


def main() -> None:
    rows = json.loads(RAW.read_text(encoding="utf-8"))
    assert len(rows) == 45, f"expected 45 runs, got {len(rows)}"
    RESULTS.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)

    flat_fields = [
        "group", "order", "quotient_size", "compression_ratio", "seed", "parameters",
        "quotient_gap_auc", "id_exact_accuracy", "ood_exact_accuracy", "runtime_seconds",
        "peak_cuda_bytes",
    ]
    with (RESULTS / "all_runs.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=flat_fields)
        writer.writeheader()
        writer.writerows([{field: row[field] for field in flat_fields} for row in rows])

    checkpoint_rows = []
    for row in rows:
        for checkpoint in row["checkpoints"]:
            checkpoint_rows.append({
                "group": row["group"], "order": row["order"], "seed": row["seed"],
                **checkpoint,
            })
    with (RESULTS / "trajectories.csv").open("w", newline="", encoding="utf-8") as handle:
        fields = ["group", "order", "seed", "step", "exact_accuracy", "quotient_accuracy", "nll"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(checkpoint_rows)

    group_names = sorted({row["group"] for row in rows}, key=lambda name: (
        next(row["order"] for row in rows if row["group"] == name),
        next(row["compression_ratio"] for row in rows if row["group"] == name), name,
    ))
    group_summary: dict[str, dict] = {}
    for group in group_names:
        selected = [row for row in rows if row["group"] == group]
        group_summary[group] = {
            "order": selected[0]["order"],
            "quotient_size": selected[0]["quotient_size"],
            "compression_ratio": selected[0]["compression_ratio"],
            "id_exact_accuracy": stats([row["id_exact_accuracy"] for row in selected]),
            "ood_exact_accuracy": stats([row["ood_exact_accuracy"] for row in selected]),
            "quotient_gap_auc": stats([row["quotient_gap_auc"] for row in selected]),
            "id_pass_seeds": sum(row["id_exact_accuracy"] >= .95 for row in selected),
        }

    cohort_summary: dict[str, dict] = {}
    for cohort, order in COHORTS.items():
        groups = [group for group in group_names if group_summary[group]["order"] == order]
        compression = [group_summary[group]["compression_ratio"] for group in groups]
        gaps = [group_summary[group]["quotient_gap_auc"]["mean"] for group in groups]
        id_accuracy = [group_summary[group]["id_exact_accuracy"]["mean"] for group in groups]
        seed_rhos = {}
        for seed in sorted({row["seed"] for row in rows}):
            seed_rows = [row for row in rows if row["order"] == order and row["seed"] == seed]
            seed_rows.sort(key=lambda row: (row["compression_ratio"], row["group"]))
            seed_rhos[str(seed)] = correlation(
                [row["compression_ratio"] for row in seed_rows],
                [row["quotient_gap_auc"] for row in seed_rows],
            )["rho"]
        cohort_summary[cohort] = {
            "groups": groups,
            "compression_vs_gap": correlation(compression, gaps),
            "compression_vs_id_accuracy": correlation(compression, id_accuracy),
            "positive_gap_ordering_seeds": sum(rho >= .7 for rho in seed_rhos.values()),
            "seed_rhos": seed_rhos,
        }

    overall_gap_ood = correlation(
        [row["quotient_gap_auc"] for row in rows],
        [row["ood_exact_accuracy"] for row in rows],
    )
    overall_gap_id = correlation(
        [row["quotient_gap_auc"] for row in rows],
        [row["id_exact_accuracy"] for row in rows],
    )
    failing_groups = [
        group for group, values in group_summary.items()
        if values["id_pass_seeds"] < 5
    ]
    gate = {
        "all_runs_id_exact_at_least_0_95": not failing_groups,
        "groups_failing_id_control": failing_groups,
        "order12_compression_gap_rho_at_least_0_7": (
            cohort_summary["order12"]["compression_vs_gap"]["rho"] >= .7
        ),
        "order24_compression_gap_rho_at_least_0_7": (
            cohort_summary["order24"]["compression_vs_gap"]["rho"] >= .7
        ),
        "overall_gap_ood_rho_at_most_minus_0_7": overall_gap_ood["rho"] <= -.7,
        "direction_at_least_4_of_5_both_cohorts": all(
            values["positive_gap_ordering_seeds"] >= 4
            for values in cohort_summary.values()
        ),
        "scientific_interpretation": "INCONCLUSIVE",
        "meta_arc_action": "KILL",
        "reason": (
            "The preregistered difficulty control failed for multiple groups; quotient-gap "
            "is strongly confounded with final exact-task accuracy, while OOD accuracy is near chance."
        ),
    }
    output = {
        "n_runs": len(rows),
        "n_seeds": len({row["seed"] for row in rows}),
        "group_summary": group_summary,
        "cohort_summary": cohort_summary,
        "overall_gap_vs_ood": overall_gap_ood,
        "overall_gap_vs_id": overall_gap_id,
        "gate": gate,
        "total_runtime_seconds": sum(row["runtime_seconds"] for row in rows),
        "max_peak_cuda_bytes": max(row["peak_cuda_bytes"] for row in rows),
    }
    (RESULTS / "aggregate.json").write_text(json.dumps(output, indent=2), encoding="utf-8")

    colors = {12: "#2f6f9f", 24: "#d97706"}
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.6))
    for group in group_names:
        values = group_summary[group]
        color = colors[values["order"]]
        x = values["compression_ratio"]
        gap = values["quotient_gap_auc"]["mean"]
        ident = values["id_exact_accuracy"]["mean"]
        ood = values["ood_exact_accuracy"]["mean"]
        axes[0].scatter(x, gap, color=color, s=55)
        axes[0].annotate(group, (x, gap), xytext=(4, 4), textcoords="offset points", fontsize=8)
        axes[1].scatter(gap, ident, color=color, s=55)
        axes[1].annotate(group, (gap, ident), xytext=(4, 4), textcoords="offset points", fontsize=8)
        axes[2].scatter(gap, ood, color=color, s=55)
        axes[2].annotate(group, (gap, ood), xytext=(4, 4), textcoords="offset points", fontsize=8)
    axes[0].set(xlabel="Abelianization compression |G|/|G/[G,G]|", ylabel="Quotient-gap AUC")
    axes[1].set(xlabel="Quotient-gap AUC", ylabel="Final ID exact accuracy")
    axes[2].set(xlabel="Quotient-gap AUC", ylabel="OOD exact accuracy (depth 8/12)")
    for ax in axes:
        ax.grid(alpha=.25)
    fig.suptitle("ARC-23: quotient-first ordering is inseparable from exact-task difficulty")
    fig.tight_layout()
    fig.savefig(FIGURES / "quotient_gap_controls.png", dpi=180)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8), sharey=True)
    for ax, order in zip(axes, [12, 24]):
        for group in [g for g in group_names if group_summary[g]["order"] == order]:
            selected = [row for row in rows if row["group"] == group]
            steps = [checkpoint["step"] for checkpoint in selected[0]["checkpoints"]]
            exact = np.mean([[c["exact_accuracy"] for c in row["checkpoints"]] for row in selected], axis=0)
            quotient = np.mean([[c["quotient_accuracy"] for c in row["checkpoints"]] for row in selected], axis=0)
            line = ax.plot(steps, exact, label=f"{group} exact")[0]
            if group_summary[group]["compression_ratio"] > 1:
                ax.plot(steps, quotient, linestyle="--", color=line.get_color(), label=f"{group} quotient")
        ax.set_title(f"Group order {order}")
        ax.set_xlabel("Training step")
        ax.grid(alpha=.25)
        ax.legend(fontsize=7, ncol=2)
    axes[0].set_ylabel("ID depth-4 accuracy")
    fig.suptitle("Exact and quotient learning trajectories (mean over five seeds)")
    fig.tight_layout()
    fig.savefig(FIGURES / "learning_trajectories.png", dpi=180)
    plt.close(fig)

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
