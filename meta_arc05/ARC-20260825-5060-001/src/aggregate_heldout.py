"""Apply the preregistered held-out Pythia-70M prediction gate."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "experiments" / "heldout" / "raw_results.json"
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"


def main() -> None:
    raw = json.loads(RAW.read_text(encoding="utf-8"))
    RESULTS.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    checkpoint_rows = []
    for checkpoint in raw["checkpoints"]:
        middle = [i for i in range(checkpoint["n_layers"]) if .25 <= i / (checkpoint["n_layers"] - 1) <= .75]
        by_seed = {}
        for seed in checkpoint["seed_results"]:
            by_seed[str(seed["seed"])] = float(np.mean([
                seed["layers"][i]["top1_agreement"] for i in middle
            ]))
        checkpoint_rows.append({
            "revision": checkpoint["revision"], "step": checkpoint["step"],
            "middle_layers": middle, "by_seed_agreement": by_seed,
            "mean_agreement": float(np.mean(list(by_seed.values()))),
            "sd_agreement": float(np.std(list(by_seed.values()), ddof=1)),
            "mean_excess_nll": float(np.mean([
                np.mean([seed["layers"][i]["excess_nll"] for i in middle])
                for seed in checkpoint["seed_results"]
            ])),
            "baseline_nll_by_seed": {str(seed["seed"]): seed["baseline_nll"] for seed in checkpoint["seed_results"]},
        })
    early, late = checkpoint_rows
    declines = {
        seed: early["by_seed_agreement"][seed] - late["by_seed_agreement"][seed]
        for seed in early["by_seed_agreement"]
    }
    bins = []
    for bin_index in range(len(raw["config"]["confidence_bins"]) - 1):
        values = []
        for checkpoint in raw["checkpoints"]:
            middle = [i for i in range(checkpoint["n_layers"]) if .25 <= i / (checkpoint["n_layers"] - 1) <= .75]
            num = 0.0
            den = 0
            low = high = None
            for seed in checkpoint["seed_results"]:
                for layer in middle:
                    item = seed["layers"][layer]["confidence_bins"][bin_index]
                    low, high = item["low"], item["high"]
                    if item["count"]:
                        num += item["agreement"] * item["count"]
                        den += item["count"]
            values.append({"agreement": num / den if den else None, "count": den})
        bins.append({
            "low": low, "high": high, "step1000": values[0], "step143000": values[1],
            "decline": values[0]["agreement"] - values[1]["agreement"] if values[0]["count"] and values[1]["count"] else None,
        })
    qualified_bins = [
        row for row in bins
        if min(row["step1000"]["count"], row["step143000"]["count"]) >= 100
        and row["decline"] is not None and row["decline"] > 0
    ]
    competence = all(value <= 4.5 for value in late["baseline_nll_by_seed"].values())
    gate = {
        "final_competence": competence,
        "decline_at_least_0_05_all_seeds": all(value >= .05 for value in declines.values()),
        "at_least_three_confidence_bins_decline": len(qualified_bins) >= 3,
    }
    gate["heldout_prediction"] = "PASS" if all(gate.values()) else "FAIL"
    output = {
        "checkpoints": checkpoint_rows, "decline_by_seed": declines,
        "confidence_bins": bins, "qualified_declining_bins": len(qualified_bins),
        "gate": gate,
        "total_runtime_seconds": sum(c["runtime_seconds"] for c in raw["checkpoints"]),
        "max_peak_cuda_bytes": max(c["peak_cuda_bytes"] for c in raw["checkpoints"]),
    }
    (RESULTS / "heldout_aggregate.json").write_text(json.dumps(output, indent=2), encoding="utf-8")

    fig, ax = plt.subplots(figsize=(7, 4.6))
    seeds = sorted(declines, key=int)
    for seed in seeds:
        ax.plot([1000, 143000], [early["by_seed_agreement"][seed], late["by_seed_agreement"][seed]],
                marker="o", label=f"shard {seed}")
    ax.set_xscale("log")
    ax.set(xlabel="Pretraining step", ylabel="Middle-layer top-1 agreement", ylim=(0, .55))
    ax.grid(alpha=.25)
    ax.legend()
    ax.set_title("Held-out Pythia-70M: continued pretraining reduces deletion robustness")
    fig.tight_layout()
    fig.savefig(FIGURES / "heldout_prediction.png", dpi=180)
    plt.close(fig)
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()

