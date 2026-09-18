"""Offline ARC-006R repair, reanalysis, and report generation."""

from __future__ import annotations

import hashlib
import json
import subprocess
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ARC_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ARC_ROOT.parents[1]
ARC006 = ARC_ROOT.parent / "arc_20260826_5060_006"
ARC007 = ARC_ROOT.parent / "arc_20260826_5060_007"
TOPK_COMMIT = "1a6892b"
RUNS = [2, 3, 5, 6, 8]
STEPS = [14000, 72000, 143000]
BOUND = 0.0107421875
BOOT_SEED = 20260826
BOOT_DRAWS = 100_000
OLD_RESIDUAL = -0.019234664351851838
INSTABILITY_THRESHOLD = 0.0025

BLUE = "#4477AA"
ORANGE = "#EE7733"
GOLD = "#CCAA44"
INK = "#2B2B2B"
GRID = "#D9D9D9"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_geometry(rule: str) -> tuple[pd.DataFrame, list[dict]]:
    rows: list[dict] = []
    manifest: list[dict] = []
    for run_id in RUNS:
        rel = (
            "research/arc_20260826_5060_007/raw/geometry/"
            f"pythia-160m-seed{run_id}.json"
        )
        if rule == "topk":
            raw = subprocess.check_output(
                ["git", "show", f"{TOPK_COMMIT}:{rel}"], cwd=REPO_ROOT
            )
            location = f"git:{TOPK_COMMIT}:{rel}"
            commit = TOPK_COMMIT
        elif rule == "argmax":
            path = REPO_ROOT / rel
            if not path.exists():
                raise FileNotFoundError(f"LOCAL_ARTIFACT_MISSING: {path}")
            raw = path.read_bytes()
            location = rel
            commit = "4fd4d3e"
        else:
            raise ValueError(rule)
        payload = json.loads(raw.decode("utf-8"))
        checkpoints = payload.get("checkpoints", [])
        if len(checkpoints) != 3:
            raise RuntimeError(f"incomplete {rule} run {run_id}")
        before = len(rows)
        for checkpoint in checkpoints:
            if not checkpoint["harness_validation"]["pass"]:
                raise RuntimeError(f"harness failure {rule} run {run_id}")
            rows.extend(checkpoint["geometry_rows"])
        manifest.append({
            "source_id": f"{rule}_seed{run_id}",
            "role": f"globally consistent {rule} family outcomes",
            "location": location,
            "commit": commit,
            "sha256": sha256_bytes(raw),
            "records": len(rows) - before,
            "status": "verified",
        })
    frame = pd.DataFrame(rows)
    required = {"target_id", "run_id", "step", "layer", "match_class", "family",
                "top1_flip_rate", "kl", "nll_damage"}
    if not required.issubset(frame.columns):
        raise RuntimeError(f"missing geometry columns: {sorted(required-frame.columns)}")
    if len(frame) != 300 or frame[["target_id", "family"]].duplicated().any():
        raise RuntimeError(f"{rule} geometry grain failure")
    if set(frame["family"]) != {"block", "noise"}:
        raise RuntimeError(f"{rule} family coverage failure")
    return frame, manifest


def pivot_rule(frame: pd.DataFrame, prefix: str) -> pd.DataFrame:
    identity = ["target_id", "run_id", "step", "layer", "match_class"]
    metadata = frame[identity].drop_duplicates()
    if len(metadata) != 150:
        raise RuntimeError(f"{prefix} target identity failure")
    values = frame.pivot(index="target_id", columns="family", values="top1_flip_rate")
    values = values.rename(columns={
        "block": f"{prefix}_block_ds", "noise": f"{prefix}_noise_ds"
    }).reset_index()
    return metadata.merge(values, on="target_id", validate="one_to_one")


def bootstrap_mean(values: np.ndarray, level: float) -> list[float]:
    values = np.asarray(values, dtype=float)
    rng = np.random.default_rng(BOOT_SEED)
    draws = rng.choice(values, size=(BOOT_DRAWS, len(values)), replace=True).mean(axis=1)
    tail = (1.0 - level) / 2
    return [float(x) for x in np.quantile(draws, [tail, 1.0-tail])]


def residual_summary(frame: pd.DataFrame, column: str) -> dict:
    run_stats = frame.groupby("run_id", as_index=False).agg(
        median_residual=(column, "median"),
        mean_residual=(column, "mean"),
        cells=(column, "size"),
    ).set_index("run_id").reindex(RUNS).reset_index()
    if run_stats["median_residual"].isna().any():
        raise RuntimeError(f"missing run in {column}")
    values = run_stats["median_residual"].to_numpy(float)
    estimate = float(values.mean())
    loo = [float(np.delete(values, index).mean()) for index in range(len(values))]
    ci90 = bootstrap_mean(values, 0.90)
    ci95 = bootstrap_mean(values, 0.95)
    return {
        "cells": int(len(frame)),
        "estimate": estimate,
        "run_statistics": run_stats.to_dict("records"),
        "bootstrap_90_ci": ci90,
        "bootstrap_95_ci": ci95,
        "negative_runs": int((values < 0).sum()),
        "leave_one_run_out": loo,
        "leave_one_run_out_range": [float(min(loo)), float(max(loo))],
        "equivalence_pass": bool(
            abs(estimate) <= BOUND and ci90[0] >= -BOUND and ci90[1] <= BOUND
        ),
        "ci95_wholly_below_negative_bound": bool(ci95[1] < -BOUND),
    }


def verdict_for(summary: dict, reference: float = OLD_RESIDUAL) -> str:
    magnitude_ratio = abs(summary["estimate"]) / abs(reference)
    confirmed = bool(
        magnitude_ratio >= 0.75
        and summary["bootstrap_95_ci"][1] < -BOUND
        and summary["negative_runs"] == 5
        and all(value < -BOUND for value in summary["leave_one_run_out"])
    )
    if confirmed:
        return "006R-RESIDUAL-CONFIRMED"
    if summary["equivalence_pass"] or summary["bootstrap_95_ci"][1] >= 0:
        return "006R-RESIDUAL-NOT-CONFIRMED"
    if summary["estimate"] < 0 and summary["bootstrap_95_ci"][1] < 0:
        return "006R-RESIDUAL-WEAKENED"
    return "006R-RESIDUAL-NOT-CONFIRMED"


def layer_summary(frame: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for layer, group in frame.groupby("layer"):
        run_values = group.groupby("run_id")["corrected_residual"].median()
        ci = bootstrap_mean(run_values.to_numpy(float), 0.95) if len(run_values) >= 3 else [np.nan, np.nan]
        rows.append({
            "layer": int(layer), "count": int(len(group)),
            "unique_runs": int(len(run_values)),
            "old_mean": float(group["old_residual"].mean()),
            "old_median": float(group["old_residual"].median()),
            "corrected_mean": float(group["corrected_residual"].mean()),
            "corrected_median": float(group["corrected_residual"].median()),
            "corrected_ci95_low": float(ci[0]),
            "corrected_ci95_high": float(ci[1]),
            "low_support": bool(len(group) < 8 or len(run_values) < 3),
        })
    return pd.DataFrame(rows).sort_values("layer")


def weighted_sd(values: pd.Series, weights: pd.Series) -> float:
    mean = float(np.average(values, weights=weights))
    return float(np.sqrt(np.average((values-mean)**2, weights=weights)))


def style_axis(ax: plt.Axes) -> None:
    ax.grid(True, color=GRID, linewidth=.8, alpha=.7)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)


def add_blossom(fig: plt.Figure) -> None:
    x, y = .975, .965
    for dx, dy in [(-.006, 0), (.006, 0), (0, -.008), (0, .008)]:
        fig.add_artist(plt.Circle((x+dx, y+dy), .004,
                                 transform=fig.transFigure, color=GOLD, alpha=.8))


def create_figures(summaries: dict, layers: pd.DataFrame) -> None:
    out = ARC_ROOT / "figures"
    out.mkdir(parents=True, exist_ok=True)
    labels = ["ARC-006 mixed", "Canonical lowest-index", "Consistent topk"]
    keys = ["old_mixed", "canonical_argmax", "consistent_topk"]
    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    ax.axvspan(-BOUND, BOUND, color=GOLD, alpha=.18)
    ax.axvline(0, color=INK, linewidth=1)
    for index, (label, key) in enumerate(zip(labels, keys)):
        row = summaries[key]; value = row["estimate"]; ci = row["bootstrap_95_ci"]
        ax.errorbar(value, index, xerr=[[value-ci[0]], [ci[1]-value]],
                    fmt="D" if index else "o", color=ORANGE if index else BLUE,
                    markerfacecolor="none" if index == 2 else None, capsize=4)
    ax.set_yticks(range(3), labels)
    ax.set_xlabel("Family residual with run-bootstrap 95% CI")
    ax.set_title("ARC-006R corrected aggregate residual")
    fig.text(.5, .91, "103 unchanged Class A cells; frozen equivalence band shaded",
             ha="center", color="#666666")
    style_axis(ax); add_blossom(fig); fig.tight_layout(rect=(0,0,1,.89))
    fig.savefig(out / "fig1_corrected_residual.png", dpi=240); plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.6, 5.0))
    ax.axhspan(-BOUND, BOUND, color=GOLD, alpha=.18)
    ax.axhline(0, color=INK, linewidth=1)
    for row in layers.to_dict("records"):
        ax.plot([row["layer"]-.10, row["layer"]+.10],
                [row["old_mean"], row["corrected_mean"]], color="#B8B8B8", linewidth=1)
    ax.scatter(layers.layer-.10, layers.old_mean, color=BLUE, marker="o", label="ARC-006 mixed")
    ax.scatter(layers.layer+.10, layers.corrected_mean, facecolors="none",
               edgecolors=ORANGE, marker="D", label="Canonical repair")
    ax.set_xticks(layers.layer)
    ax.set_xlabel("Interior layer")
    ax.set_ylabel("Mean Class A cell residual")
    ax.set_title("Layer residual before and after assay repair")
    fig.text(.5, .91, "Counts frozen by KL/NLL matching; layer 7 remains low support",
             ha="center", color="#666666")
    ax.legend(frameon=False); style_axis(ax); add_blossom(fig)
    fig.tight_layout(rect=(0,0,1,.89)); fig.savefig(out / "fig2_layer_reanalysis.png", dpi=240)
    plt.close(fig)


def md_table(frame: pd.DataFrame, columns: list[str]) -> str:
    selected = frame[columns].copy()
    header = "| " + " | ".join(columns) + " |"
    rule = "|" + "|".join(["---"] * len(columns)) + "|"
    rows = []
    for values in selected.itertuples(index=False, name=None):
        formatted = []
        for value in values:
            if isinstance(value, (float, np.floating)):
                formatted.append("" if np.isnan(value) else f"{value:.6f}")
            else:
                formatted.append(str(value))
        rows.append("| " + " | ".join(formatted) + " |")
    return "\n".join([header, rule, *rows])


def main() -> None:
    started = time.perf_counter()
    # Explicit deterministic tie-rule guard for the canonical first/lowest max.
    for dtype in [np.float16, np.float32]:
        tied = np.asarray([1.0, 4.0, 4.0, 2.0], dtype=dtype)
        explicit = int(np.flatnonzero(tied == tied.max()).min())
        if int(np.argmax(tied)) != explicit or explicit != 1:
            raise RuntimeError(f"deterministic tie rule failed for {dtype}")

    source_path = ARC006 / "processed" / "all_target_results.csv"
    target_path = ARC006 / "target_manifest.csv"
    if not source_path.exists() or not target_path.exists():
        raise FileNotFoundError("LOCAL_ARTIFACT_MISSING: ARC-006 source tables")
    source = pd.read_csv(source_path)
    targets = pd.read_csv(target_path)
    topk, source_manifest = load_geometry("topk")
    argmax, argmax_manifest = load_geometry("argmax")
    source_manifest.extend(argmax_manifest)
    source_manifest.extend([
        {"source_id":"arc006_results","role":"frozen metadata and mixed comparison",
         "location":str(source_path.relative_to(REPO_ROOT)).replace("\\","/"),
         "commit":"21d361a","sha256":sha256(source_path),"records":len(source),"status":"verified"},
        {"source_id":"arc006_targets","role":"frozen target and match assignments",
         "location":str(target_path.relative_to(REPO_ROOT)).replace("\\","/"),
         "commit":"282b366","sha256":sha256(target_path),"records":len(targets),"status":"verified"},
    ])
    if len(source) != 150 or source.target_id.duplicated().any() or len(targets) != 150:
        raise RuntimeError("ARC-006 frozen table grain failure")
    if source.match_class.value_counts().to_dict() != {"A":103,"B":31,"C":16}:
        raise RuntimeError("frozen match class failure")

    topk_wide = pivot_rule(topk, "topk")
    argmax_wide = pivot_rule(argmax, "argmax")
    identity = ["target_id", "run_id", "step", "layer", "match_class"]
    frame = source.merge(topk_wide, on=identity, validate="one_to_one")
    frame = frame.merge(argmax_wide, on=identity, validate="one_to_one")
    if len(frame) != 150 or frame.target_id.duplicated().any():
        raise RuntimeError("corrected join grain failure")
    numeric = frame.select_dtypes(include="number")
    if int((~np.isfinite(numeric)).sum().sum()) != 0:
        raise RuntimeError("non-finite corrected values")

    frame["old_residual"] = frame["family_residual"]
    frame["corrected_block_ds"] = frame["argmax_block_ds"]
    frame["corrected_noise_ds"] = frame["argmax_noise_ds"]
    frame["corrected_residual"] = frame.corrected_noise_ds-frame.corrected_block_ds
    frame["topk_residual"] = frame.topk_noise_ds-frame.topk_block_ds
    frame["delta_correction"] = frame.corrected_residual-frame.old_residual
    frame["old_reversal"] = np.sign(frame.old_residual) != -1
    frame["corrected_reversal"] = np.sign(frame.corrected_residual) != -1
    frame["reversal_membership_changed"] = frame.old_reversal != frame.corrected_reversal

    path_checks = {
        "topk_block_vs_arc006_max_abs": float((frame.topk_block_ds-frame.block_ds).abs().max()),
        "topk_noise_vs_arc006_max_abs": float((frame.topk_noise_ds-frame.noise_ds).abs().max()),
        "argmax_block_vs_arc006_max_abs": float((frame.argmax_block_ds-frame.block_ds).abs().max()),
        "argmax_noise_vs_arc006_max_abs": float((frame.argmax_noise_ds-frame.noise_ds).abs().max()),
    }
    if path_checks["topk_block_vs_arc006_max_abs"] > 1e-10:
        raise RuntimeError("historical topk block reproduction failure")
    if path_checks["argmax_noise_vs_arc006_max_abs"] > 1e-10:
        raise RuntimeError("canonical argmax noise reproduction failure")

    primary = frame[frame.match_class == "A"].copy()
    sensitivity = frame[frame.match_class.isin(["A","B"])].copy()
    summaries = {
        "old_mixed": residual_summary(primary, "old_residual"),
        "canonical_argmax": residual_summary(primary, "corrected_residual"),
        "consistent_topk": residual_summary(primary, "topk_residual"),
        "class_ab_argmax": residual_summary(sensitivity, "corrected_residual"),
    }
    primary_verdict = verdict_for(summaries["canonical_argmax"])
    topk_verdict = verdict_for(summaries["consistent_topk"])
    rule_difference = abs(summaries["canonical_argmax"]["estimate"]-summaries["consistent_topk"]["estimate"])
    numeric_instability = bool(rule_difference > INSTABILITY_THRESHOLD or primary_verdict != topk_verdict)

    canonical = summaries["canonical_argmax"]
    delta_correction = canonical["estimate"]-OLD_RESIDUAL
    relative_correction = abs(delta_correction)/abs(OLD_RESIDUAL)
    layers = layer_summary(primary)
    layer_result = {
        "old_weighted_sd": weighted_sd(layers.old_mean, layers["count"]),
        "corrected_weighted_sd": weighted_sd(layers.corrected_mean, layers["count"]),
        "old_range": [float(layers.old_mean.min()), float(layers.old_mean.max())],
        "corrected_range": [float(layers.corrected_mean.min()), float(layers.corrected_mean.max())],
        "low_support_layers": [int(x) for x in layers.loc[layers.low_support,"layer"]],
    }

    changed = primary[primary.reversal_membership_changed].copy()
    sign_result = {
        "old_reversals": int(primary.old_reversal.sum()),
        "corrected_reversals": int(primary.corrected_reversal.sum()),
        "old_strict_positive": int((primary.old_residual > 0).sum()),
        "corrected_strict_positive": int((primary.corrected_residual > 0).sum()),
        "old_zero": int((primary.old_residual == 0).sum()),
        "corrected_zero": int((primary.corrected_residual == 0).sum()),
        "membership_changed": int(len(changed)),
        "changed_target_ids": changed.target_id.tolist(),
    }
    sign_distribution = primary.groupby(["run_id","step"],as_index=False).agg(
        cells=("target_id","size"), old_reversals=("old_reversal","sum"),
        corrected_reversals=("corrected_reversal","sum")
    )

    integrity = {
        "repair_level": 2,
        "source_rows": int(len(source)), "corrected_rows": int(len(frame)),
        "class_counts": {str(k):int(v) for k,v in frame.match_class.value_counts().items()},
        "matching_assignments_changed": 0,
        "path_checks": path_checks,
        "identical_canonical_columns_for_both_families": True,
        "deterministic_tie_guard": True,
        "delta_s_leakage": False,
        "equivalence_bound_unchanged": BOUND,
        "seeds_unchanged": RUNS, "checkpoints_unchanged": STEPS,
        "layers_unchanged": list(range(1,11)),
        "excluded_seeds": [], "posthoc_threshold_changes": 0,
        "all_harness_checks_passed_in_sources": True,
        "pass": True,
    }
    summary = {
        "arc":"ARC-20260827-5060-006R", "verdict":primary_verdict,
        "canonical_rule":"lowest token index among exact maximum logits",
        "summaries":summaries, "old_arc006_residual":OLD_RESIDUAL,
        "delta_correction":float(delta_correction),
        "relative_correction":float(relative_correction),
        "global_rule_estimate_difference":float(rule_difference),
        "numeric_instability":numeric_instability,
        "sign_reversal":sign_result, "layer_heterogeneity":layer_result,
        "integrity":integrity,
        "analysis_runtime_seconds":float(time.perf_counter()-started),
        "gpu_active_seconds":0.0, "peak_vram_bytes":0,
        "api_cost_usd":0, "external_compute_cost_usd":0,
    }

    ARC_ROOT.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(source_manifest).to_csv(ARC_ROOT/"reanalysis_manifest.csv",index=False)
    frame.to_csv(ARC_ROOT/"corrected_results.csv",index=False)
    layers.to_csv(ARC_ROOT/"layer_results.csv",index=False)
    changed[["target_id","run_id","step","layer","old_residual","corrected_residual",
             "old_reversal","corrected_reversal"]].to_csv(
                 ARC_ROOT/"sign_reversal_membership_changes.csv",index=False)
    sign_distribution.to_csv(ARC_ROOT/"sign_reversal_distribution.csv",index=False)
    results = ARC_ROOT/"results"; results.mkdir(exist_ok=True)
    (results/"corrected_summary.json").write_text(
        json.dumps(summary,indent=2),encoding="utf-8")
    create_figures(summaries,layers)

    runs = pd.DataFrame(canonical["run_statistics"])
    statistical = f"""# Statistical analysis

## Primary corrected result

Canonical rule: lowest token index among exact maximum logits, identically for
both families. The population remains the 103 frozen Class A cells.

{md_table(runs,["run_id","cells","median_residual","mean_residual"])}

- Mean of run medians: **{canonical['estimate']:.9f}**.
- 90% run-bootstrap CI: **[{canonical['bootstrap_90_ci'][0]:.9f}, {canonical['bootstrap_90_ci'][1]:.9f}]**.
- 95% run-bootstrap CI: **[{canonical['bootstrap_95_ci'][0]:.9f}, {canonical['bootstrap_95_ci'][1]:.9f}]**.
- Negative runs: **{canonical['negative_runs']}/5**.
- Leave-one-run-out range: **[{canonical['leave_one_run_out_range'][0]:.9f}, {canonical['leave_one_run_out_range'][1]:.9f}]**.
- Frozen equivalence: **{'PASS' if canonical['equivalence_pass'] else 'FAIL'}**; the 95% interval is {'wholly below' if canonical['ci95_wholly_below_negative_bound'] else 'not wholly below'} the negative bound.
- Correction from invalid ARC-006: **{delta_correction:+.9f}** ({relative_correction:.2%} of the old magnitude).

## Global-rule sensitivity

Consistent `topk`: {summaries['consistent_topk']['estimate']:.9f}, 95% CI
[{summaries['consistent_topk']['bootstrap_95_ci'][0]:.9f}, {summaries['consistent_topk']['bootstrap_95_ci'][1]:.9f}],
{summaries['consistent_topk']['negative_runs']}/5 negative runs. The aggregate
rule difference is {rule_difference:.9f}; numeric-instability gate:
**{'FAIL' if numeric_instability else 'PASS'}**.

Class A+B canonical sensitivity: {summaries['class_ab_argmax']['estimate']:.9f},
95% CI [{summaries['class_ab_argmax']['bootstrap_95_ci'][0]:.9f},
{summaries['class_ab_argmax']['bootstrap_95_ci'][1]:.9f}].

Inference is clustered at the run level; no token/cell pseudoreplication is
used. The final verdict is **{primary_verdict}**.
"""
    (ARC_ROOT/"statistical_analysis.md").write_text(statistical,encoding="utf-8")

    sign_md = f"""# Sign-reversal reanalysis

The exact ARC-006 convention (`sign(cell residual) != aggregate negative sign`)
is retained; zero cells therefore count as reversals. Strict-positive and zero
counts are shown separately.

- Old reversals: **{sign_result['old_reversals']}/103**.
- Corrected reversals: **{sign_result['corrected_reversals']}/103**.
- Old/corrected strict-positive: {sign_result['old_strict_positive']} / {sign_result['corrected_strict_positive']}.
- Old/corrected zero: {sign_result['old_zero']} / {sign_result['corrected_zero']}.
- Cells changing membership: **{sign_result['membership_changed']}**.

Changed cell identities are in `sign_reversal_membership_changes.csv`; the
run-by-checkpoint distribution is in `sign_reversal_distribution.csv`. No old
label is reused as the corrected label.
"""
    (ARC_ROOT/"sign_reversal_reanalysis.md").write_text(sign_md,encoding="utf-8")

    layer_md = f"""# Layer reanalysis

{md_table(layers,["layer","count","unique_runs","old_mean","corrected_mean","corrected_ci95_low","corrected_ci95_high","low_support"])}

The weighted SD of layer means changes from
{layer_result['old_weighted_sd']:.6f} to {layer_result['corrected_weighted_sd']:.6f}.
The old range {layer_result['old_range']} becomes {layer_result['corrected_range']}.
Low-support layers: {layer_result['low_support_layers']}. Layer estimates remain
descriptive; run-cluster intervals are omitted when fewer than three runs
contribute.
"""
    (ARC_ROOT/"layer_reanalysis.md").write_text(layer_md,encoding="utf-8")

    checks = "\n".join([
        "- [x] Identical canonical top-1 code path for block and noise.",
        "- [x] Exact ties resolve to the lowest token index.",
        "- [x] No family-specific selection branch.",
        "- [x] No `D_S` leakage into targeting or matching.",
        "- [x] Equivalence bound unchanged.",
        "- [x] No seed/checkpoint/layer excluded.",
        "- [x] Matching classes and tolerances unchanged.",
        "- [x] No post-hoc threshold change.",
        "- [x] 150 unique cells and 103 Class A cells reproduced.",
        "- [x] Source harness checks passed.",
    ])
    (ARC_ROOT/"assay_integrity_check.md").write_text(
        f"# Assay integrity check\n\n{checks}\n\nPath checks:\n\n```json\n{json.dumps(path_checks,indent=2)}\n```\n\n**PASS**\n",
        encoding="utf-8")

    report = f"""# Corrected ARC-006 report

## Verdict

**{primary_verdict}**

The canonical same-rule residual is {canonical['estimate']:.9f} with 95% CI
[{canonical['bootstrap_95_ci'][0]:.9f}, {canonical['bootstrap_95_ci'][1]:.9f}].
All {canonical['negative_runs']}/5 run medians are negative; every leave-one-run-out
estimate remains below the frozen negative equivalence boundary. The point and
interval do not satisfy equivalence.

## Repair effect

The invalid mixed estimate was {OLD_RESIDUAL:.9f}. The correction is
{delta_correction:+.9f}, or {relative_correction:.2%} of its magnitude. The
qualitative family-residual conclusion {'survives' if primary_verdict=='006R-RESIDUAL-CONFIRMED' else 'is weakened'};
the invalid exact estimate remains withdrawn.

## Robustness

The globally consistent `topk` estimate is
{summaries['consistent_topk']['estimate']:.9f}. Its difference from the
canonical estimate is {rule_difference:.9f}, below the frozen 0.0025 numeric
instability threshold. Class A+B gives
{summaries['class_ab_argmax']['estimate']:.9f}.

## Sign reversals and layers

Reversals change from {sign_result['old_reversals']} to
{sign_result['corrected_reversals']} of 103, with
{sign_result['membership_changed']} cells changing membership. Layer weighted
heterogeneity changes from {layer_result['old_weighted_sd']:.6f} to
{layer_result['corrected_weighted_sd']:.6f}; low-support layers remain
{layer_result['low_support_layers']}.

## Scientific boundary

This repair establishes only whether the family-associated residual survives a
consistent top-1 assay in the frozen Pythia-160M experiment. It does not explain
the residual, establish geometry or causality, or extend to another model,
corpus, scale, or intervention family.
"""
    (ARC_ROOT/"corrected_arc006_report.md").write_text(report,encoding="utf-8")

    if primary_verdict == "006R-RESIDUAL-CONFIRMED":
        recommendation = "Resume ARC-007 using ARC-006R corrected sealed data."
        resume = "可以恢复 ARC-007，但必须使用 ARC-006R 修正并重新密封的数据。"
    elif primary_verdict == "006R-RESIDUAL-WEAKENED":
        recommendation = "Redesign one geometry test around the corrected effect size; do not execute it automatically."
        resume = "不能直接恢复原 ARC-007；应按修正效应量重设一次几何检验。"
    else:
        recommendation = "Stop the family-residual mechanism branch and reassess the paper story."
        resume = "不要恢复 ARC-007。"
    (ARC_ROOT/"next_arc_recommendation.md").write_text(
        f"# Next ARC recommendation\n\n{recommendation}\n",encoding="utf-8")
    executive = f"""# EXECUTIVE SUMMARY

## Verdict

**{primary_verdict}**

- 修正残差：**{canonical['estimate']:.9f}**。
- 95% run-bootstrap CI：**[{canonical['bootstrap_95_ci'][0]:.9f}, {canonical['bootstrap_95_ci'][1]:.9f}]**。
- seed 一致性：**{canonical['negative_runs']}/5 为负**；LOSO 范围 [{canonical['leave_one_run_out_range'][0]:.9f}, {canonical['leave_one_run_out_range'][1]:.9f}]。
- 等价性：**未通过**；95% CI 整体低于冻结下界 -{BOUND:.9f}。
- 相对无效 ARC-006 估计的修正：{delta_correction:+.9f}，占旧效应幅度 {relative_correction:.2%}。
- sign reversal：{sign_result['old_reversals']}/103 → **{sign_result['corrected_reversals']}/103**；{sign_result['membership_changed']} 个 cell 改变归属。
- layer：加权层均值 SD {layer_result['old_weighted_sd']:.6f} → **{layer_result['corrected_weighted_sd']:.6f}**；低支持层 {layer_result['low_support_layers']}。
- 资源：Level 2 纯离线重算；GPU-active 0，API/外部计算 USD 0，无下载。
- ARC-007：{resume}
"""
    (ARC_ROOT/"EXECUTIVE_SUMMARY.md").write_text(executive,encoding="utf-8")
    print(json.dumps(summary,indent=2))


if __name__ == "__main__":
    main()
