"""Aggregate preregistered PolyPythias stability runs and render diagnostics."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import yaml


ROOT = Path(__file__).resolve().parents[1]
CONFIG = yaml.safe_load((ROOT / "configs/stability.yaml").read_text(encoding="utf-8"))
EARLY = CONFIG["checkpoint_steps"][0]
LATE = CONFIG["checkpoint_steps"][-1]


def mean(values):
    values = list(values)
    return float(np.mean(values)) if values else None


def checkpoint_summary(checkpoint: dict) -> dict:
    eval_rows = []
    for seed in checkpoint["seed_results"]:
        eval_rows.append({
            "evaluation_seed": seed["evaluation_seed"],
            "baseline_nll": seed["baseline_nll"],
            "confidence": seed["baseline_top1_confidence"],
            "agreement": mean(row["top1_agreement"] for row in seed["layers"]),
            "nll_damage": mean(row["nll_damage"] for row in seed["layers"]),
            "kl": mean(row["kl"] for row in seed["layers"]),
        })
    return {
        "step": checkpoint["step"],
        "progress": checkpoint["normalized_progress"],
        "baseline_nll": mean(row["baseline_nll"] for row in eval_rows),
        "confidence": mean(row["confidence"] for row in eval_rows),
        "agreement": mean(row["agreement"] for row in eval_rows),
        "nll_damage": mean(row["nll_damage"] for row in eval_rows),
        "kl": mean(row["kl"] for row in eval_rows),
        "eval_rows": eval_rows,
        "raw": checkpoint,
    }


def load_runs() -> list[dict]:
    runs = []
    for path in sorted((ROOT / CONFIG["output_dir"]).glob("pythia-*-seed*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        checkpoints = {row["step"]: checkpoint_summary(row) for row in payload["checkpoints"]}
        runs.append({
            "path": str(path), "scale": payload["scale_m"],
            "run_id": payload["training_run_id"], "model": payload["model"],
            "checkpoints": checkpoints,
            "runtime_seconds": sum(row["runtime_seconds"] for row in payload["checkpoints"]),
            "peak_cuda_bytes": max((row["peak_cuda_bytes"] for row in payload["checkpoints"]), default=0),
        })
    return runs


def bootstrap_ci(values: list[float], samples: int = 10000) -> list[float] | None:
    if not values:
        return None
    rng = np.random.default_rng(20260825)
    array = np.asarray(values)
    means = np.mean(rng.choice(array, size=(samples, len(array)), replace=True), axis=1)
    return [float(x) for x in np.quantile(means, [0.025, 0.975])]


def rankdata(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values)
    ranks = np.empty(len(values), dtype=float)
    ranks[order] = np.arange(len(values), dtype=float)
    return ranks


def spearman(x, y) -> float:
    return float(np.corrcoef(rankdata(np.asarray(x)), rankdata(np.asarray(y)))[0, 1])


def confidence_bin(checkpoint: dict, bin_index: int) -> tuple[int, float | None]:
    count = 0
    agreed = 0.0
    for seed in checkpoint["raw"]["seed_results"]:
        for layer in seed["layers"]:
            row = layer["confidence_bins"][bin_index]
            if row["agreement"] is not None:
                count += row["count"]
                agreed += row["agreement"] * row["count"]
    return count, (agreed / count if count else None)


def confound_analysis(runs: list[dict], scale: int) -> dict:
    rows = [
        {**checkpoint, "run_id": run["run_id"]}
        for run in runs if run["scale"] == scale
        for checkpoint in run["checkpoints"].values()
    ]
    if len(rows) < 3:
        return {"status": "insufficient"}
    y = np.asarray([row["agreement"] for row in rows])
    nll = np.asarray([row["baseline_nll"] for row in rows])
    progress = np.asarray([row["progress"] for row in rows])
    znll = (nll - nll.mean()) / nll.std()
    zprogress = (progress - progress.mean()) / progress.std()
    design_nll = np.column_stack([np.ones(len(rows)), znll])
    design_full = np.column_stack([np.ones(len(rows)), znll, zprogress])
    fit_nll = np.linalg.lstsq(design_nll, y, rcond=None)[0]
    fit_full = np.linalg.lstsq(design_full, y, rcond=None)[0]
    residual_y = y - design_nll @ fit_nll
    fit_progress_from_nll = np.linalg.lstsq(design_nll, zprogress, rcond=None)[0]
    residual_progress = zprogress - design_nll @ fit_progress_from_nll
    partial = float(np.corrcoef(residual_y, residual_progress)[0, 1])
    sse_nll = float(np.sum((y - design_nll @ fit_nll) ** 2))
    sse_full = float(np.sum((y - design_full @ fit_full) ** 2))

    # Post-sweep robustness check: remove each run's mean before fitting so the
    # progress coefficient cannot be driven by between-run intercept shifts.
    run_ids = np.asarray([row["run_id"] for row in rows])
    centered_y = y.copy()
    centered_nll = nll.copy()
    centered_progress = progress.copy()
    for run_id in np.unique(run_ids):
        mask = run_ids == run_id
        centered_y[mask] -= centered_y[mask].mean()
        centered_nll[mask] -= centered_nll[mask].mean()
        centered_progress[mask] -= centered_progress[mask].mean()
    within_design = np.column_stack([centered_nll, centered_progress])
    within_fit = np.linalg.lstsq(within_design, centered_y, rcond=None)[0]
    within_y_residual = centered_y - centered_nll[:, None] @ np.asarray([within_fit[0]])
    progress_on_nll = np.linalg.lstsq(centered_nll[:, None], centered_progress, rcond=None)[0]
    within_progress_residual = centered_progress - centered_nll * progress_on_nll[0]
    within_partial = float(np.corrcoef(within_y_residual, within_progress_residual)[0, 1])
    return {
        "status": "pass" if fit_full[2] < 0 and partial < 0 and within_fit[1] < 0 and within_partial < 0 else "partial",
        "standardized_progress_coefficient_controlling_nll": float(fit_full[2]),
        "partial_correlation_progress_agreement_given_nll": partial,
        "within_run_progress_coefficient_controlling_nll": float(within_fit[1]),
        "within_run_partial_correlation_progress_agreement_given_nll": within_partial,
        "sse_nll_only": sse_nll,
        "sse_nll_plus_progress": sse_full,
        "observations": len(rows),
    }


def analyze_scale(runs: list[dict], scale: int) -> dict:
    eligible = []
    excluded = []
    for run in sorted((row for row in runs if row["scale"] == scale), key=lambda row: row["run_id"]):
        if EARLY not in run["checkpoints"] or LATE not in run["checkpoints"]:
            excluded.append({"run_id": run["run_id"], "reason": "missing endpoint"})
            continue
        early, late = run["checkpoints"][EARLY], run["checkpoints"][LATE]
        if early["baseline_nll"] > CONFIG["competence_max_nll"] or late["baseline_nll"] > CONFIG["competence_max_nll"]:
            excluded.append({
                "run_id": run["run_id"], "reason": "competence gate",
                "early_nll": early["baseline_nll"], "late_nll": late["baseline_nll"],
            })
            continue
        eval_deltas = []
        early_eval = {row["evaluation_seed"]: row for row in early["eval_rows"]}
        late_eval = {row["evaluation_seed"]: row for row in late["eval_rows"]}
        for evaluation_seed in CONFIG["evaluation_seeds"]:
            eval_deltas.append(late_eval[evaluation_seed]["agreement"] - early_eval[evaluation_seed]["agreement"])
        trajectory = [run["checkpoints"][step]["agreement"] for step in CONFIG["checkpoint_steps"] if step in run["checkpoints"]]
        progress = [run["checkpoints"][step]["progress"] for step in CONFIG["checkpoint_steps"] if step in run["checkpoints"]]
        eligible.append({
            "run_id": run["run_id"],
            "delta_agreement": late["agreement"] - early["agreement"],
            "delta_nll_damage": late["nll_damage"] - early["nll_damage"],
            "delta_kl": late["kl"] - early["kl"],
            "early_nll": early["baseline_nll"], "late_nll": late["baseline_nll"],
            "eval_deltas": eval_deltas,
            "eval_negative_count": sum(value < 0 for value in eval_deltas),
            "spearman_progress_agreement": spearman(progress, trajectory) if len(trajectory) >= 3 else None,
        })
    agreement_deltas = [row["delta_agreement"] for row in eligible]
    nll_deltas = [row["delta_nll_damage"] for row in eligible]
    kl_deltas = [row["delta_kl"] for row in eligible]

    bin_comparisons = []
    pooled_bin_deltas = []
    for run in (row for row in runs if row["scale"] == scale and any(e["run_id"] == row["run_id"] for e in eligible)):
        early, late = run["checkpoints"][EARLY], run["checkpoints"][LATE]
        for index in range(len(CONFIG["confidence_bins"]) - 1):
            early_count, early_agree = confidence_bin(early, index)
            late_count, late_agree = confidence_bin(late, index)
            if min(early_count, late_count) >= 100:
                delta = late_agree - early_agree
                bin_comparisons.append({
                    "run_id": run["run_id"], "bin_index": index,
                    "low": CONFIG["confidence_bins"][index], "high": CONFIG["confidence_bins"][index + 1],
                    "early_count": early_count, "late_count": late_count,
                    "early_agreement": early_agree, "late_agreement": late_agree, "delta": delta,
                })
    for index in range(len(CONFIG["confidence_bins"]) - 1):
        values = [row["delta"] for row in bin_comparisons if row["bin_index"] == index]
        if values:
            pooled_bin_deltas.append({"bin_index": index, "mean_delta": mean(values), "runs": len(values)})

    leave_one_out_medians = [
        float(np.median([value for index, value in enumerate(agreement_deltas) if index != omitted]))
        for omitted in range(len(agreement_deltas))
    ] if len(agreement_deltas) > 1 else []
    criteria = {
        "minimum_runs": len(eligible) >= 5,
        "direction": sum(value < 0 for value in agreement_deltas) / len(eligible) >= 0.8 if eligible else False,
        "magnitude": float(np.median(agreement_deltas)) <= -0.05 if eligible else False,
        "nll_damage": sum(value > 0 for value in nll_deltas) / len(eligible) >= 0.8 if eligible else False,
        "kl": sum(value > 0 for value in kl_deltas) / len(eligible) >= 0.8 if eligible else False,
        "resampling": sum(row["eval_negative_count"] >= 2 for row in eligible) / len(eligible) >= 0.8 if eligible else False,
        "no_outlier_dominance": bool(leave_one_out_medians) and all(value < 0 for value in leave_one_out_medians),
        "confidence": (
            len({row["bin_index"] for row in bin_comparisons}) >= 3
            and sum(row["delta"] < 0 for row in bin_comparisons) / len(bin_comparisons) >= 0.75
            and mean(row["delta"] for row in bin_comparisons) < 0
        ) if bin_comparisons else False,
    }
    return {
        "scale_m": scale, "eligible_runs": len(eligible), "excluded": excluded,
        "individual_runs": eligible,
        "negative_runs": sum(value < 0 for value in agreement_deltas),
        "mean_delta_agreement": mean(agreement_deltas),
        "median_delta_agreement": float(np.median(agreement_deltas)) if eligible else None,
        "std_delta_agreement": float(np.std(agreement_deltas, ddof=1)) if len(eligible) > 1 else None,
        "bootstrap_95_ci_mean_delta": bootstrap_ci(agreement_deltas),
        "positive_nll_damage_runs": sum(value > 0 for value in nll_deltas),
        "positive_kl_runs": sum(value > 0 for value in kl_deltas),
        "confidence_bin_comparisons": bin_comparisons,
        "pooled_confidence_bin_deltas": pooled_bin_deltas,
        "leave_one_out_medians": leave_one_out_medians,
        "criteria": criteria,
        "scale_pass": all(criteria.values()),
        "nll_confound": confound_analysis(runs, scale),
    }


def plot_results(runs: list[dict], analyses: list[dict]) -> None:
    figure_dir = ROOT / "figures"
    figure_dir.mkdir(exist_ok=True)
    colors = plt.cm.tab10(np.linspace(0, 1, 10))

    fig, axes = plt.subplots(1, 2, figsize=(11, 4), sharey=False)
    for axis, scale in zip(axes, CONFIG["scales"]):
        for run in sorted((r for r in runs if r["scale"] == scale), key=lambda r: r["run_id"]):
            rows = [run["checkpoints"][step] for step in CONFIG["checkpoint_steps"] if step in run["checkpoints"]]
            axis.plot([r["progress"] for r in rows], [r["agreement"] for r in rows], marker="o", label=f"seed{run['run_id']}", color=colors[run["run_id"] - 1])
        axis.set(title=f"Pythia-{scale}M", xlabel="Normalized training progress", ylabel="Middle-layer top-1 agreement")
        axis.grid(alpha=.25); axis.legend(ncol=2, fontsize=8)
    fig.tight_layout(); fig.savefig(figure_dir / "fig1_independent_run_trajectories.png", dpi=180); plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
    for axis, analysis in zip(axes, analyses):
        values = [r["delta_agreement"] for r in analysis["individual_runs"]]
        axis.axhline(0, color="black", lw=1); axis.bar(range(1, len(values) + 1), values)
        axis.axhline(-.05, color="firebrick", ls="--", lw=1)
        axis.set(title=f"Pythia-{analysis['scale_m']}M", xlabel="Independent run", ylabel="Late - early agreement")
    fig.tight_layout(); fig.savefig(figure_dir / "fig2_delta_distribution.png", dpi=180); plt.close(fig)

    for metric, filename, ylabel in [
        ("nll_damage", "fig3_nll_damage.png", "Deleted - intact NLL"),
        ("kl", "fig4_kl_divergence.png", "KL(intact || deleted)"),
    ]:
        fig, axes = plt.subplots(1, 2, figsize=(11, 4))
        for axis, scale in zip(axes, CONFIG["scales"]):
            for run in sorted((r for r in runs if r["scale"] == scale), key=lambda r: r["run_id"]):
                rows = [run["checkpoints"][step] for step in CONFIG["checkpoint_steps"] if step in run["checkpoints"]]
                axis.plot([r["progress"] for r in rows], [r[metric] for r in rows], marker="o", label=f"seed{run['run_id']}")
            axis.set(title=f"Pythia-{scale}M", xlabel="Normalized training progress", ylabel=ylabel); axis.grid(alpha=.25)
        fig.tight_layout(); fig.savefig(figure_dir / filename, dpi=180); plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4), sharey=False)
    for axis, analysis in zip(axes, analyses):
        rows = analysis["confidence_bin_comparisons"]
        indices = sorted({r["bin_index"] for r in rows})
        early = [mean(r["early_agreement"] for r in rows if r["bin_index"] == i) for i in indices]
        late = [mean(r["late_agreement"] for r in rows if r["bin_index"] == i) for i in indices]
        labels = [f"{CONFIG['confidence_bins'][i]:.2g}-{CONFIG['confidence_bins'][i+1]:.2g}" for i in indices]
        x = np.arange(len(indices)); axis.bar(x - .18, early, .36, label="early"); axis.bar(x + .18, late, .36, label="late")
        axis.set(title=f"Pythia-{analysis['scale_m']}M", xlabel="Intact confidence bin", ylabel="Agreement", xticks=x, xticklabels=labels); axis.legend()
    fig.tight_layout(); fig.savefig(figure_dir / "fig5_confidence_matched.png", dpi=180); plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    for axis, scale in zip(axes, CONFIG["scales"]):
        scale_runs = [run for run in runs if run["scale"] == scale]
        sample = next((run for run in scale_runs if len(run["checkpoints"]) == len(CONFIG["checkpoint_steps"])), None)
        if not sample:
            continue
        layers = sample["checkpoints"][EARLY]["raw"]["candidate_layers"]
        matrix = []
        for step in CONFIG["checkpoint_steps"]:
            matrix.append([
                mean(
                    layer["top1_agreement"]
                    for run in scale_runs
                    for seed in run["checkpoints"][step]["raw"]["seed_results"]
                    for layer in seed["layers"] if layer["layer"] == layer_index
                )
                for layer_index in layers
            ])
        image = axis.imshow(np.asarray(matrix).T, aspect="auto", origin="lower", cmap="viridis")
        axis.set(title=f"Pythia-{scale}M", xlabel="Training step", ylabel="Deleted layer", xticks=range(len(CONFIG["checkpoint_steps"])), xticklabels=[f"{s//1000}k" for s in CONFIG["checkpoint_steps"]], yticks=range(len(layers)), yticklabels=layers)
        fig.colorbar(image, ax=axis, label="Agreement")
    fig.tight_layout(); fig.savefig(figure_dir / "fig6_layer_progress_heatmap.png", dpi=180); plt.close(fig)


def write_tables(runs: list[dict], analyses: list[dict]) -> None:
    table_dir = ROOT / "results"
    table_dir.mkdir(exist_ok=True)
    with (table_dir / "checkpoint_metrics.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["scale_m", "run_id", "step", "progress", "intact_nll", "agreement", "nll_damage", "kl"])
        for run in runs:
            for step, row in sorted(run["checkpoints"].items()):
                writer.writerow([run["scale"], run["run_id"], step, row["progress"], row["baseline_nll"], row["agreement"], row["nll_damage"], row["kl"]])
    with (table_dir / "run_deltas.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["scale_m", "run_id", "delta_agreement", "delta_nll_damage", "delta_kl", "negative_eval_resamples", "spearman"])
        for analysis in analyses:
            for row in analysis["individual_runs"]:
                writer.writerow([analysis["scale_m"], row["run_id"], row["delta_agreement"], row["delta_nll_damage"], row["delta_kl"], row["eval_negative_count"], row["spearman_progress_agreement"]])


def main() -> None:
    runs = load_runs()
    analyses = [analyze_scale(runs, scale) for scale in CONFIG["scales"]]
    complete = all(len([run for run in runs if run["scale"] == scale and len(run["checkpoints"]) == len(CONFIG["checkpoint_steps"])]) >= 5 for scale in CONFIG["scales"])
    confidence_pass = all(analysis["criteria"]["confidence"] for analysis in analyses)
    confound_pass = all(analysis["nll_confound"].get("status") == "pass" for analysis in analyses)
    if not complete:
        final = "INCONCLUSIVE"
    elif all(analysis["scale_pass"] for analysis in analyses) and confidence_pass:
        final = "PROMOTE"
    elif any(not analysis["criteria"]["confidence"] for analysis in analyses) and all(analysis["criteria"]["direction"] for analysis in analyses):
        final = "KILL-CONFOUND"
    else:
        final = "KILL-STABILITY"
    summary = {
        "arc": "ARC-20260825-5060-002", "complete": complete, "analyses": analyses,
        "confidence_control_pass": confidence_pass,
        "nll_competence_confound": "PASS" if confound_pass else "PARTIAL",
        "final": final,
        "total_checkpoint_runtime_seconds": sum(run["runtime_seconds"] for run in runs),
        "peak_cuda_bytes": max((run["peak_cuda_bytes"] for run in runs), default=0),
    }
    result_dir = ROOT / "results"; result_dir.mkdir(exist_ok=True)
    (result_dir / "stability_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_tables(runs, analyses)
    if complete:
        plot_results(runs, analyses)
    print(json.dumps({"final": final, "complete": complete, "scales": [{"scale": a["scale_m"], "runs": a["eligible_runs"], "negative": a["negative_runs"], "median_delta": a["median_delta_agreement"], "pass": a["scale_pass"]} for a in analyses]}, indent=2))


if __name__ == "__main__":
    main()
