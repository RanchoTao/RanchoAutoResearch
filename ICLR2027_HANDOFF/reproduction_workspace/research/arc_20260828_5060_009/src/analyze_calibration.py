"""Classify ARC-009 feasibility, build reports, and render blinded figures."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
BLUE = "#3F6F8F"
ORANGE = "#C96F3B"
GOLD = "#C7A64A"
INK = "#22272E"
GRID = "#D9DEE3"
PALE = "#E9EFF3"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def truth(value) -> bool:
    return str(value).strip().lower() == "true"


def relative(a: pd.Series, b: pd.Series) -> pd.Series:
    denominator = np.maximum(np.maximum(a.abs(), b.abs()), 1e-12)
    return (a - b).abs() / denominator


def ratio(a: pd.Series, b: pd.Series) -> pd.Series:
    epsilon = 1e-12
    return np.maximum((a + epsilon) / (b + epsilon), (b + epsilon) / (a + epsilon))


def style(ax) -> None:
    ax.grid(True, axis="y", color=GRID, linewidth=0.8, alpha=0.7)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(colors=INK)


def blossom(fig) -> None:
    for dx, dy in [(-0.006, 0), (0.006, 0), (0, -0.008), (0, 0.008)]:
        fig.add_artist(plt.Circle((0.975 + dx, 0.965 + dy), 0.004,
                                  transform=fig.transFigure, color=GOLD, alpha=0.8))


def save(fig, path: Path) -> None:
    blossom(fig)
    fig.savefig(path, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def markdown_table(mapping: dict) -> str:
    lines = ["| group | count |", "|---|---:|"]
    lines.extend(f"| {key} | {value} |" for key, value in mapping.items())
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--orchestration-wall-seconds", type=float, required=True)
    args = parser.parse_args()
    cfg = yaml.safe_load((ROOT / "config.yaml").read_text(encoding="utf-8"))
    raw_paths = sorted((ROOT / "raw").glob("calibration_seed*.csv"))
    meta_paths = sorted((ROOT / "raw").glob("calibration_seed*.json"))
    manifest_paths = sorted((ROOT / "raw").glob("alpha_manifest_seed*.csv"))
    if len(raw_paths) != 5 or len(meta_paths) != 5 or len(manifest_paths) != 5:
        raise SystemExit("LOCAL_ARTIFACT_MISSING: expected five calibration result sets")
    data = pd.concat([pd.read_csv(path) for path in raw_paths], ignore_index=True)
    targets = pd.read_csv(ROOT / "sanitized_targets.csv")
    manifest = pd.concat([pd.read_csv(path) for path in manifest_paths], ignore_index=True)
    if len(data) != 103 or data.target_id.nunique() != 103:
        raise SystemExit("LOCAL_ARTIFACT_MISSING: calibration universe is not 103 unique cells")
    if set(data.target_id) != set(targets.target_id):
        raise SystemExit("BLINDING_FAILURE: calibrated cell IDs differ from sanitized universe")
    if len(manifest) != 412:
        raise SystemExit("LOCAL_ARTIFACT_MISSING: expected four root records per cell")

    forbidden = {"d_s", "ds", "flips", "residual", "reversal", "top1_flip"}
    for frame_name, frame in (("calibration", data), ("manifest", manifest), ("targets", targets)):
        collision = forbidden.intersection({str(column).lower() for column in frame.columns})
        if collision:
            raise SystemExit(f"BLINDING_FAILURE: {frame_name} has forbidden columns {sorted(collision)}")

    numeric = data.select_dtypes(include=[np.number])
    if not np.isfinite(numeric.to_numpy()).all():
        raise SystemExit("ALPHA-NUMERICALLY-UNSTABLE: nonfinite saved calibration value")
    if not ((data.block_alpha >= data.alpha_min) & (data.block_alpha <= data.alpha_max)
            & (data.noise_alpha >= data.alpha_min) & (data.noise_alpha <= data.alpha_max)).all():
        raise SystemExit("BLINDING_FAILURE: selected alpha escaped preregistered range")

    calipers = cfg["pair_calipers"]
    relaxed = cfg["pass_b_relaxed_secondary"]
    data["relative_kl_difference"] = relative(data.block_kl, data.noise_kl)
    data["relative_nll_difference"] = relative(data.block_nll_damage, data.noise_nll_damage)
    data["hidden_norm_ratio"] = ratio(data.block_hidden_relative_norm, data.noise_hidden_relative_norm)
    data["output_norm_ratio"] = ratio(data.block_output_logit_norm, data.noise_output_logit_norm)
    data["absolute_cosine_difference"] = (data.block_output_abs_cosine - data.noise_output_abs_cosine).abs()
    data["pass_kl"] = data.relative_kl_difference <= calipers["relative_kl_difference"]
    data["pass_nll"] = data.relative_nll_difference <= calipers["relative_nll_difference"]
    data["pass_hidden_norm"] = data.hidden_norm_ratio <= calipers["hidden_norm_ratio"]
    data["pass_output_norm"] = data.output_norm_ratio <= calipers["output_norm_ratio"]
    data["pass_abs_cosine"] = data.absolute_cosine_difference <= calipers["absolute_cosine_difference"]
    data["block_target_kl_log_error"] = np.abs(np.log(np.maximum(data.block_kl, 1e-12) / data.target_kl))
    data["noise_target_kl_log_error"] = np.abs(np.log(np.maximum(data.noise_kl, 1e-12) / data.target_kl))
    data["block_target_nll_log_error"] = np.abs(np.log(np.maximum(data.block_nll_damage, 1e-12) / data.target_nll_damage))
    data["noise_target_nll_log_error"] = np.abs(np.log(np.maximum(data.noise_nll_damage, 1e-12) / data.target_nll_damage))
    data["mean_target_log_error"] = data[[
        "block_target_kl_log_error", "noise_target_kl_log_error",
        "block_target_nll_log_error", "noise_target_nll_log_error",
    ]].mean(axis=1)

    classes = []
    for row in data.itertuples():
        if truth(row.numerical_issue):
            classes.append("FAIL-NUMERICAL")
            continue
        if truth(row.no_bracket):
            classes.append("FAIL-NO-BRACKET")
            continue
        if truth(row.pathological):
            classes.append("FAIL-PATHOLOGICAL")
            continue
        primary = [row.pass_kl, row.pass_nll, row.pass_hidden_norm,
                   row.pass_output_norm, row.pass_abs_cosine]
        if all(primary):
            classes.append("PASS-A")
            continue
        secondary_strict = [row.pass_hidden_norm, row.pass_output_norm, row.pass_abs_cosine]
        secondary_relaxed = [
            row.hidden_norm_ratio <= relaxed["hidden_norm_ratio"],
            row.output_norm_ratio <= relaxed["output_norm_ratio"],
            row.absolute_cosine_difference <= relaxed["absolute_cosine_difference"],
        ]
        if row.pass_kl and row.pass_nll and secondary_strict.count(False) == 1 and all(secondary_relaxed):
            classes.append("PASS-B")
        else:
            classes.append("FAIL-TRADEOFF")
    data["calibration_class"] = classes

    # Outcome-blind damage strata are frozen empirical terciles of target KL.
    data["damage_regime"] = pd.qcut(data.target_kl, q=3, labels=["low", "mid", "high"])
    counts = data.calibration_class.value_counts().to_dict()
    pass_a = data[data.calibration_class.eq("PASS-A")]
    by_run = pass_a.groupby("run_id").size().reindex(cfg["run_ids"], fill_value=0).astype(int)
    by_step = pass_a.groupby("step").size().reindex(cfg["checkpoint_steps"], fill_value=0).astype(int)
    by_layer = pass_a.groupby("layer").size().reindex(range(1, 11), fill_value=0).astype(int)
    by_damage = pass_a.groupby("damage_regime", observed=False).size().astype(int)
    n_pass = len(pass_a)
    run_shares = by_run / max(n_pass, 1)
    step_shares = by_step / max(n_pass, 1)
    coverage = cfg["coverage"]
    coverage_pass = bool(
        by_run.min() >= coverage["meaningful_per_run"]
        and by_step.min() >= coverage["meaningful_per_checkpoint"]
        and run_shares.max() <= coverage["maximum_run_share"]
        and step_shares.max() <= coverage["maximum_checkpoint_share"]
    )
    numerical_count = int((data.calibration_class == "FAIL-NUMERICAL").sum())
    numerical_rate = numerical_count / len(data)
    failure_counts = data[data.calibration_class.str.startswith("FAIL")].calibration_class.value_counts()
    primarily_numerical = bool(
        numerical_count >= math.ceil(len(data) / 2)
        and (failure_counts.empty or numerical_count == failure_counts.max())
    )
    thresholds = cfg["feasibility"]
    if primarily_numerical:
        verdict = "ALPHA-NUMERICALLY-UNSTABLE"
    elif n_pass < thresholds["moderate_pass_a"] or not coverage_pass:
        verdict = "ALPHA-NOT-FEASIBLE"
    elif (n_pass >= thresholds["strong_pass_a"]
          and numerical_rate <= thresholds["maximum_numerical_failure_rate"]):
        verdict = "ALPHA-FEASIBLE"
    else:
        verdict = "ALPHA-BORDERLINE"

    support_gain = n_pass - 15
    relative_gain = n_pass / 15 - 1
    data.sort_values(["run_id", "step", "layer", "target_id"]).to_csv(
        ROOT / "calibration_results.csv", index=False
    )
    manifest.sort_values(["run_id", "step", "layer", "target_id", "family", "target_metric"]).to_csv(
        ROOT / "alpha_search_manifest.csv", index=False
    )

    meta = [json.loads(path.read_text(encoding="utf-8")) for path in meta_paths]
    resource = {
        "orchestration_wall_seconds": args.orchestration_wall_seconds,
        "summed_calibration_process_wall_seconds": sum(item["wall_seconds"] for item in meta),
        "summed_cpu_seconds": sum(item["cpu_seconds"] for item in meta),
        "gpu_session_seconds": sum(item["wall_seconds"] for item in meta),
        "peak_cuda_bytes": max(item["peak_cuda_bytes"] for item in meta),
        "peak_working_set_bytes": None,
        "peak_working_set_note": "Windows peak-working-set probe returned unavailable in all isolated model processes.",
        "network_bytes_caused": 0,
        "network_basis": "offline environment, local_files_only model/tokenizer loads, no network-capable code path",
        "api_cost_usd": 0,
        "external_compute_cost_usd": 0,
        "downloads": 0,
    }
    summary = {
        "arc": cfg["arc"], "outcome_blind": True, "cells": len(data),
        "counts": {str(key): int(value) for key, value in counts.items()},
        "pass_a": n_pass, "pass_b": int((data.calibration_class == "PASS-B").sum()),
        "arc008_support": 15, "support_gain": support_gain,
        "relative_support_increase": relative_gain,
        "by_run": {str(key): int(value) for key, value in by_run.items()},
        "by_step": {str(key): int(value) for key, value in by_step.items()},
        "by_layer": {str(key): int(value) for key, value in by_layer.items()},
        "by_damage_regime": {str(key): int(value) for key, value in by_damage.items()},
        "maximum_run_share": float(run_shares.max()),
        "maximum_checkpoint_share": float(step_shares.max()),
        "coverage_pass": coverage_pass, "numerical_failure_rate": numerical_rate,
        "boundary_selected": int(data.boundary_selected.map(truth).sum()),
        "median_mean_target_log_error": float(data.mean_target_log_error.median()),
        "median_relative_kl_difference": float(data.relative_kl_difference.median()),
        "median_relative_nll_difference": float(data.relative_nll_difference.median()),
        "median_hidden_norm_ratio": float(data.hidden_norm_ratio.median()),
        "median_output_norm_ratio": float(data.output_norm_ratio.median()),
        "median_absolute_cosine_difference": float(data.absolute_cosine_difference.median()),
        "verdict": verdict, "resource": resource,
    }
    (ROOT / "feasibility_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    figures = ROOT / "figures"
    figures.mkdir(exist_ok=True)
    order = ["PASS-A", "PASS-B", "FAIL-NO-BRACKET", "FAIL-TRADEOFF", "FAIL-NUMERICAL", "FAIL-PATHOLOGICAL"]
    values = [counts.get(label, 0) for label in order]
    fig, ax = plt.subplots(figsize=(9.2, 4.8))
    colors = [BLUE, ORANGE] + ["#AEB8C2"] * 4
    bars = ax.bar(order, values, color=colors, edgecolor=INK, linewidth=0.6)
    ax.bar_label(bars, padding=3, color=INK)
    ax.set_title("ARC-009 calibration classes", loc="left", color=INK, fontweight="bold")
    ax.set_ylabel("Cells (N=103)")
    ax.tick_params(axis="x", rotation=22)
    style(ax)
    save(fig, figures / "fig1_calibration_classes.png")

    fig, axes = plt.subplots(1, 3, figsize=(12.5, 4.5))
    axes[0].hist(data.block_alpha_multiplier, bins=14, color=BLUE, alpha=0.75, edgecolor=INK, label="block")
    axes[0].hist(data.noise_alpha_multiplier, bins=14, histtype="step", color=ORANGE, linewidth=2, label="noise")
    axes[0].set_title("Selected alpha / beta", loc="left", fontweight="bold")
    axes[0].set_xlabel("Multiplier")
    axes[0].legend(frameon=False)
    axes[1].hist(data.mean_target_log_error, bins=15, color=BLUE, edgecolor=INK)
    axes[1].set_title("Frozen target mismatch", loc="left", fontweight="bold")
    axes[1].set_xlabel("Mean absolute log error")
    axes[2].hist(data.objective, bins=15, color=ORANGE, edgecolor=INK)
    axes[2].set_title("Joint calibration objective", loc="left", fontweight="bold")
    axes[2].set_xlabel("Objective")
    for ax in axes:
        style(ax)
    fig.suptitle("Alpha solutions and mismatch distributions (103 blinded cells)", x=0.02, ha="left", color=INK)
    fig.tight_layout()
    save(fig, figures / "fig2_alpha_and_mismatch.png")

    fig, axes = plt.subplots(1, 3, figsize=(12.5, 4.4))
    for ax, series, title in (
        (axes[0], by_run, "PASS-A by seed"),
        (axes[1], by_step, "PASS-A by checkpoint"),
        (axes[2], by_layer, "PASS-A by layer"),
    ):
        bars = ax.bar([str(value) for value in series.index], series.values, color=BLUE, edgecolor=INK, linewidth=0.5)
        ax.bar_label(bars, padding=2, fontsize=8)
        ax.set_title(title, loc="left", fontweight="bold")
        ax.set_ylabel("Cells")
        style(ax)
    fig.suptitle("PASS-A coverage across frozen strata", x=0.02, ha="left", color=INK)
    fig.tight_layout()
    save(fig, figures / "fig3_coverage.png")

    failures = data[data.calibration_class.str.startswith("FAIL")].calibration_class.value_counts().sort_values()
    fig, ax = plt.subplots(figsize=(8.4, 4.4))
    if len(failures):
        bars = ax.barh(failures.index, failures.values, color="#AEB8C2", edgecolor=INK)
        ax.bar_label(bars, padding=3)
    else:
        ax.text(0.5, 0.5, "No failed cells", ha="center", va="center", transform=ax.transAxes, color=INK)
    ax.set_title("Failure-mode distribution", loc="left", color=INK, fontweight="bold")
    ax.set_xlabel("Cells")
    ax.grid(True, axis="x", color=GRID, alpha=0.7)
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, figures / "fig4_failure_modes.png")

    failure_md = f"""# Failure modes

The frozen priority classification produced:

{markdown_table({key: counts.get(key, 0) for key in order})}

No failed cell was dropped. `FAIL-NO-BRACKET` means at least one frozen target
was unreachable inside `[0.125 beta, 2 beta]`; `FAIL-TRADEOFF` means roots were
numerically available but the unchanged joint damage/geometry conditions could
not all be met. Numerical and pathological failures are reported separately.
"""
    (ROOT / "failure_modes.md").write_text(failure_md, encoding="utf-8")

    coverage_md = f"""# Coverage analysis

PASS-A support is **{n_pass}/103**. Frozen coverage gate: **{'PASS' if coverage_pass else 'FAIL'}**.

## By seed

{markdown_table({str(key): int(value) for key, value in by_run.items()})}

## By checkpoint

{markdown_table({str(key): int(value) for key, value in by_step.items()})}

## By layer

{markdown_table({str(key): int(value) for key, value in by_layer.items()})}

## Concentration

- Maximum seed share: {run_shares.max():.3f} (frozen maximum 0.35).
- Maximum checkpoint share: {step_shares.max():.3f} (frozen maximum 0.65).
- Damage-regime PASS-A counts: {', '.join(f'{key}={int(value)}' for key, value in by_damage.items())}.

Damage regimes are outcome-blind terciles of frozen target KL. They are
descriptive and did not alter cell selection or the verdict.
"""
    (ROOT / "coverage_analysis.md").write_text(coverage_md, encoding="utf-8")

    resource_md = f"""# Resource usage

- Orchestration wall time: {args.orchestration_wall_seconds:.3f} s.
- Summed isolated calibration-process wall time: {resource['summed_calibration_process_wall_seconds']:.3f} s.
- Summed CPU time: {resource['summed_cpu_seconds']:.3f} s.
- GPU session time (model processes resident/executing): {resource['gpu_session_seconds']:.3f} s.
- Peak allocated VRAM: {resource['peak_cuda_bytes'] / 2**30:.3f} GiB.
- Peak RAM: not captured; the Windows peak-working-set probe returned unavailable.
- ARC-caused network: 0 bytes by construction (offline variables plus `local_files_only=True`).
- Downloads: 0.
- API cost: USD 0.
- External compute cost: USD 0.

Disk written is finalized after reports, figures, validation, and the integrity
seal are generated.
"""
    (ROOT / "resource_usage.md").write_text(resource_md, encoding="utf-8")

    interpretation = {
        "ALPHA-FEASIBLE": "A separately preregistered direction-swap causal reveal is adequately supported, but no outcome is revealed here.",
        "ALPHA-BORDERLINE": "Support may justify one final causal reveal only after explicit human judgment; criteria must remain unchanged.",
        "ALPHA-NOT-FEASIBLE": "Continuous alpha did not identify broad causal support under the current assay; terminate this internal-direction branch.",
        "ALPHA-NUMERICALLY-UNSTABLE": "The solver, rather than target compatibility, prevented an identification conclusion.",
    }[verdict]
    report = f"""# ARC-009 feasibility report

## Question

Can continuous/high-resolution alpha calibration make the frozen internal
direction counterfactual broadly identifiable without accessing `D_S`?

## Result

- PASS-A: **{n_pass}/103**.
- PASS-B (descriptive): **{int((data.calibration_class == 'PASS-B').sum())}/103**.
- ARC-008 strict support: 15/103.
- Absolute support gain: **{support_gain:+d} cells**.
- Relative support increase: **{relative_gain * 100:.1f}%**.
- Coverage gate: **{'PASS' if coverage_pass else 'FAIL'}**.
- Numerical-failure rate: {numerical_rate:.1%}.
- Boundary selections: {int(data.boundary_selected.map(truth).sum())}/103.

Median diagnostic values were: target log-error {data.mean_target_log_error.median():.4f},
block/noise KL imbalance {data.relative_kl_difference.median():.1%}, NLL imbalance
{data.relative_nll_difference.median():.1%}, hidden-norm ratio
{data.hidden_norm_ratio.median():.3f}, output-norm ratio
{data.output_norm_ratio.median():.3f}, and alignment difference
{data.absolute_cosine_difference.median():.4f}.

## Interpretation

{interpretation}

This is only an identification-feasibility result. It is not evidence that
direction changes `D_S`, and no causal effect was estimated.

## Final verdict

**{verdict}**
"""
    (ROOT / "feasibility_report.md").write_text(report, encoding="utf-8")

    if verdict == "ALPHA-FEASIBLE":
        recommendation = "Preregister a final direction-swap causal reveal ARC using the frozen successful PASS-A cells and frozen alpha solutions. Do not execute it automatically."
    elif verdict == "ALPHA-BORDERLINE":
        recommendation = "Do not change calibration criteria. Human judgment is required on whether the expected information gain justifies one final causal reveal."
    elif verdict == "ALPHA-NOT-FEASIBLE":
        recommendation = "Stop the internal-direction mechanism branch. Begin paper consolidation around validated phenomenon, mechanism falsifications, family dependence, and identified limitations."
    else:
        recommendation = "Stop. Diagnose the frozen solver instability without revealing outcomes; do not launch a causal ARC."
    (ROOT / "next_arc_recommendation.md").write_text(
        f"# Next ARC recommendation\n\n{recommendation}\n", encoding="utf-8"
    )
    executive = f"""# ARC-009 executive summary

1. Purpose: test continuous-alpha identification feasibility only.
2. Blinding: preserved; no outcome column was loaded or emitted.
3. Universe: 103/103 frozen Class A cells.
4. PASS-A: **{n_pass}/103**; PASS-B: **{int((data.calibration_class == 'PASS-B').sum())}/103**.
5. Support gain over ARC-008: **{support_gain:+d} cells** ({relative_gain * 100:+.1f}%).
6. Coverage: {'adequate' if coverage_pass else 'inadequate'} across all runs/checkpoints.
7. Failures: {', '.join(f'{key}={int(value)}' for key, value in failure_counts.items()) if len(failure_counts) else 'none'}.
8. Numerical stability: {numerical_count}/103 numerical failures.
9. No `D_S` was revealed and no causal effect was estimated.
10. FINAL VERDICT: **{verdict}**.
11. Recommended action: {recommendation}
"""
    (ROOT / "EXECUTIVE_SUMMARY.md").write_text(executive, encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

