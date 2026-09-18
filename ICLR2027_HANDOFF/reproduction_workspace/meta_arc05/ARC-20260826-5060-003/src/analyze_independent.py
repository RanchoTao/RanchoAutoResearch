"""Frozen analysis for ARC-003 independent pretraining-run validation."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import yaml


ROOT = Path(__file__).resolve().parents[1]
PREVIOUS = ROOT.parent / "ARC-20260825-5060-002"
CONFIG = yaml.safe_load((ROOT / "configs/independent_runs.yaml").read_text(encoding="utf-8"))
EARLY, MID, LATE = 14000, 72000, 143000


def load_previous_module():
    source = PREVIOUS / "src" / "aggregate_stability.py"
    spec = importlib.util.spec_from_file_location("arc002_aggregate", source)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load frozen analysis helpers: {source}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.CONFIG = CONFIG
    module.EARLY = EARLY
    module.LATE = LATE
    return module


BASE = load_previous_module()


def read_run(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    checkpoints = {row["step"]: BASE.checkpoint_summary(row) for row in payload["checkpoints"]}
    return {
        "path": str(path),
        "scale": payload["scale_m"],
        "run_id": payload["training_run_id"],
        "model": payload["model"],
        "checkpoints": checkpoints,
        "runtime_seconds": sum(row["runtime_seconds"] for row in payload["checkpoints"]),
        "peak_cuda_bytes": max((row["peak_cuda_bytes"] for row in payload["checkpoints"]), default=0),
    }


def load_runs(include_heldout: bool) -> list[dict]:
    paths = []
    for scale in (70, 160):
        for run_id in range(1, 6):
            paths.append(PREVIOUS / "experiments" / "raw" / f"pythia-{scale}m-seed{run_id}.json")
    upper = 9 if include_heldout else 8
    for run_id in range(6, upper + 1):
        paths.append(ROOT / "experiments" / "raw" / f"pythia-160m-seed{run_id}.json")
    missing = [str(path) for path in paths if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing preregistered raw files:\n" + "\n".join(missing))
    runs = [read_run(path) for path in paths]
    for run in runs:
        missing_steps = sorted(set(CONFIG["checkpoint_steps"]) - set(run["checkpoints"]))
        if missing_steps:
            raise ValueError(f"{run['model']} missing steps {missing_steps}")
    return runs


def run_level_ci(values: list[float], seed: int = 20260826, samples: int = 100000) -> list[float]:
    rng = np.random.default_rng(seed)
    array = np.asarray(values, dtype=float)
    draws = rng.choice(array, size=(samples, len(array)), replace=True).mean(axis=1)
    return [float(value) for value in np.quantile(draws, [0.025, 0.975])]


def shard_ci(values: list[float], run_id: int, samples: int = 20000) -> list[float]:
    rng = np.random.default_rng(20260826 + run_id)
    array = np.asarray(values, dtype=float)
    draws = rng.choice(array, size=(samples, len(array)), replace=True).mean(axis=1)
    return [float(value) for value in np.quantile(draws, [0.025, 0.975])]


def checkpoint_value(run: dict, step: int, metric: str) -> float:
    return float(run["checkpoints"][step][metric])


def layer_endpoint_rows(runs: list[dict], scale: int = 160) -> list[dict]:
    rows = []
    for run in sorted((item for item in runs if item["scale"] == scale), key=lambda item: item["run_id"]):
        early = run["checkpoints"][EARLY]["raw"]
        late = run["checkpoints"][LATE]["raw"]
        for layer in early["candidate_layers"]:
            def value(checkpoint):
                return float(np.mean([
                    row["top1_agreement"]
                    for seed in checkpoint["seed_results"]
                    for row in seed["layers"] if row["layer"] == layer
                ]))
            early_value, late_value = value(early), value(late)
            rows.append({
                "run_id": run["run_id"], "layer": layer,
                "relative_depth": layer / (early["n_layers"] - 1),
                "early": early_value, "late": late_value,
                "delta": late_value - early_value,
            })
    return rows


def layer_robustness(rows: list[dict]) -> dict:
    negative_fraction = float(np.mean([row["delta"] < 0 for row in rows]))
    layers = sorted({row["layer"] for row in rows})
    layer_medians = [{
        "layer": layer,
        "median_delta": float(np.median([row["delta"] for row in rows if row["layer"] == layer])),
    } for layer in layers]
    negative_layer_fraction = float(np.mean([row["median_delta"] < 0 for row in layer_medians]))
    return {
        "run_layer_negative_fraction": negative_fraction,
        "layers_with_negative_median_fraction": negative_layer_fraction,
        "layer_medians": layer_medians,
        "pass": negative_fraction >= 0.70 and negative_layer_fraction >= 0.70,
    }


def build_summary(runs: list[dict], include_heldout: bool) -> dict:
    primary = BASE.analyze_scale(runs, 160)
    secondary = BASE.analyze_scale(runs, 70)
    deltas = [row["delta_agreement"] for row in primary["individual_runs"]]
    primary["bootstrap_95_ci_mean_delta"] = run_level_ci(deltas)
    for row in primary["individual_runs"]:
        row["diagnostic_shard_bootstrap_95_ci"] = shard_ci(row["eval_deltas"], row["run_id"])
    layers = layer_endpoint_rows(runs)
    robustness = layer_robustness(layers)
    ci_excludes_zero = primary["bootstrap_95_ci_mean_delta"][1] < 0
    gates = {
        "at_least_eight_runs": primary["eligible_runs"] >= 8,
        "direction_80_percent": primary["negative_runs"] / primary["eligible_runs"] >= 0.8,
        "median_at_most_minus_005": primary["median_delta_agreement"] <= -0.05,
        "run_bootstrap_excludes_zero": ci_excludes_zero,
        "leave_one_out_sign": all(value < 0 for value in primary["leave_one_out_medians"]),
        "resampling_stability": sum(row["eval_negative_count"] >= 2 for row in primary["individual_runs"]) / primary["eligible_runs"] >= 0.8,
        "nll_damage_direction": primary["positive_nll_damage_runs"] / primary["eligible_runs"] >= 0.8,
        "kl_direction": primary["positive_kl_runs"] / primary["eligible_runs"] >= 0.8,
        "confidence": primary["criteria"]["confidence"],
    }
    primary_pass = all(gates.values())
    heldout = next((row for row in primary["individual_runs"] if row["run_id"] == 9), None)
    second_scale_support = secondary["scale_pass"] and secondary["negative_runs"] == secondary["eligible_runs"]
    verdict = "DISCOVERY-ONLY"
    if include_heldout:
        if not gates["confidence"] and gates["direction_80_percent"]:
            verdict = "KILL-CONFOUND"
        elif not gates["direction_80_percent"] or not gates["leave_one_out_sign"]:
            verdict = "KILL-STABILITY"
        elif primary_pass and heldout and heldout["delta_agreement"] < 0 and robustness["pass"] and second_scale_support:
            verdict = "PROMOTE-FULL"
        elif primary_pass or (gates["direction_80_percent"] and gates["run_bootstrap_excludes_zero"]):
            verdict = "PROMOTE-WEAK"
        else:
            verdict = "KILL-STABILITY"
    return {
        "arc": "ARC-20260826-5060-003",
        "mode": "final" if include_heldout else "discovery",
        "primary": primary,
        "primary_gates": gates,
        "primary_pass": primary_pass,
        "heldout": heldout,
        "layer_location_robustness": robustness,
        "layer_endpoint_rows": layers,
        "second_scale": secondary,
        "second_scale_support": second_scale_support,
        "verdict": verdict,
        "new_runtime_seconds": sum(run["runtime_seconds"] for run in runs if run["scale"] == 160 and run["run_id"] >= 6),
        "new_peak_cuda_bytes": max((run["peak_cuda_bytes"] for run in runs if run["scale"] == 160 and run["run_id"] >= 6), default=0),
    }


def write_tables(runs: list[dict], summary: dict) -> None:
    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    with (out / "run_level_results.csv").open("w", newline="", encoding="utf-8") as handle:
        fields = ["run", "early_s", "mid_s", "late_s", "delta_late_early", "direction", "nll_delta", "kl_delta", "spearman"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        run_map = {run["run_id"]: run for run in runs if run["scale"] == 160}
        detail_map = {row["run_id"]: row for row in summary["primary"]["individual_runs"]}
        for run_id in sorted(run_map):
            run, detail = run_map[run_id], detail_map[run_id]
            writer.writerow({
                "run": run_id,
                "early_s": checkpoint_value(run, EARLY, "agreement"),
                "mid_s": checkpoint_value(run, MID, "agreement"),
                "late_s": checkpoint_value(run, LATE, "agreement"),
                "delta_late_early": detail["delta_agreement"],
                "direction": "negative" if detail["delta_agreement"] < 0 else "positive",
                "nll_delta": detail["delta_nll_damage"],
                "kl_delta": detail["delta_kl"],
                "spearman": detail["spearman_progress_agreement"],
            })
    with (out / "checkpoint_metrics.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["scale_m", "run", "step", "progress", "intact_nll", "agreement", "nll_damage", "kl"])
        for run in sorted(runs, key=lambda item: (item["scale"], item["run_id"])):
            for step, row in sorted(run["checkpoints"].items()):
                writer.writerow([run["scale"], run["run_id"], step, row["progress"], row["baseline_nll"], row["agreement"], row["nll_damage"], row["kl"]])
    with (out / "layer_endpoint_deltas.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["run_id", "layer", "relative_depth", "early", "late", "delta"])
        writer.writeheader(); writer.writerows(summary["layer_endpoint_rows"])


def plot_final(runs: list[dict], summary: dict) -> None:
    out = ROOT / "figures"; out.mkdir(exist_ok=True)
    primary_runs = sorted((run for run in runs if run["scale"] == 160), key=lambda run: run["run_id"])
    colors = plt.cm.tab10(np.linspace(0, 1, 10))

    fig, axis = plt.subplots(figsize=(9, 5))
    for run in primary_runs:
        rows = [run["checkpoints"][step] for step in CONFIG["checkpoint_steps"]]
        axis.plot([row["progress"] for row in rows], [row["agreement"] for row in rows], marker="o", color=colors[run["run_id"] - 1], linestyle="--" if run["run_id"] == 9 else "-", label=f"seed{run['run_id']}" + (" held out" if run["run_id"] == 9 else ""))
    axis.set(xlabel="Normalized training progress", ylabel="Middle-layer top-1 substitutability", title="Independent PolyPythias-160M trajectories")
    axis.grid(alpha=.25); axis.legend(ncol=3, fontsize=8); fig.tight_layout(); fig.savefig(out / "fig1_independent_trajectories.png", dpi=200); plt.close(fig)

    details = summary["primary"]["individual_runs"]
    fig, axis = plt.subplots(figsize=(8, 4.5))
    values = [row["delta_agreement"] for row in details]
    bars = axis.bar([row["run_id"] for row in details], values, color=[colors[row["run_id"] - 1] for row in details])
    axis.axhline(0, color="black", lw=1); axis.axhline(-.05, color="firebrick", ls="--", lw=1, label="frozen magnitude gate")
    axis.set(xlabel="Independent pretraining run", ylabel="Late - early substitutability", title="Run-level endpoint contrasts"); axis.legend(); fig.tight_layout(); fig.savefig(out / "fig2_late_minus_early_distribution.png", dpi=200); plt.close(fig)

    fig, axis = plt.subplots(figsize=(8, 5))
    y = np.arange(len(details)); point = np.asarray(values)
    low = point - np.asarray([row["diagnostic_shard_bootstrap_95_ci"][0] for row in details]); high = np.asarray([row["diagnostic_shard_bootstrap_95_ci"][1] for row in details]) - point
    axis.errorbar(point, y, xerr=np.vstack([low, high]), fmt="o", capsize=3)
    axis.axvline(0, color="black", lw=1); axis.set(yticks=y, yticklabels=[f"seed{row['run_id']}" for row in details], xlabel="Late - early substitutability", title="Run-level effects (diagnostic shard-bootstrap 95% CIs)"); fig.tight_layout(); fig.savefig(out / "fig3_run_level_forest.png", dpi=200); plt.close(fig)

    comparisons = summary["primary"]["confidence_bin_comparisons"]
    indices = sorted({row["bin_index"] for row in comparisons})
    early = [BASE.mean(row["early_agreement"] for row in comparisons if row["bin_index"] == index) for index in indices]
    late = [BASE.mean(row["late_agreement"] for row in comparisons if row["bin_index"] == index) for index in indices]
    labels = [f"{CONFIG['confidence_bins'][i]:.2g}-{CONFIG['confidence_bins'][i+1]:.2g}" for i in indices]
    x = np.arange(len(indices)); fig, axis = plt.subplots(figsize=(8, 4.5)); axis.bar(x-.18, early, .36, label="early"); axis.bar(x+.18, late, .36, label="late"); axis.set(xticks=x, xticklabels=labels, xlabel="Intact confidence bin", ylabel="Substitutability", title="Fixed-bin confidence control"); axis.legend(); fig.tight_layout(); fig.savefig(out / "fig4_confidence_matched.png", dpi=200); plt.close(fig)

    layers = primary_runs[0]["checkpoints"][EARLY]["raw"]["candidate_layers"]
    matrix = []
    for layer in layers:
        row = []
        for step in CONFIG["checkpoint_steps"]:
            row.append(float(np.mean([
                layer_row["top1_agreement"]
                for run in primary_runs
                for seed in run["checkpoints"][step]["raw"]["seed_results"]
                for layer_row in seed["layers"] if layer_row["layer"] == layer
            ])))
        matrix.append(row)
    fig, axis = plt.subplots(figsize=(8, 5)); image = axis.imshow(np.asarray(matrix), aspect="auto", origin="lower", cmap="viridis"); axis.set(xticks=range(5), xticklabels=["14k", "36k", "72k", "107k", "143k"], yticks=range(len(layers)), yticklabels=layers, xlabel="Training checkpoint", ylabel="Deleted layer", title="Layer x progress substitutability"); fig.colorbar(image, ax=axis, label="Top-1 agreement"); fig.tight_layout(); fig.savefig(out / "fig5_layer_progress_heatmap.png", dpi=200); plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    for axis, metric, label in zip(axes, ["nll_damage", "kl"], ["Deleted - intact NLL", "KL(intact || deleted)"]):
        for run in primary_runs:
            rows = [run["checkpoints"][step] for step in CONFIG["checkpoint_steps"]]
            axis.plot([row["progress"] for row in rows], [row[metric] for row in rows], marker="o", alpha=.8, label=f"seed{run['run_id']}")
        axis.set(xlabel="Normalized training progress", ylabel=label, title=label); axis.grid(alpha=.25)
    axes[1].legend(ncol=3, fontsize=7); fig.tight_layout(); fig.savefig(out / "fig6_functional_metrics.png", dpi=200); plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["discovery", "final"], required=True)
    args = parser.parse_args()
    include_heldout = args.mode == "final"
    runs = load_runs(include_heldout)
    summary = build_summary(runs, include_heldout)
    results = ROOT / "results"; results.mkdir(exist_ok=True)
    target = results / ("independent_run_summary.json" if include_heldout else "discovery_summary.json")
    target.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    if include_heldout:
        write_tables(runs, summary)
        plot_final(runs, summary)
    print(json.dumps({
        "mode": summary["mode"], "runs": summary["primary"]["eligible_runs"],
        "negative": summary["primary"]["negative_runs"],
        "median_delta": summary["primary"]["median_delta_agreement"],
        "ci": summary["primary"]["bootstrap_95_ci_mean_delta"],
        "verdict": summary["verdict"],
    }, indent=2))


if __name__ == "__main__":
    main()

