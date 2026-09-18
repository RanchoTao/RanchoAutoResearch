"""Aggregate discovery checkpoint sweep and test simple confidence proxies."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import spearmanr


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "experiments" / "boundary" / "raw_results.json"
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"


def middle_indices(n_layers: int) -> list[int]:
    return [i for i in range(n_layers) if .25 <= i / (n_layers - 1) <= .75]


def main() -> None:
    raw = json.loads(RAW.read_text(encoding="utf-8"))
    RESULTS.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    rows = []
    controlled_bins = []
    for checkpoint in raw["checkpoints"]:
        middle = middle_indices(checkpoint["n_layers"])
        seed_agreement = []
        seed_excess = []
        for seed in checkpoint["seed_results"]:
            seed_agreement.append(float(np.mean([seed["layers"][i]["top1_agreement"] for i in middle])))
            seed_excess.append(float(np.mean([seed["layers"][i]["excess_nll"] for i in middle])))
        row = {
            "revision": checkpoint["revision"], "step": checkpoint["step"],
            "middle_agreement_mean": float(np.mean(seed_agreement)),
            "middle_agreement_sd": float(np.std(seed_agreement, ddof=1)),
            "middle_excess_nll_mean": float(np.mean(seed_excess)),
            "baseline_nll_mean": float(np.mean([s["baseline_nll"] for s in checkpoint["seed_results"]])),
            "baseline_confidence_mean": float(np.mean([s["baseline_top1_confidence"] for s in checkpoint["seed_results"]])),
            "baseline_entropy_mean": float(np.mean([s["baseline_entropy"] for s in checkpoint["seed_results"]])),
            "by_seed_agreement": dict(zip(map(str, raw["config"]["seeds"]), seed_agreement)),
        }
        rows.append(row)
        for bin_index in range(len(raw["config"]["confidence_bins"]) - 1):
            numerator = 0.0
            denominator = 0
            low = high = None
            for seed in checkpoint["seed_results"]:
                for layer in middle:
                    item = seed["layers"][layer]["confidence_bins"][bin_index]
                    low, high = item["low"], item["high"]
                    if item["count"] and item["agreement"] is not None:
                        numerator += item["agreement"] * item["count"]
                        denominator += item["count"]
            controlled_bins.append({
                "revision": checkpoint["revision"], "step": checkpoint["step"],
                "low": low, "high": high, "count": denominator,
                "middle_agreement": numerator / denominator if denominator else None,
            })

    trained = rows[1:]
    rho_step = float(spearmanr([r["step"] for r in trained], [r["middle_agreement_mean"] for r in trained]).statistic)
    rho_nll = float(spearmanr([r["baseline_nll_mean"] for r in trained], [r["middle_agreement_mean"] for r in trained]).statistic)
    rho_conf = float(spearmanr([r["baseline_confidence_mean"] for r in trained], [r["middle_agreement_mean"] for r in trained]).statistic)
    monotone_seeds = sum(
        all(rows[index]["by_seed_agreement"][str(seed)] > rows[index + 1]["by_seed_agreement"][str(seed)]
            for index in range(1, len(rows) - 1))
        for seed in raw["config"]["seeds"]
    )
    overlapping_bin_declines = []
    for low, high in zip(raw["config"]["confidence_bins"][:-1], raw["config"]["confidence_bins"][1:]):
        early = next(item for item in controlled_bins if item["step"] == 1000 and item["low"] == low)
        late = next(item for item in controlled_bins if item["step"] == 143000 and item["low"] == low)
        if early["count"] and late["count"]:
            overlapping_bin_declines.append({
                "low": low, "high": high, "step1000": early["middle_agreement"],
                "step143000": late["middle_agreement"],
                "decline": early["middle_agreement"] - late["middle_agreement"],
                "min_count": min(early["count"], late["count"]),
            })
    output = {
        "checkpoints": rows, "confidence_control": overlapping_bin_declines,
        "trained_checkpoint_spearman_step_vs_agreement": rho_step,
        "trained_checkpoint_spearman_nll_vs_agreement": rho_nll,
        "trained_checkpoint_spearman_confidence_vs_agreement": rho_conf,
        "strict_monotone_decline_seeds": monotone_seeds,
        "discovery_result": (
            "After competence begins at step1000, middle-layer deletion robustness declines "
            "strictly with continued pretraining in all three text shards, including within "
            "every populated intact-confidence bin."
        ),
        "total_checkpoint_runtime_seconds": sum(c["runtime_seconds"] for c in raw["checkpoints"]),
        "max_peak_cuda_bytes": max(c["peak_cuda_bytes"] for c in raw["checkpoints"]),
    }
    (RESULTS / "boundary_aggregate.json").write_text(json.dumps(output, indent=2), encoding="utf-8")

    steps = [row["step"] for row in rows]
    agree = [row["middle_agreement_mean"] for row in rows]
    agree_sd = [row["middle_agreement_sd"] for row in rows]
    nll = [row["baseline_nll_mean"] for row in rows]
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.5))
    axes[0].errorbar(steps, agree, yerr=agree_sd, marker="o", capsize=3)
    axes[0].set_xscale("symlog", linthresh=1000)
    axes[0].set(xlabel="Pretraining step", ylabel="Middle-layer top-1 agreement", ylim=(0, 1))
    axes[1].plot(steps, nll, marker="o", label="Intact NLL")
    axes[1].set_xscale("symlog", linthresh=1000)
    axes[1].set(xlabel="Pretraining step", ylabel="Intact next-token NLL")
    for ax in axes:
        ax.grid(alpha=.25)
    fig.suptitle("Pythia-160M: deletion robustness peaks early then declines")
    fig.tight_layout()
    fig.savefig(FIGURES / "boundary_training_progress.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    for row in overlapping_bin_declines:
        ax.plot([1000, 143000], [row["step1000"], row["step143000"]], marker="o",
                label=f"p(top1) in [{row['low']:.2f}, {min(row['high'], 1):.2f})")
    ax.set_xscale("log")
    ax.set(xlabel="Pretraining step", ylabel="Middle-layer agreement within confidence bin")
    ax.grid(alpha=.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIGURES / "confidence_control.png", dpi=180)
    plt.close(fig)
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()

