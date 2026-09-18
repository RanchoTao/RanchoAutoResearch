"""Aggregate the frozen WSD-window analysis without changing its contract."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
PREVIOUS = ROOT.parent / "ARC-20260825-5060-003"
CONFIG = yaml.safe_load((ROOT / "configs/wsd_window.yaml").read_text(encoding="utf-8"))


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
        "revision": checkpoint["revision"],
        "commit_hash": checkpoint["commit_hash"],
        "step": checkpoint["step"],
        "training_tokens": checkpoint["training_tokens"],
        "normalized_progress": checkpoint["normalized_progress"],
        "phase": (
            "stable/pre-decay" if checkpoint["step"] < CONFIG["inferred_decay_start_step"]
            else "WSD decay"
        ),
        "baseline_nll": mean(row["baseline_nll"] for row in eval_rows),
        "confidence": mean(row["confidence"] for row in eval_rows),
        "agreement": mean(row["agreement"] for row in eval_rows),
        "nll_damage": mean(row["nll_damage"] for row in eval_rows),
        "kl": mean(row["kl"] for row in eval_rows),
        "eval_rows": eval_rows,
        "raw": checkpoint,
    }


def bootstrap_ci(values: list[float]) -> list[float]:
    rng = np.random.default_rng(20260825)
    array = np.asarray(values, dtype=float)
    draws = np.mean(
        rng.choice(array, size=(CONFIG["bootstrap_samples"], len(array)), replace=True),
        axis=1,
    )
    return [float(value) for value in np.quantile(draws, [0.025, 0.975])]


def seed_map(checkpoint: dict) -> dict[int, dict]:
    return {row["evaluation_seed"]: row for row in checkpoint["eval_rows"]}


def interval(start: dict, end: dict, metric: str = "agreement") -> dict:
    starts, ends = seed_map(start), seed_map(end)
    deltas = [
        ends[seed][metric] - starts[seed][metric]
        for seed in CONFIG["evaluation_seeds"]
    ]
    return {
        "start_revision": start["revision"],
        "end_revision": end["revision"],
        "start_progress": start["normalized_progress"],
        "end_progress": end["normalized_progress"],
        "metric": metric,
        "start_mean": start[metric],
        "end_mean": end[metric],
        "mean_delta": end[metric] - start[metric],
        "seed_deltas": deltas,
        "bootstrap_95_ci": bootstrap_ci(deltas),
        "all_seed_deltas_negative": all(value < 0 for value in deltas),
        "all_seed_deltas_positive": all(value > 0 for value in deltas),
    }


def phase_slope(checkpoints: list[dict], metric: str = "agreement") -> dict:
    x = np.asarray([row["normalized_progress"] for row in checkpoints])
    slopes = []
    for seed in CONFIG["evaluation_seeds"]:
        y = np.asarray([seed_map(row)[seed][metric] for row in checkpoints])
        slopes.append(float(np.polyfit(x, y, 1)[0]))
    return {
        "metric": metric,
        "revisions": [row["revision"] for row in checkpoints],
        "mean_slope": float(np.mean(slopes)),
        "seed_slopes": slopes,
        "bootstrap_95_ci": bootstrap_ci(slopes),
    }


def confidence_bin(checkpoint: dict, index: int) -> tuple[int, float | None]:
    count = 0
    agreed = 0.0
    for seed in checkpoint["raw"]["seed_results"]:
        for layer in seed["layers"]:
            row = layer["confidence_bins"][index]
            if row["agreement"] is not None:
                count += row["count"]
                agreed += row["agreement"] * row["count"]
    return count, agreed / count if count else None


def confidence_comparison(start: dict, end: dict) -> dict:
    bins = []
    for index in range(len(CONFIG["confidence_bins"]) - 1):
        start_count, start_agreement = confidence_bin(start, index)
        end_count, end_agreement = confidence_bin(end, index)
        bins.append({
            "low": CONFIG["confidence_bins"][index],
            "high": CONFIG["confidence_bins"][index + 1],
            "start_count": start_count,
            "end_count": end_count,
            "start_agreement": start_agreement,
            "end_agreement": end_agreement,
            "delta": end_agreement - start_agreement,
            "eligible": min(start_count, end_count) >= 100,
        })
    eligible = [row for row in bins if row["eligible"]]
    return {
        "start_revision": start["revision"],
        "end_revision": end["revision"],
        "bins": bins,
        "eligible_bins": len(eligible),
        "negative_bins": sum(row["delta"] < 0 for row in eligible),
        "mean_delta": mean(row["delta"] for row in eligible),
    }


def nll_adjustment(checkpoints: list[dict]) -> dict:
    agreement = np.asarray([row["agreement"] for row in checkpoints])
    nll = np.asarray([row["baseline_nll"] for row in checkpoints])
    progress = np.asarray([row["normalized_progress"] for row in checkpoints])
    znll = (nll - nll.mean()) / nll.std()
    zprogress = (progress - progress.mean()) / progress.std()
    design_nll = np.column_stack([np.ones(len(checkpoints)), znll])
    design_full = np.column_stack([np.ones(len(checkpoints)), znll, zprogress])
    fit_nll = np.linalg.lstsq(design_nll, agreement, rcond=None)[0]
    fit_full = np.linalg.lstsq(design_full, agreement, rcond=None)[0]
    agreement_residual = agreement - design_nll @ fit_nll
    progress_fit = np.linalg.lstsq(design_nll, zprogress, rcond=None)[0]
    progress_residual = zprogress - design_nll @ progress_fit
    return {
        "standardized_progress_coefficient_controlling_nll": float(fit_full[2]),
        "partial_correlation_progress_agreement_given_nll": float(
            np.corrcoef(agreement_residual, progress_residual)[0, 1]
        ),
        "observations": len(checkpoints),
        "warning": "descriptive only: one trajectory",
    }


def load_competence(revision: str) -> dict:
    local = ROOT / "experiments/competence" / f"hellaswag-{revision}.json"
    previous = PREVIOUS / "experiments/competence" / f"hellaswag-{revision}.json"
    path = local if local.exists() else previous
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    payload = json.loads(
        (ROOT / "experiments/trajectory/raw_results.json").read_text(encoding="utf-8")
    )
    checkpoints = [
        checkpoint_summary(row)
        for row in sorted(payload["checkpoints"], key=lambda item: item["step"])
    ]
    expected_steps = set(CONFIG["checkpoint_steps"])
    if {row["step"] for row in checkpoints} != expected_steps:
        raise ValueError("Full preregistered eight-checkpoint trajectory is required")
    by_step = {row["step"]: row for row in checkpoints}
    competence = {revision: load_competence(revision) for revision in CONFIG["revisions"]}
    for row in checkpoints:
        task = competence[row["revision"]]
        row["hellaswag_raw_accuracy"] = task["raw_accuracy"]
        row["hellaswag_normalized_accuracy"] = task["normalized_accuracy"]
        row["hellaswag_normalized_ci"] = task["normalized_bootstrap_95_ci"]

    early = by_step[320000]
    pre_end = by_step[1920000]
    decay_start = by_step[2080000]
    prefinal = by_step[2400000]
    final = by_step[2560000]
    total = interval(early, final)
    pre = interval(early, pre_end)
    boundary = interval(pre_end, decay_start)
    confirmed_decay = interval(decay_start, final)
    bracketing = interval(pre_end, final)
    final_excluded_total = interval(early, prefinal)
    final_excluded_decay = interval(decay_start, prefinal)
    final_interval = interval(prefinal, final)

    adjacent = [interval(left, right) for left, right in zip(checkpoints, checkpoints[1:])]
    largest = max(adjacent, key=lambda row: abs(row["mean_delta"]))
    total_delta = total["mean_delta"]
    confirmed_fraction = confirmed_decay["mean_delta"] / total_delta if total_delta else None
    bracketing_fraction = bracketing["mean_delta"] / total_delta if total_delta else None
    pre_fraction = pre["mean_delta"] / total_delta if total_delta else None
    largest_fraction = abs(largest["mean_delta"]) / abs(total_delta) if total_delta else None
    final_bracketing_fraction = (
        abs(final_interval["mean_delta"]) / abs(bracketing["mean_delta"])
        if bracketing["mean_delta"] else None
    )

    pre_points = [row for row in checkpoints if row["step"] <= 1920000]
    decay_points = [row for row in checkpoints if row["step"] >= 2080000]
    pre_slope = phase_slope(pre_points)
    decay_slope = phase_slope(decay_points)

    finite = all(
        np.isfinite(value)
        for row in checkpoints
        for value in [row["baseline_nll"], row["agreement"], row["nll_damage"], row["kl"]]
    )
    expected_commits = {
        "step-2080000": "94c6cef4a924c2c2edbf0da3b9d082010c1f2629",
        "step-2240000": "8f5f6865f1d1d368a03a55a9a3a90b458ab7b513",
        "step-2400000": "94a4fe6b676f6a84980793194d34798aabd24e48",
    }
    commit_match = all(
        next(row for row in checkpoints if row["revision"] == revision)["commit_hash"] == commit
        for revision, commit in expected_commits.items()
    )
    competence_pass = all(
        row["baseline_nll"] <= CONFIG["competence_max_nll"]
        and competence[row["revision"]]["normalized_accuracy"] >= CONFIG["hellaswag_normalized_accuracy_min"]
        and competence[row["revision"]]["raw_accuracy"] >= CONFIG["hellaswag_raw_accuracy_min"]
        and competence[row["revision"]]["distinct_normalized_labels"] >= 3
        and competence[row["revision"]]["max_normalized_label_fraction"] <= CONFIG["hellaswag_max_label_fraction"]
        for row in checkpoints
    )

    broad = (
        pre["mean_delta"] <= CONFIG["meaningful_pre_decay_delta"]
        and pre_fraction is not None and pre_fraction >= CONFIG["meaningful_pre_decay_fraction"]
        and pre["all_seed_deltas_negative"] and pre["bootstrap_95_ci"][1] < 0
        and pre_slope["mean_slope"] < 0 and pre_slope["bootstrap_95_ci"][1] < 0
        and final_excluded_total["all_seed_deltas_negative"]
        and final_excluded_total["bootstrap_95_ci"][1] < 0
    )
    decay_adjacent = [row for row in adjacent if row["start_progress"] >= 0.8125]
    narrow = (
        not broad
        and confirmed_decay["mean_delta"] < 0
        and confirmed_fraction is not None and confirmed_fraction >= 0.50
        and sum(row["mean_delta"] < 0 for row in decay_adjacent) >= 2
        and final_excluded_decay["all_seed_deltas_negative"]
        and final_excluded_decay["bootstrap_95_ci"][1] < 0
    )
    final_risk = (
        not broad and not narrow
        and final_bracketing_fraction is not None and final_bracketing_fraction >= 0.50
        and (
            not final_excluded_decay["all_seed_deltas_negative"]
            or final_excluded_decay["bootstrap_95_ci"][1] >= 0
        )
    )
    density_valid = len(pre_points) >= 1 and len(decay_points) >= 4
    if not finite or not commit_match or not competence_pass or not density_valid:
        verdict = "BLOCKED-WINDOW"
    elif broad:
        verdict = "PROMOTE-BROAD"
    elif narrow:
        verdict = "NARROW-WSD"
    elif final_risk:
        verdict = "FINAL-CHECKPOINT-RISK"
    else:
        verdict = "MIXED"

    nll_intervals = {
        "total": interval(early, final, "nll_damage"),
        "pre_decay": interval(early, pre_end, "nll_damage"),
        "confirmed_decay": interval(decay_start, final, "nll_damage"),
        "final_excluded_decay": interval(decay_start, prefinal, "nll_damage"),
    }
    kl_intervals = {
        "total": interval(early, final, "kl"),
        "pre_decay": interval(early, pre_end, "kl"),
        "confirmed_decay": interval(decay_start, final, "kl"),
        "final_excluded_decay": interval(decay_start, prefinal, "kl"),
    }
    new_rows = [row["raw"] for row in checkpoints if row["step"] in CONFIG["new_checkpoint_steps"]]
    new_competence = [competence[revision] for revision in CONFIG["new_revisions"]]
    summary = {
        "arc": "ARC-20260825-5060-004",
        "model": CONFIG["model"],
        "dtype": CONFIG["dtype"],
        "schedule": {
            "final_step": CONFIG["final_step"],
            "tokens_per_step": CONFIG["tokens_per_step"],
            "documented_decay_fraction": CONFIG["decay_fraction"],
            "best_supported_decay_start_step": CONFIG["inferred_decay_start_step"],
            "best_supported_decay_start_tokens": CONFIG["inferred_decay_start_step"] * CONFIG["tokens_per_step"],
            "exact_boundary_checkpoint_public": False,
            "last_public_pre_decay_step": CONFIG["last_public_pre_decay_step"],
            "first_public_decay_step": CONFIG["first_public_decay_step"],
        },
        "sample_counts": {
            "evaluation_seeds": len(CONFIG["evaluation_seeds"]),
            "tokens_per_checkpoint": len(CONFIG["evaluation_seeds"]) * CONFIG["sequences_per_seed"] * CONFIG["sequence_length"],
            "candidate_layers": 30,
            "token_layer_observations_per_checkpoint": len(CONFIG["evaluation_seeds"]) * CONFIG["sequences_per_seed"] * CONFIG["sequence_length"] * 30,
            "hellaswag_examples_per_checkpoint": CONFIG["hellaswag_examples"],
        },
        "checkpoints": [
            {key: value for key, value in row.items() if key not in {"raw", "eval_rows"}}
            for row in checkpoints
        ],
        "primary": {
            "total": total,
            "pre_decay": pre,
            "boundary_straddling": boundary,
            "confirmed_decay": confirmed_decay,
            "boundary_bracketing": bracketing,
            "final_excluded_total": final_excluded_total,
            "final_excluded_confirmed_decay": final_excluded_decay,
            "final_interval": final_interval,
            "pre_decay_fraction_of_total": pre_fraction,
            "confirmed_decay_fraction_of_total": confirmed_fraction,
            "boundary_bracketing_fraction_of_total": bracketing_fraction,
            "largest_adjacent_interval": largest,
            "largest_interval_fraction_of_total": largest_fraction,
            "final_interval_fraction_of_bracketing_change": final_bracketing_fraction,
        },
        "piecewise": {"pre_decay": pre_slope, "confirmed_decay": decay_slope},
        "adjacent_intervals": adjacent,
        "nll_damage": nll_intervals,
        "kl": kl_intervals,
        "confidence_controls": {
            "pre_decay": confidence_comparison(early, pre_end),
            "confirmed_decay": confidence_comparison(decay_start, final),
            "final_excluded_total": confidence_comparison(early, prefinal),
        },
        "nll_adjustment": nll_adjustment(checkpoints),
        "competence": {
            "all_checkpoints_pass": competence_pass,
            "normalized_accuracy_min": min(row["hellaswag_normalized_accuracy"] for row in checkpoints),
            "normalized_accuracy_max": max(row["hellaswag_normalized_accuracy"] for row in checkpoints),
            "intact_nll_min": min(row["baseline_nll"] for row in checkpoints),
            "intact_nll_max": max(row["baseline_nll"] for row in checkpoints),
        },
        "integrity": {
            "finite": finite,
            "new_commit_match": commit_match,
            "density_valid": density_valid,
        },
        "verdict_criteria": {
            "promote_broad": broad,
            "narrow_wsd": narrow,
            "final_checkpoint_risk": final_risk,
        },
        "verdict": verdict,
        "new_trajectory_runtime_seconds": sum(row["runtime_seconds"] for row in new_rows),
        "new_competence_runtime_seconds": sum(row["runtime_seconds"] for row in new_competence),
        "peak_cuda_bytes": max(
            [row["peak_cuda_bytes"] for row in new_rows]
            + [row["peak_cuda_bytes"] for row in new_competence]
        ),
    }

    results = ROOT / "results"
    figures = ROOT / "figures"
    results.mkdir(exist_ok=True)
    figures.mkdir(exist_ok=True)
    (results / "wsd_window_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    with (results / "wsd_checkpoint_metrics.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow([
            "revision", "commit", "step", "tokens", "progress", "phase",
            "intact_nll", "agreement", "nll_damage", "kl", "confidence",
            "hellaswag_raw", "hellaswag_normalized",
        ])
        for row in checkpoints:
            writer.writerow([
                row["revision"], row["commit_hash"], row["step"], row["training_tokens"],
                row["normalized_progress"], row["phase"], row["baseline_nll"],
                row["agreement"], row["nll_damage"], row["kl"], row["confidence"],
                row["hellaswag_raw_accuracy"], row["hellaswag_normalized_accuracy"],
            ])
    with (results / "adjacent_intervals.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["start", "end", "mean_delta", "seed11", "seed23", "seed37", "ci_low", "ci_high"])
        for row in adjacent:
            writer.writerow([
                row["start_revision"], row["end_revision"], row["mean_delta"],
                *row["seed_deltas"], *row["bootstrap_95_ci"],
            ])

    x = np.asarray([row["normalized_progress"] for row in checkpoints])
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.2))
    metrics = [("agreement", "Top-1 agreement"), ("nll_damage", "Deleted - intact NLL"), ("kl", "KL(intact || deleted)")]
    for axis, (metric, label) in zip(axes, metrics):
        axis.plot(x, [row[metric] for row in checkpoints], marker="o")
        axis.axvline(0.8, color="black", ls="--", lw=1, label="inferred WSD start")
        axis.axvspan(0.8, 1.0, color="tab:orange", alpha=0.10)
        axis.set(xlabel="Normalized training progress", ylabel=label)
        axis.grid(alpha=0.25)
    axes[0].legend(fontsize=8)
    fig.suptitle("SmolLM2-360M dense WSD-window trajectory (unsmoothed)")
    fig.tight_layout()
    fig.savefig(figures / "dense_wsd_trajectory.png", dpi=180)
    plt.close(fig)

    fig, axis = plt.subplots(figsize=(8, 5))
    agreement = np.asarray([row["agreement"] for row in checkpoints])
    axis.plot(x, agreement, color="0.55", marker="o", label="checkpoint mean")
    for points, color, label in [(pre_points, "tab:blue", "pre-decay fit"), (decay_points, "tab:orange", "decay fit")]:
        px = np.asarray([row["normalized_progress"] for row in points])
        py = np.asarray([row["agreement"] for row in points])
        coefficient = np.polyfit(px, py, 1)
        axis.plot(px, np.polyval(coefficient, px), color=color, lw=2, label=f"{label}: slope {coefficient[0]:.4f}")
    axis.axvline(0.8, color="black", ls="--", lw=1)
    axis.axvspan(0.8, 1.0, color="tab:orange", alpha=0.10)
    axis.set(xlabel="Normalized training progress", ylabel="Top-1 agreement", title="Frozen piecewise comparison")
    axis.grid(alpha=0.25)
    axis.legend()
    fig.tight_layout()
    fig.savefig(figures / "piecewise_pre_vs_decay.png", dpi=180)
    plt.close(fig)

    comparison_rows = [total, pre, confirmed_decay, final_excluded_decay, final_interval]
    labels = ["total", "pre-decay", "decay", "decay excl. final", "final interval"]
    values = [row["mean_delta"] for row in comparison_rows]
    lower = [value - row["bootstrap_95_ci"][0] for value, row in zip(values, comparison_rows)]
    upper = [row["bootstrap_95_ci"][1] - value for value, row in zip(values, comparison_rows)]
    fig, axis = plt.subplots(figsize=(9, 5))
    axis.bar(np.arange(len(values)), values, color=["0.4", "tab:blue", "tab:orange", "tab:green", "tab:red"])
    axis.errorbar(np.arange(len(values)), values, yerr=np.asarray([lower, upper]), fmt="none", color="black", capsize=4)
    axis.axhline(0, color="black", lw=1)
    axis.set(xticks=np.arange(len(values)), xticklabels=labels, ylabel="Agreement change", title="Final-checkpoint-excluded comparison")
    axis.grid(alpha=0.25, axis="y")
    fig.tight_layout()
    fig.savefig(figures / "final_checkpoint_excluded.png", dpi=180)
    plt.close(fig)

    print(json.dumps({
        "exact_WSD_decay_boundary": summary["schedule"],
        "usable_checkpoints": len(checkpoints),
        "pre_decay_primary_change": pre,
        "confirmed_decay_primary_change": confirmed_decay,
        "confirmed_decay_fraction_of_total": confirmed_fraction,
        "largest_single_interval": largest,
        "excluding_final_checkpoint": final_excluded_total,
        "NLL_damage": nll_intervals,
        "KL": kl_intervals,
        "competence": summary["competence"],
        "FINAL_VERDICT": verdict,
    }, indent=2))


if __name__ == "__main__":
    main()

