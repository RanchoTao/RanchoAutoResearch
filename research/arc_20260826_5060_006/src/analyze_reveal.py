"""Frozen ARC-006 reveal analysis and publication-draft figures."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ARC_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ARC_ROOT.parents[1]
RUNS = [2, 3, 5, 6, 8]
STEPS = [14000, 72000, 143000]
BOUND = 0.0107421875
ARC005_RESIDUAL = -0.019603587962962975
ARC005_CI95 = [-0.02591869212962968, -0.01404079861111110]
BOOT_SEED = 20260826

BLUE = "#4477AA"
ORANGE = "#EE7733"
GOLD = "#CCAA44"
INK = "#2B2B2B"
GRID = "#D9D9D9"


def json_scalar(value):
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    if isinstance(value, np.bool_):
        return bool(value)
    raise TypeError(type(value).__name__)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def bootstrap_mean(values: np.ndarray, level: float, samples: int = 100_000) -> list[float]:
    values = np.asarray(values, dtype=float)
    rng = np.random.default_rng(BOOT_SEED)
    draws = rng.choice(values, size=(samples, len(values)), replace=True).mean(axis=1)
    tail = (1.0 - level) / 2
    return [float(x) for x in np.quantile(draws, [tail, 1 - tail])]


def load_reveal() -> tuple[pd.DataFrame, list[dict]]:
    rows, payloads = [], []
    for run_id in RUNS:
        path = ARC_ROOT / "raw" / "reveal" / f"pythia-160m-seed{run_id}.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        payloads.append(payload)
        if len(payload["checkpoints"]) != 3:
            raise RuntimeError(f"incomplete reveal run {run_id}")
        for checkpoint in payload["checkpoints"]:
            if not checkpoint["harness_validation"]["pass"]:
                raise RuntimeError(f"reveal harness failure run {run_id}")
            rows.extend(checkpoint["target_results"])
    return pd.DataFrame(rows), payloads


def load_block() -> pd.DataFrame:
    return pd.read_csv(
        REPO_ROOT / "research" / "arc_20260826_5060_005" / "processed" / "block_anchor_cells.csv"
    ).rename(columns={
        "top1_agreement": "block_s", "top1_damage": "block_ds",
        "kl": "block_kl", "nll_damage": "block_nll_damage",
    })


def residual_summary(frame: pd.DataFrame) -> dict:
    run_stats = frame.groupby("run_id", as_index=False).agg(
        median_residual=("family_residual", "median"),
        mean_residual=("family_residual", "mean"),
        cells=("family_residual", "size"),
    )
    values = run_stats["median_residual"].to_numpy(float)
    mean = float(values.mean())
    sign = -1 if mean < 0 else 1
    loo = [float(np.delete(values, i).mean()) for i in range(len(values))]
    return {
        "cells": int(len(frame)),
        "run_statistics": run_stats.to_dict("records"),
        "mean_run_median_residual": mean,
        "median_run_median_residual": float(np.median(values)),
        "bootstrap_90_ci": bootstrap_mean(values, 0.90),
        "bootstrap_95_ci": bootstrap_mean(values, 0.95),
        "same_sign_runs": int((np.sign(values) == sign).sum()),
        "leave_one_run_out_means": loo,
        "leave_one_run_out_range": [float(min(loo)), float(max(loo))],
    }


def interaction_analysis(frame: pd.DataFrame) -> dict:
    rows = []
    for row in frame.to_dict("records"):
        rows.extend([
            {"run_id": row["run_id"], "step": row["step"], "layer": row["layer"],
             "family": 0.0, "kl": row["block_kl"],
             "nll": row["block_nll_damage"], "ds": row["block_ds"]},
            {"run_id": row["run_id"], "step": row["step"], "layer": row["layer"],
             "family": 1.0, "kl": row["reveal_kl"],
             "nll": row["reveal_nll_damage"], "ds": row["noise_ds"]},
        ])
    data = pd.DataFrame(rows)
    for column in ["kl", "nll"]:
        data[f"z_{column}"] = (data[column] - data[column].mean()) / data[column].std(ddof=0)
    data["f_damage"] = (data["z_kl"] + data["z_nll"]) / 2
    data["interaction"] = data["f_damage"] * data["family"]
    fixed = pd.get_dummies(
        data[["run_id", "step", "layer"]].astype(str), drop_first=True, dtype=float
    )
    design = np.column_stack([
        np.ones(len(data)), data["f_damage"], data["family"], data["interaction"], fixed
    ])
    coefficients = np.linalg.lstsq(design, data["ds"].to_numpy(float), rcond=None)[0]
    slopes = []
    for run_id, group in data.groupby("run_id"):
        block = group[group["family"] == 0]
        noise = group[group["family"] == 1]
        b = float(np.polyfit(block["f_damage"], block["ds"], 1)[0])
        n = float(np.polyfit(noise["f_damage"], noise["ds"], 1)[0])
        slopes.append({"run_id": int(run_id), "block_slope": b,
                       "noise_slope": n, "difference": n - b})
    differences = np.asarray([row["difference"] for row in slopes])
    ci = bootstrap_mean(differences, 0.95)
    common = float(coefficients[1])
    strong = bool(
        (ci[0] > 0 or ci[1] < 0)
        and abs(differences.mean()) > 0.25 * abs(common)
    )
    return {
        "observations": int(len(data)), "design_rank": int(np.linalg.matrix_rank(design)),
        "design_columns": int(design.shape[1]),
        "condition_number": float(np.linalg.cond(design)),
        "coefficient_f_damage": float(coefficients[1]),
        "coefficient_family_noise": float(coefficients[2]),
        "coefficient_interaction": float(coefficients[3]),
        "run_slopes": slopes,
        "mean_slope_difference": float(differences.mean()),
        "slope_difference_bootstrap_95_ci": ci,
        "relative_slope_difference": float(abs(differences.mean()) / (abs(common) + 1e-12)),
        "strong_interaction": strong,
    }


def style_axis(ax: plt.Axes) -> None:
    ax.grid(True, color=GRID, linewidth=0.8, alpha=0.7)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)


def add_blossom(fig: plt.Figure) -> None:
    x, y = 0.975, 0.965
    for dx, dy in [(-.006, 0), (.006, 0), (0, -.008), (0, .008)]:
        fig.add_artist(plt.Circle((x + dx, y + dy), .004,
                                 transform=fig.transFigure, color=GOLD, alpha=.8))


def create_figures(frame: pd.DataFrame, primary: pd.DataFrame, summary: dict,
                   quality: dict, worst: dict) -> None:
    out = ARC_ROOT / "figures"
    out.mkdir(exist_ok=True)
    plt.rcParams.update({"font.size": 10, "axes.titlesize": 11, "axes.labelsize": 10})

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))
    for ax, target, achieved, label in [
        (axes[0], "target_kl", "reveal_kl", "KL damage"),
        (axes[1], "target_nll_damage", "reveal_nll_damage", "NLL damage"),
    ]:
        for match_class, marker, face in [("A", "o", BLUE), ("B", "^", "none"), ("C", "x", ORANGE)]:
            subset = frame[frame["match_class"] == match_class]
            ax.scatter(subset[target], subset[achieved], marker=marker, s=30,
                       facecolors=face, edgecolors=ORANGE if face == "none" else BLUE,
                       color=ORANGE if marker == "x" else None, alpha=.7, label=f"Class {match_class}")
        limits = [min(frame[target].min(), frame[achieved].min()),
                  max(frame[target].max(), frame[achieved].max())]
        ax.plot(limits, limits, color=INK, linestyle="--", linewidth=1.2)
        ax.set_xlabel(f"Target {label}"); ax.set_ylabel(f"Achieved {label}")
        style_axis(ax)
    axes[0].legend(frameon=False)
    fig.suptitle("Prospective inverse-targeting accuracy")
    fig.text(.5,.92,f"150 run-checkpoint-layer targets; A={quality['class_counts']['A']}, B={quality['class_counts']['B']}, C={quality['class_counts']['C']}",ha="center",color="#666")
    add_blossom(fig); fig.tight_layout(rect=(0,0,1,.9)); fig.savefig(out/"fig1_targeting_accuracy.png",dpi=240); plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.4,4.6))
    labels = ["ARC-005\npost-hoc", "ARC-006\nClass A", "ARC-006\nA+B"]
    values = [26, quality["class_counts"]["A"], quality["class_counts"]["A"]+quality["class_counts"]["B"]]
    bars = ax.bar(labels, values, color=[BLUE, ORANGE, "none"], edgecolor=[BLUE, ORANGE, ORANGE], linewidth=1.8)
    for bar,value in zip(bars,values): ax.text(bar.get_x()+bar.get_width()/2,value+3,f"{value}/150\n({value/150:.1%})",ha="center")
    ax.set_ylim(0,155); ax.set_ylabel("Matched target cells"); ax.set_title("Cross-family match coverage")
    style_axis(ax); add_blossom(fig); fig.tight_layout(); fig.savefig(out/"fig2_match_coverage.png",dpi=240); plt.close(fig)

    fig, axes = plt.subplots(1,5,figsize=(13,4),sharey=True)
    for ax,run_id in zip(axes,RUNS):
        subset=primary[primary.run_id==run_id]
        for row in subset.to_dict("records"): ax.plot([0,1],[row["block_ds"],row["noise_ds"]],color="#BBB",alpha=.35)
        ax.scatter(np.zeros(len(subset)),subset.block_ds,color=BLUE,s=18,alpha=.65)
        ax.scatter(np.ones(len(subset)),subset.noise_ds,facecolors="none",edgecolors=ORANGE,marker="^",s=25)
        ax.plot([0,1],[subset.block_ds.median(),subset.noise_ds.median()],color=INK,marker="D",linewidth=2)
        ax.set_xticks([0,1],["Block","Noise"]); ax.set_title(f"seed{run_id}\nn={len(subset)}"); style_axis(ax)
    axes[0].set_ylabel("Top-1 damage $D_S$")
    fig.suptitle("Prospectively damage-matched top-1 damage"); fig.text(.5,.92,"Class A cells; thin lines share run, checkpoint, and layer",ha="center",color="#666")
    add_blossom(fig); fig.tight_layout(rect=(0,0,1,.9)); fig.savefig(out/"fig3_prospective_ds_pairs.png",dpi=240); plt.close(fig)

    run_stats=pd.DataFrame(summary["run_statistics"])
    fig,ax=plt.subplots(figsize=(7.2,4.8)); ax.axvspan(-BOUND,BOUND,color=GOLD,alpha=.18); ax.axvline(0,color=INK,linewidth=1)
    y=np.arange(len(run_stats)); ax.scatter(run_stats.median_residual,y,color=BLUE,s=48)
    agg=len(run_stats)+.8; mean=summary["mean_run_median_residual"]; ci=summary["bootstrap_95_ci"]
    ax.errorbar(mean,agg,xerr=[[mean-ci[0]],[ci[1]-mean]],fmt="D",color=ORANGE,capsize=4)
    ax.set_yticks(list(y)+[agg],[f"seed{x}" for x in run_stats.run_id]+["aggregate"]); ax.set_xlabel("$D_S$(noise) - $D_S$(block)"); ax.set_title("Prospective family residual")
    style_axis(ax); add_blossom(fig); fig.tight_layout(); fig.savefig(out/"fig4_family_residual.png",dpi=240); plt.close(fig)

    fig,ax=plt.subplots(figsize=(7.4,4.6)); estimates=[ARC005_RESIDUAL,summary["mean_run_median_residual"]]; cis=[ARC005_CI95,summary["bootstrap_95_ci"]]
    for index,(value,ci,color,marker) in enumerate(zip(estimates,cis,[BLUE,ORANGE],["o","D"])):
        ax.errorbar(value,index,xerr=[[value-ci[0]],[ci[1]-value]],fmt=marker,color=color,capsize=4,markersize=7)
    ax.axvspan(-BOUND,BOUND,color=GOLD,alpha=.18); ax.axvline(0,color=INK,linewidth=1)
    ax.set_yticks([0,1],["ARC-005 post-hoc","ARC-006 prospective"]); ax.set_xlabel("Family residual with 95% interval"); ax.set_title("Cross-family residual comparison")
    style_axis(ax); add_blossom(fig); fig.tight_layout(); fig.savefig(out/"fig5_residual_shrinkage.png",dpi=240); plt.close(fig)

    subset=primary[(primary.run_id==worst["run_id"])&(primary.step==worst["step"])]
    fig,ax=plt.subplots(figsize=(7.6,4.6)); ax.axhspan(-BOUND,BOUND,color=GOLD,alpha=.18); ax.axhline(0,color=INK,linewidth=1)
    ax.scatter(subset.layer,subset.family_residual,marker="^",facecolors="none",edgecolors=ORANGE,s=65)
    ax.set_xticks(sorted(subset.layer.unique())); ax.set_xlabel("Interior layer"); ax.set_ylabel("Family residual"); ax.set_title("Strongest residual-deviation stratum")
    fig.text(.5,.91,f"seed{worst['run_id']}, step {worst['step']:,}; selected by largest absolute stratum mean",ha="center",color="#666")
    style_axis(ax); add_blossom(fig); fig.tight_layout(rect=(0,0,1,.89)); fig.savefig(out/"fig6_strongest_counterevidence.png",dpi=240); plt.close(fig)


def main() -> None:
    manifest = pd.read_csv(ARC_ROOT / "target_manifest.csv")
    quality = json.loads((ARC_ROOT / "match_diagnostics" / "targeting_quality.json").read_text())
    reveal, payloads = load_reveal()
    block = load_block()
    if len(reveal) != 150 or reveal["target_id"].duplicated().any():
        raise RuntimeError("reveal key coverage failure")
    frame = manifest.merge(
        reveal.rename(columns={"top1_agreement":"noise_s","top1_damage":"noise_ds",
                               "kl":"reveal_kl","nll_damage":"reveal_nll_damage"}),
        on=["target_id","run_id","step","layer","selected_beta","match_class"],
        validate="one_to_one",
    ).merge(
        block[["run_id","step","layer","block_s","block_ds","block_kl","block_nll_damage"]],
        on=["run_id","step","layer"], validate="one_to_one",
    )
    frame["family_residual"] = frame["noise_ds"] - frame["block_ds"]
    frame["reveal_kl_difference"] = frame["reveal_kl"] - frame["achieved_kl"]
    frame["reveal_nll_difference"] = frame["reveal_nll_damage"] - frame["achieved_nll_damage"]
    primary = frame[frame["match_class"] == "A"].copy()
    sensitivity = frame[frame["match_class"].isin(["A","B"])].copy()
    primary_summary = residual_summary(primary)
    sensitivity_summary = residual_summary(sensitivity)
    ci90 = primary_summary["bootstrap_90_ci"]
    equivalence = bool(
        abs(primary_summary["mean_run_median_residual"]) <= BOUND
        and ci90[0] >= -BOUND and ci90[1] <= BOUND
    )
    shrinkage = float(1 - abs(primary_summary["mean_run_median_residual"]) / abs(ARC005_RESIDUAL))
    sign = -1 if primary_summary["mean_run_median_residual"] < 0 else 1
    ci95 = primary_summary["bootstrap_95_ci"]
    outside = bool(ci95[1] < -BOUND if sign < 0 else ci95[0] > BOUND)
    loo_stable = bool(all(
        value < -BOUND if sign < 0 else value > BOUND
        for value in primary_summary["leave_one_run_out_means"]
    ))
    family_clear = bool(outside and primary_summary["same_sign_runs"] >= 4 and loo_stable)
    if not quality["quality_gate_pass"]:
        verdict = "TARGETING-NONIDENTIFIABLE"
    elif equivalence:
        verdict = "TARGETING-GO"
    elif family_clear:
        verdict = "TARGETING-FAMILY"
    else:
        verdict = "TARGETING-PARTIAL"

    by_step = primary.groupby("step")["family_residual"].agg(["count","mean","median"]).reset_index()
    by_layer = primary.groupby("layer")["family_residual"].agg(["count","mean","median"]).reset_index()
    primary["damage_quartile"] = pd.qcut(primary["target_kl"],4,labels=False,duplicates="drop")
    by_damage = primary.groupby("damage_quartile")["family_residual"].agg(["count","mean","median"]).reset_index()
    strata = primary.groupby(["run_id","step"])["family_residual"].agg(["count","mean","median"])
    worst_key = max(strata.index,key=lambda key:abs(strata.loc[key,"mean"]))
    worst_row = primary.loc[primary.family_residual.abs().idxmax()]
    worst_match = frame.loc[(frame.relative_kl_error+frame.relative_nll_error).idxmax()]
    counterevidence = {
        "worst_target_match": {key: json_scalar(worst_match[key]) if isinstance(worst_match[key],np.generic) else worst_match[key] for key in ["target_id","match_class","relative_kl_error","relative_nll_error"]},
        "largest_absolute_family_residual": {key: json_scalar(worst_row[key]) if isinstance(worst_row[key],np.generic) else worst_row[key] for key in ["target_id","run_id","step","layer","family_residual"]},
        "strongest_stratum": {"run_id":int(worst_key[0]),"step":int(worst_key[1]),"count":int(strata.loc[worst_key,"count"]),"mean_residual":float(strata.loc[worst_key,"mean"])},
        "sign_reversal_cells": int((np.sign(primary.family_residual) != sign).sum()),
        "weakest_support_layer": int(quality["coverage_by_layer"][6]["layer"]),
    }
    interaction = interaction_analysis(primary)
    data_quality = {
        "manifest_rows":len(manifest),"reveal_rows":len(reveal),"merged_rows":len(frame),
        "key_duplicates":int(frame.target_id.duplicated().sum()),
        "nonfinite_numeric":int((~np.isfinite(frame.select_dtypes(include="number"))).sum().sum()),
        "max_reveal_targeting_kl_difference":float(frame.reveal_kl_difference.abs().max()),
        "max_reveal_targeting_nll_difference":float(frame.reveal_nll_difference.abs().max()),
        "all_reveal_harness_pass":bool(all(c["harness_validation"]["pass"] for p in payloads for c in p["checkpoints"])),
    }
    data_quality["pass"] = bool(
        data_quality["manifest_rows"]==150 and data_quality["reveal_rows"]==150
        and data_quality["merged_rows"]==150 and data_quality["key_duplicates"]==0
        and data_quality["nonfinite_numeric"]==0 and data_quality["all_reveal_harness_pass"]
        and data_quality["max_reveal_targeting_kl_difference"] <= 1e-10
        and data_quality["max_reveal_targeting_nll_difference"] <= 1e-10
    )
    if not data_quality["pass"]:
        raise RuntimeError(f"reveal data-quality failure: {data_quality}")
    runtime = float(sum(c["runtime_seconds"] for p in payloads for c in p["checkpoints"]))
    peak = int(max(c["peak_cuda_bytes"] for p in payloads for c in p["checkpoints"]))
    summary = {
        "arc":"ARC-20260826-5060-006","quality_gate":quality,
        "class_a_primary":primary_summary,"class_ab_sensitivity":sensitivity_summary,
        "arc005_residual":ARC005_RESIDUAL,"arc005_ci95":ARC005_CI95,
        "arc006_residual":primary_summary["mean_run_median_residual"],
        "shrinkage":shrinkage,"equivalence_bound":BOUND,"equivalence_pass":equivalence,
        "family_clear":family_clear,"interaction":interaction,
        "residual_by_checkpoint":by_step.to_dict("records"),
        "residual_by_layer":by_layer.to_dict("records"),
        "residual_by_damage_quartile":by_damage.to_dict("records"),
        "strongest_counterevidence":counterevidence,"data_quality":data_quality,
        "verdict":verdict,"resources":{"reveal_checkpoint_runtime_seconds_sum":runtime,"peak_cuda_bytes":peak,"api_cost_usd":0,"external_compute_cost_usd":0},
        "raw_reveal_sha256":{path.name:sha256(path) for path in sorted((ARC_ROOT/"raw"/"reveal").glob("*.json"))},
    }
    out=ARC_ROOT/"processed"; out.mkdir(exist_ok=True)
    frame.to_csv(out/"all_target_results.csv",index=False); primary.to_csv(out/"class_a_results.csv",index=False); sensitivity.to_csv(out/"class_ab_results.csv",index=False)
    results=ARC_ROOT/"results"; results.mkdir(exist_ok=True)
    (results/"inverse_targeting_summary.json").write_text(json.dumps(summary,indent=2,default=json_scalar),encoding="utf-8")
    create_figures(frame,primary,primary_summary,quality,counterevidence["strongest_stratum"])
    print(json.dumps({"verdict":verdict,"quality_gate_pass":quality["quality_gate_pass"],"primary":primary_summary,"sensitivity":sensitivity_summary,"shrinkage":shrinkage,"equivalence":equivalence,"interaction":interaction,"counterevidence":counterevidence,"data_quality":data_quality},indent=2,default=json_scalar))


if __name__ == "__main__":
    main()
