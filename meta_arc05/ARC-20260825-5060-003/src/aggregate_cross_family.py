"""Aggregate the preregistered cross-family trajectory and render figures."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import yaml


ROOT = Path(__file__).resolve().parents[1]
CONFIG = yaml.safe_load((ROOT / "configs/cross_family.yaml").read_text(encoding="utf-8"))


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
        "revision": checkpoint["revision"], "commit_hash": checkpoint["commit_hash"],
        "step": checkpoint["step"], "training_tokens": checkpoint["training_tokens"],
        "normalized_progress": checkpoint["normalized_progress"],
        "baseline_nll": mean(row["baseline_nll"] for row in eval_rows),
        "confidence": mean(row["confidence"] for row in eval_rows),
        "agreement": mean(row["agreement"] for row in eval_rows),
        "nll_damage": mean(row["nll_damage"] for row in eval_rows),
        "kl": mean(row["kl"] for row in eval_rows),
        "eval_rows": eval_rows, "raw": checkpoint,
    }


def confidence_bin(checkpoint: dict, index: int) -> tuple[int, float | None]:
    count = 0
    agreed = 0.0
    for seed in checkpoint["seed_results"]:
        for layer in seed["layers"]:
            row = layer["confidence_bins"][index]
            if row["agreement"] is not None:
                count += row["count"]
                agreed += row["agreement"] * row["count"]
    return count, agreed / count if count else None


def bootstrap_resample_ci(values: list[float]) -> list[float]:
    rng = np.random.default_rng(20260825)
    array = np.asarray(values)
    draws = np.mean(rng.choice(array, size=(10000, len(array)), replace=True), axis=1)
    return [float(value) for value in np.quantile(draws, [0.025, 0.975])]


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
        "partial_correlation_progress_agreement_given_nll": float(np.corrcoef(agreement_residual, progress_residual)[0, 1]),
        "observations": len(checkpoints),
        "warning": "descriptive only: one trajectory and five checkpoints",
    }


def main() -> None:
    trajectory_path = ROOT / CONFIG["output_dir"] / "trajectory/raw_results.json"
    payload = json.loads(trajectory_path.read_text(encoding="utf-8"))
    checkpoints = [checkpoint_summary(row) for row in sorted(payload["checkpoints"], key=lambda row: row["step"])]
    competence = []
    for revision in CONFIG["revisions"]:
        path = ROOT / CONFIG["output_dir"] / "competence" / f"hellaswag-{revision}.json"
        competence.append(json.loads(path.read_text(encoding="utf-8")))
    competence_by_revision = {row["revision"]: row for row in competence}
    for row in checkpoints:
        task = competence_by_revision[row["revision"]]
        row["hellaswag_raw_accuracy"] = task["raw_accuracy"]
        row["hellaswag_normalized_accuracy"] = task["normalized_accuracy"]
        row["hellaswag_normalized_ci"] = task["normalized_bootstrap_95_ci"]

    early, late = checkpoints[0], checkpoints[-1]
    early_eval = {row["evaluation_seed"]: row for row in early["eval_rows"]}
    late_eval = {row["evaluation_seed"]: row for row in late["eval_rows"]}
    resample_deltas = [
        late_eval[seed]["agreement"] - early_eval[seed]["agreement"]
        for seed in CONFIG["evaluation_seeds"]
    ]
    bin_rows = []
    for index in range(len(CONFIG["confidence_bins"]) - 1):
        early_count, early_agreement = confidence_bin(early["raw"], index)
        late_count, late_agreement = confidence_bin(late["raw"], index)
        if min(early_count, late_count) >= 100:
            bin_rows.append({
                "bin_index": index, "low": CONFIG["confidence_bins"][index],
                "high": CONFIG["confidence_bins"][index + 1],
                "early_count": early_count, "late_count": late_count,
                "early_agreement": early_agreement, "late_agreement": late_agreement,
                "delta": late_agreement - early_agreement,
            })

    finite = all(
        np.isfinite(value)
        for row in checkpoints
        for value in [row["baseline_nll"], row["agreement"], row["nll_damage"], row["kl"]]
    )
    late_task = competence_by_revision[CONFIG["revisions"][-1]]
    competence_pass = (
        late_task["normalized_accuracy"] >= CONFIG["hellaswag_normalized_accuracy_min"]
        and late_task["raw_accuracy"] >= CONFIG["hellaswag_raw_accuracy_min"]
        and late_task["distinct_normalized_labels"] >= 3
        and late_task["max_normalized_label_fraction"] <= CONFIG["hellaswag_max_label_fraction"]
        and early["baseline_nll"] <= CONFIG["competence_max_nll"]
        and late["baseline_nll"] <= CONFIG["competence_max_nll"]
    )
    delta_agreement = late["agreement"] - early["agreement"]
    criteria = {
        "finite_harness": finite,
        "competence": competence_pass,
        "magnitude": delta_agreement <= -0.05,
        "all_resamples_negative": all(value < 0 for value in resample_deltas),
        "bootstrap_ci_below_zero": bootstrap_resample_ci(resample_deltas)[1] < 0,
        "nll_damage_direction": late["nll_damage"] - early["nll_damage"] > 0,
        "kl_direction": late["kl"] - early["kl"] > 0,
        "confidence": (
            len(bin_rows) >= 3
            and sum(row["delta"] < 0 for row in bin_rows) / len(bin_rows) >= 0.75
            and mean(row["delta"] for row in bin_rows) < 0
        ),
    }
    if not finite:
        verdict = "BLOCKED"
    elif all(criteria.values()):
        verdict = "PROMOTE"
    elif competence_pass and delta_agreement < 0:
        verdict = "MIXED"
    elif competence_pass and delta_agreement >= 0 and bootstrap_resample_ci(resample_deltas)[0] >= 0:
        verdict = "KILL-CROSS-FAMILY"
    else:
        verdict = "MIXED"

    summary = {
        "arc": "ARC-20260825-5060-003", "selected_family": "SmolLM2-360M",
        "model": CONFIG["model"], "dtype": CONFIG["dtype"],
        "checkpoints": [{key: value for key, value in row.items() if key not in {"raw", "eval_rows"}} for row in checkpoints],
        "primary": {
            "early_agreement": early["agreement"], "late_agreement": late["agreement"],
            "delta_agreement": delta_agreement, "resample_deltas": resample_deltas,
            "resample_bootstrap_95_ci": bootstrap_resample_ci(resample_deltas),
        },
        "nll_damage": {"early": early["nll_damage"], "late": late["nll_damage"], "delta": late["nll_damage"] - early["nll_damage"]},
        "kl": {"early": early["kl"], "late": late["kl"], "delta": late["kl"] - early["kl"]},
        "confidence_bins": bin_rows,
        "nll_adjustment": nll_adjustment(checkpoints),
        "training_schedule_context": {
            "scheduler": "WSD",
            "documented_decay_fraction": 0.20,
            "decay_boundary_normalized_progress": 0.80,
            "warning": "the sparse 0.75 to 1.0 interval straddles the documented decay boundary",
        },
        "strongest_negative_evidence": (
            "the -0.04135 endpoint decline misses the preregistered -0.05 gate; "
            "58.7% of it occurs in the final interval, which straddles the documented WSD decay boundary"
        ),
        "recommended_next_arc": (
            "prospectively resolve the public SmolLM2 80%-100% decay window before mechanism work"
        ),
        "criteria": criteria, "verdict": verdict,
        "trajectory_runtime_seconds": sum(row["runtime_seconds"] for row in payload["checkpoints"]),
        "competence_runtime_seconds": sum(row["runtime_seconds"] for row in competence),
        "peak_cuda_bytes": max(
            max(row["peak_cuda_bytes"] for row in payload["checkpoints"]),
            max(row["peak_cuda_bytes"] for row in competence),
        ),
    }
    results_dir = ROOT / "results"; results_dir.mkdir(exist_ok=True)
    (results_dir / "cross_family_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    with (results_dir / "per_checkpoint_results.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["revision", "commit", "step", "tokens", "progress", "intact_nll", "agreement", "nll_damage", "kl", "hellaswag_raw", "hellaswag_norm"])
        for row in checkpoints:
            writer.writerow([row["revision"], row["commit_hash"], row["step"], row["training_tokens"], row["normalized_progress"], row["baseline_nll"], row["agreement"], row["nll_damage"], row["kl"], row["hellaswag_raw_accuracy"], row["hellaswag_normalized_accuracy"]])

    figure_dir = ROOT / "figures"; figure_dir.mkdir(exist_ok=True)
    x = [row["normalized_progress"] for row in checkpoints]
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    axes[0].plot(x, [row["agreement"] for row in checkpoints], marker="o")
    axes[0].axhline(early["agreement"] - .05, color="firebrick", ls="--", label="-0.05 promotion threshold")
    axes[0].set(ylabel="Middle-layer top-1 agreement", xlabel="Normalized training progress")
    axes[0].legend(fontsize=8)
    axes[1].plot(x, [row["nll_damage"] for row in checkpoints], marker="o", color="darkorange")
    axes[1].set(ylabel="Deleted - intact NLL", xlabel="Normalized training progress")
    axes[2].plot(x, [row["kl"] for row in checkpoints], marker="o", color="seagreen")
    axes[2].set(ylabel="KL(intact || deleted)", xlabel="Normalized training progress")
    for axis in axes: axis.grid(alpha=.25)
    fig.suptitle("SmolLM2-360M cross-family block-deletion trajectory")
    fig.tight_layout(); fig.savefig(figure_dir / "cross_family_trajectory.png", dpi=180); plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    norm = [row["hellaswag_normalized_accuracy"] for row in checkpoints]
    raw = [row["hellaswag_raw_accuracy"] for row in checkpoints]
    axes[0].plot(x, norm, marker="o", label="normalized")
    axes[0].plot(x, raw, marker="o", label="raw")
    axes[0].axhline(CONFIG["hellaswag_normalized_accuracy_min"], color="firebrick", ls="--", label="norm gate")
    axes[0].set(xlabel="Normalized training progress", ylabel="HellaSwag accuracy"); axes[0].legend(); axes[0].grid(alpha=.25)
    positions = np.arange(len(bin_rows))
    axes[1].bar(positions - .18, [row["early_agreement"] for row in bin_rows], .36, label="early")
    axes[1].bar(positions + .18, [row["late_agreement"] for row in bin_rows], .36, label="late")
    axes[1].set(xticks=positions, xticklabels=[f"{row['low']:.2g}-{row['high']:.2g}" for row in bin_rows], xlabel="Intact confidence bin", ylabel="Agreement")
    axes[1].legend(); axes[1].grid(alpha=.25, axis="y")
    fig.suptitle("Competence and confidence control")
    fig.tight_layout(); fig.savefig(figure_dir / "competence_and_confidence.png", dpi=180); plt.close(fig)

    print(json.dumps({
        "selected_external_model_family": summary["selected_family"],
        "competence_gate": "PASS" if competence_pass else "FAIL",
        "number_of_checkpoints": len(checkpoints),
        "early_to_late_primary": [early["agreement"], late["agreement"], delta_agreement],
        "nll_damage": summary["nll_damage"], "kl": summary["kl"],
        "robustness": {"resample_deltas": resample_deltas, "bootstrap_ci": summary["primary"]["resample_bootstrap_95_ci"], "confidence_pass": criteria["confidence"]},
        "strongest_negative_evidence": summary["strongest_negative_evidence"],
        "FINAL_VERDICT": verdict,
        "recommended_next_ARC": summary["recommended_next_arc"],
    }, indent=2))


if __name__ == "__main__":
    main()
