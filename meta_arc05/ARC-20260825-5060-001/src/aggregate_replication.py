"""Aggregate the preregistered replication and render its gate."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "experiments" / "replication" / "raw_results.json"
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"


def stat(values: list[float]) -> dict[str, float]:
    array = np.asarray(values)
    return {"mean": float(array.mean()), "sd": float(array.std(ddof=1))}


def main() -> None:
    raw = json.loads(RAW.read_text(encoding="utf-8"))
    RESULTS.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    n_layers = raw["n_layers"]
    middle = [i for i in range(n_layers) if .25 <= i / (n_layers - 1) <= .75]
    boundary = [i for i in range(n_layers) if i / (n_layers - 1) <= .125 or i / (n_layers - 1) >= .875]
    per_seed = []
    for seed in raw["seed_results"]:
        lookup = {item["layer"]: item for item in seed["layers"]}
        middle_agreement = float(np.mean([lookup[i]["top1_agreement"] for i in middle]))
        boundary_agreement = float(np.mean([lookup[i]["top1_agreement"] for i in boundary]))
        middle_excess = float(np.mean([lookup[i]["excess_nll"] for i in middle]))
        boundary_excess = float(np.mean([lookup[i]["excess_nll"] for i in boundary]))
        per_seed.append({
            "seed": seed["seed"], "baseline_nll": seed["baseline_nll"],
            "baseline_perplexity": seed["baseline_perplexity"],
            "scored_tokens": seed["scored_tokens"],
            "middle_agreement": middle_agreement,
            "boundary_agreement": boundary_agreement,
            "agreement_gap_middle_minus_boundary": middle_agreement - boundary_agreement,
            "middle_excess_nll": middle_excess,
            "boundary_excess_nll": boundary_excess,
        })
    competence = (
        raw["total_scored_tokens"] >= raw["config"]["competence_min_tokens"]
        and all(row["baseline_nll"] <= raw["config"]["competence_max_nll"] for row in per_seed)
    )
    gate_parts = {
        "competence": competence,
        "middle_agreement_at_least_0_72_all_seeds": all(row["middle_agreement"] >= .72 for row in per_seed),
        "boundary_at_least_0_03_worse_all_seeds": all(row["agreement_gap_middle_minus_boundary"] >= .03 for row in per_seed),
        "middle_excess_nll_lower_all_seeds": all(row["middle_excess_nll"] < row["boundary_excess_nll"] for row in per_seed),
    }
    gate_parts["replication"] = "PASS" if all(gate_parts.values()) else "FAIL"
    layer_summary = []
    for layer in range(n_layers):
        rows = [seed["layers"][layer] for seed in raw["seed_results"]]
        layer_summary.append({
            "layer": layer,
            "relative_depth": rows[0]["relative_depth"],
            "top1_agreement": stat([row["top1_agreement"] for row in rows]),
            "excess_nll": stat([row["excess_nll"] for row in rows]),
            "kl": stat([row["kl_baseline_to_intervened"] for row in rows]),
        })
    output = {
        "gate": gate_parts, "per_seed": per_seed, "middle_layers": middle,
        "boundary_layers": boundary, "layer_summary": layer_summary,
        "total_scored_tokens": raw["total_scored_tokens"],
        "runtime_seconds": raw["runtime_seconds"],
        "peak_cuda_bytes": raw["peak_cuda_bytes"],
    }
    (RESULTS / "replication_aggregate.json").write_text(json.dumps(output, indent=2), encoding="utf-8")

    x = [item["layer"] for item in layer_summary]
    agreement = [item["top1_agreement"]["mean"] for item in layer_summary]
    agreement_sd = [item["top1_agreement"]["sd"] for item in layer_summary]
    excess = [item["excess_nll"]["mean"] for item in layer_summary]
    excess_sd = [item["excess_nll"]["sd"] for item in layer_summary]
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.5))
    axes[0].errorbar(x, agreement, yerr=agreement_sd, marker="o", capsize=2)
    axes[0].axhline(.72, color="black", linestyle="--", linewidth=1, label="replication threshold")
    axes[0].set(xlabel="Deleted layer", ylabel="Top-1 agreement with intact model", ylim=(0, 1))
    axes[0].legend()
    axes[1].errorbar(x, excess, yerr=excess_sd, marker="o", capsize=2, color="#c65f18")
    axes[1].set(xlabel="Deleted layer", ylabel="Excess next-token NLL")
    for ax in axes:
        ax.grid(alpha=.25)
    fig.suptitle("Pythia-410M layer deletion on WikiText-2 (mean ± SD, 3 shards)")
    fig.tight_layout()
    fig.savefig(FIGURES / "replication_layer_profile.png", dpi=180)
    plt.close(fig)
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()

