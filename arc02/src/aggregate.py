from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from analysis import jaccard


ROOT = Path(__file__).resolve().parent.parent
RUNS = ["mvp_seed11", "rep_seed23", "rep_seed37"]
METHODS = ["activation_patching", "zero_ablation"]
DEPTHS = np.arange(1, 6, dtype=float)


def criteria(y: np.ndarray, prediction: np.ndarray, k: int) -> dict[str, float]:
    n = len(y)
    rss = max(float(np.square(y - prediction).sum()), 1e-12)
    return {
        "rss": rss,
        "aic": float(n * math.log(rss / n) + 2 * k),
        "bic": float(n * math.log(rss / n) + k * math.log(n)),
    }


def fit_seed_adjusted(values: np.ndarray) -> dict:
    # 15 observations. Seed fixed effects absorb between-training-run offsets;
    # shape parameters must therefore be supported within seeds.
    y = values.reshape(-1)
    depth = np.tile(DEPTHS, values.shape[0])
    seed_ids = np.repeat(np.arange(values.shape[0]), len(DEPTHS))
    seed_dummies = np.column_stack([(seed_ids == i).astype(float) for i in range(1, values.shape[0])])
    base = np.column_stack([np.ones_like(depth), seed_dummies])
    output = {}
    designs = {
        "linear": (np.column_stack([base, depth]), 4),
        "quadratic": (np.column_stack([base, depth, depth ** 2]), 5),
    }
    for name, (design, k) in designs.items():
        coefficient, *_ = np.linalg.lstsq(design, y, rcond=None)
        output[name] = {"coefficients": coefficient.tolist(), **criteria(y, design @ coefficient, k)}
    candidates = []
    for breakpoint in (2.0, 3.0, 4.0):
        design = np.column_stack([base, depth, np.maximum(0.0, depth - breakpoint)])
        coefficient, *_ = np.linalg.lstsq(design, y, rcond=None)
        prediction = design @ coefficient
        candidates.append((float(np.square(y - prediction).sum()), breakpoint, coefficient, prediction))
    _, breakpoint, coefficient, prediction = min(candidates, key=lambda item: item[0])
    output["piecewise"] = {
        "breakpoint": breakpoint, "coefficients": coefficient.tolist(),
        **criteria(y, prediction, 6),  # seed effects, slopes, and selected breakpoint
    }
    return output


def selected_set(run: dict, depth: int, method: str) -> set[str]:
    return set(run["circuits"][str(depth)]["methods"][method]["selected"])


def main() -> None:
    runs = [json.loads((ROOT / "experiments" / name / "results.json").read_text(encoding="utf-8"))
            for name in RUNS]
    output = {"runs": RUNS, "n_seeds": len(runs), "methods": {}}
    table_rows = []
    for method in METHODS:
        sizes = np.asarray([
            [run["circuits"][str(depth)]["methods"][method]["size"] for depth in range(1, 6)]
            for run in runs
        ], dtype=float)
        mean = sizes.mean(axis=0)
        sd = sizes.std(axis=0, ddof=1)
        half_width = 4.3026527299 * sd / math.sqrt(len(runs))  # t(2), 95%
        adjacent = np.asarray([
            [jaccard(selected_set(run, depth, method), selected_set(run, depth + 1, method))
             for depth in range(1, 5)] for run in runs
        ])
        method_jaccard = np.asarray([
            [run["circuits"][str(depth)]["method_jaccard"] for depth in range(1, 6)]
            for run in runs
        ])
        phase = fit_seed_adjusted(sizes)
        layer_fraction = np.zeros((len(runs), 5, 10), dtype=float)
        retained = np.zeros((len(runs), 5), dtype=float)
        ablated = np.zeros((len(runs), 5), dtype=float)
        random_retained = np.zeros((len(runs), 5), dtype=float)
        random_ablated = np.zeros((len(runs), 5), dtype=float)
        for run_index, run in enumerate(runs):
            for depth_index, depth in enumerate(range(1, 6)):
                record = run["circuits"][str(depth)]["methods"][method]
                for component in record["selected"]:
                    layer = int(component.split("H")[0].split("MLP")[0][1:])
                    layer_fraction[run_index, depth_index, layer] += 1.0 / record["size"]
                retained[run_index, depth_index] = record["retained_accuracy"]
                ablated[run_index, depth_index] = record["circuit_ablated_accuracy"]
                random_retained[run_index, depth_index] = record["random_retain_accuracy_mean"]
                random_ablated[run_index, depth_index] = record["random_ablate_accuracy_mean"]
        mean_layers = layer_fraction.mean(axis=0)
        entropy = -np.sum(np.where(mean_layers > 0, mean_layers * np.log(mean_layers), 0.0), axis=1) / np.log(10)
        centroid = (mean_layers * np.arange(10)[None, :]).sum(axis=1)
        output["methods"][method] = {
            "sizes_by_seed": sizes.tolist(), "mean_size": mean.tolist(), "sd_size": sd.tolist(),
            "ci95_low": (mean - half_width).tolist(), "ci95_high": (mean + half_width).tolist(),
            "adjacent_jaccard_by_seed": adjacent.tolist(),
            "adjacent_jaccard_mean": adjacent.mean(axis=0).tolist(),
            "phase_models_seed_adjusted": phase,
            "layer_fraction_mean": mean_layers.tolist(),
            "normalized_layer_entropy": entropy.tolist(),
            "layer_centroid": centroid.tolist(),
            "retained_accuracy_mean": retained.mean(axis=0).tolist(),
            "circuit_ablated_accuracy_mean": ablated.mean(axis=0).tolist(),
            "random_retain_accuracy_mean": random_retained.mean(axis=0).tolist(),
            "random_ablate_accuracy_mean": random_ablated.mean(axis=0).tolist(),
        }
        for index, depth in enumerate(range(1, 6)):
            table_rows.append({
                "method": method, "depth": depth, "mean_size": mean[index], "sd_size": sd[index],
                "ci95_low": mean[index] - half_width[index],
                "ci95_high": mean[index] + half_width[index],
                "mean_sparsity": 1.0 - mean[index] / 50.0,
                "mean_cross_method_jaccard": method_jaccard[:, index].mean(),
            })
    accuracies = np.asarray([
        [float(run["training"]["accuracy_by_depth"][str(depth)]) for depth in range(1, 6)]
        for run in runs
    ])
    output["accuracy"] = {
        "by_seed": accuracies.tolist(), "mean": accuracies.mean(axis=0).tolist(),
        "minimum": float(accuracies.min()),
    }
    output["runtime"] = {
        "seconds_by_seed": [run["total_runtime_seconds"] for run in runs],
        "total_seconds": float(sum(run["total_runtime_seconds"] for run in runs)),
        "peak_gpu_memory_bytes_max": int(max(run["torch_cuda_max_memory_bytes"] for run in runs)),
    }
    cka = np.asarray([
        list(run["representation"]["adjacent_cka_by_layer"].values()) for run in runs
    ], dtype=float)
    output["representation"] = {
        "adjacent_cka_mean": cka.mean(axis=0).tolist(),
        "adjacent_cka_sd": cka.std(axis=0, ddof=1).tolist(),
    }
    results_dir = ROOT / "results"
    results_dir.mkdir(exist_ok=True)
    (results_dir / "aggregate_results.json").write_text(json.dumps(output, indent=2), encoding="utf-8")
    with (results_dir / "aggregate_circuit_size.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(table_rows[0]))
        writer.writeheader()
        writer.writerows(table_rows)

    figures = ROOT / "figures"
    figures.mkdir(exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
    for axis, method in zip(axes, METHODS):
        values = np.asarray(output["methods"][method]["sizes_by_seed"])
        for row, seed_name in zip(values, RUNS):
            axis.plot(DEPTHS, row, color="0.65", alpha=0.75, marker="o", linewidth=1,
                      label=seed_name if axis is axes[0] else None)
        mean = values.mean(axis=0)
        sd = values.std(axis=0, ddof=1)
        axis.errorbar(DEPTHS, mean, yerr=sd, color="#b2182b", marker="o", linewidth=2,
                      capsize=3, label="mean ± SD")
        axis.set(title=method.replace("_", " ").title(), xlabel="Reasoning depth", xticks=DEPTHS)
    axes[0].set_ylabel("90%-fidelity circuit size / 50 components")
    axes[0].legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(figures / "aggregate_circuit_size_3seeds.png", dpi=200)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
    for axis, method in zip(axes, METHODS):
        values = np.asarray(output["methods"][method]["adjacent_jaccard_by_seed"])
        for row in values:
            axis.plot(DEPTHS[1:], row, color="0.65", alpha=0.75, marker="o", linewidth=1)
        axis.errorbar(DEPTHS[1:], values.mean(axis=0), yerr=values.std(axis=0, ddof=1),
                      color="#2166ac", marker="o", linewidth=2, capsize=3)
        axis.set(title=method.replace("_", " ").title(), xlabel="Deeper depth in adjacent pair",
                 xticks=DEPTHS[1:], ylim=(0, 1.02))
    axes[0].set_ylabel("Adjacent circuit Jaccard")
    fig.tight_layout()
    fig.savefig(figures / "aggregate_adjacent_overlap_3seeds.png", dpi=200)
    plt.close(fig)

    layers = np.asarray(output["methods"]["zero_ablation"]["layer_fraction_mean"]).T
    fig, ax = plt.subplots(figsize=(6, 4))
    image = ax.imshow(layers, origin="lower", aspect="auto", cmap="viridis")
    ax.set(xlabel="Reasoning depth", ylabel="Transformer layer",
           xticks=range(5), xticklabels=range(1, 6), yticks=range(10))
    fig.colorbar(image, ax=ax, label="Mean fraction of ablation-defined circuit")
    fig.tight_layout()
    fig.savefig(figures / "aggregate_layer_depth_heatmap_3seeds.png", dpi=200)
    plt.close(fig)

    record = output["methods"]["zero_ablation"]
    fig, ax = plt.subplots(figsize=(7, 4))
    width = 0.2
    positions = np.arange(5)
    series = [
        (np.asarray(output["accuracy"]["mean"]), "Full validation"),
        (np.asarray(record["retained_accuracy_mean"]), "Retained circuit"),
        (np.asarray(record["circuit_ablated_accuracy_mean"]), "Circuit ablated"),
        (np.asarray(record["random_ablate_accuracy_mean"]), "Random ablation"),
    ]
    for index, (values, label) in enumerate(series):
        ax.bar(positions + (index - 1.5) * width, values, width, label=label)
    ax.set(xlabel="Reasoning depth", ylabel="Mean accuracy", xticks=positions,
           xticklabels=range(1, 6), ylim=(0, 1.05))
    ax.legend(frameon=False, ncol=2)
    fig.tight_layout()
    fig.savefig(figures / "aggregate_causal_performance_3seeds.png", dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    main()
