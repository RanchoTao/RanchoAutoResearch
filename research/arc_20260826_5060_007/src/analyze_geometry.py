"""Frozen ARC-007 geometry analysis and publication-draft figures."""

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
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, roc_auc_score
from sklearn.preprocessing import StandardScaler
from statsmodels.stats.outliers_influence import variance_inflation_factor


ARC_ROOT = Path(__file__).resolve().parents[1]
ARC006 = ARC_ROOT.parent / "arc_20260826_5060_006"
RUNS = [2, 3, 5, 6, 8]
STEPS = [14000, 72000, 143000]
BOUND = 0.0107421875
FROZEN_RESIDUAL = -0.019234664351851838
ARC006_DAMAGE_COEFFICIENT = -0.02006566243296469
BOOT_SEED = 20260826
BOOT_SAMPLES = 100_000

BLUE = "#4477AA"
ORANGE = "#EE7733"
GOLD = "#CCAA44"
INK = "#2B2B2B"
GRID = "#D9D9D9"


def native(value):
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    raise TypeError(type(value).__name__)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def bootstrap_mean(values: np.ndarray, level: float = 0.95) -> list[float]:
    values = np.asarray(values, dtype=float)
    rng = np.random.default_rng(BOOT_SEED)
    draws = rng.choice(values, size=(BOOT_SAMPLES, len(values)), replace=True).mean(axis=1)
    tail = (1.0 - level) / 2.0
    return [float(x) for x in np.quantile(draws, [tail, 1.0 - tail])]


def load_geometry() -> tuple[pd.DataFrame, list[dict]]:
    rows, payloads = [], []
    for run_id in RUNS:
        path = ARC_ROOT / "raw" / "geometry" / f"pythia-160m-seed{run_id}.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        payloads.append(payload)
        if len(payload["checkpoints"]) != 3:
            raise RuntimeError(f"incomplete geometry run {run_id}")
        for checkpoint in payload["checkpoints"]:
            if not checkpoint["harness_validation"]["pass"]:
                raise RuntimeError(f"harness failure in run {run_id}")
            array_path = Path(checkpoint["array_file"])
            if sha256(array_path) != checkpoint["array_sha256"]:
                raise RuntimeError(f"per-example hash failure: {array_path}")
            for row in checkpoint["geometry_rows"]:
                row = dict(row)
                for stratum in row.pop("boundary_strata"):
                    row[f"margin_stratum_{stratum['stratum']}_count"] = stratum["count"]
                    row[f"margin_stratum_{stratum['stratum']}_flip_rate"] = stratum["flip_rate"]
                rows.append(row)
    frame = pd.DataFrame(rows)
    if len(frame) != 300 or frame.duplicated(["target_id", "family"]).any():
        raise RuntimeError("geometry observation grain failure")
    return frame, payloads


def prepare_data() -> tuple[pd.DataFrame, pd.DataFrame, dict, list[dict]]:
    geometry, payloads = load_geometry()
    source = pd.read_csv(ARC006 / "processed" / "all_target_results.csv")
    source_fields = [
        "target_id", "run_id", "step", "layer", "match_class",
        "block_ds", "block_kl", "block_nll_damage",
        "noise_ds", "reveal_kl", "reveal_nll_damage", "family_residual",
    ]
    geometry = geometry.merge(
        source[source_fields], on=["target_id", "run_id", "step", "layer", "match_class"],
        validate="many_to_one",
    )
    geometry["source_ds"] = np.where(
        geometry["family"] == "block", geometry["block_ds"], geometry["noise_ds"]
    )
    geometry["source_kl"] = np.where(
        geometry["family"] == "block", geometry["block_kl"], geometry["reveal_kl"]
    )
    geometry["source_nll_damage"] = np.where(
        geometry["family"] == "block", geometry["block_nll_damage"], geometry["reveal_nll_damage"]
    )
    geometry["family_indicator"] = (geometry["family"] == "noise").astype(float)
    geometry["ds"] = geometry["top1_flip_rate"]

    data_quality = {
        "geometry_rows": int(len(geometry)),
        "cell_keys": int(geometry["target_id"].nunique()),
        "class_a_cells": int(geometry.loc[geometry["match_class"] == "A", "target_id"].nunique()),
        "duplicate_family_keys": int(geometry.duplicated(["target_id", "family"]).sum()),
        "nonfinite_numeric": int((~np.isfinite(geometry.select_dtypes(include="number"))).sum().sum()),
        "max_ds_difference": float((geometry["ds"] - geometry["source_ds"]).abs().max()),
        "max_kl_difference": float((geometry["kl"] - geometry["source_kl"]).abs().max()),
        "max_nll_difference": float((geometry["nll_damage"] - geometry["source_nll_damage"]).abs().max()),
        "max_margin_identity_error": float(geometry["delta_margin_identity_max_abs"].max()),
        "all_harness_pass": bool(all(
            checkpoint["harness_validation"]["pass"]
            for payload in payloads for checkpoint in payload["checkpoints"]
        )),
        "all_token_counts_exact": bool(
            (geometry.loc[geometry["family"] == "block", "tokens"] == 4608).all()
            and (geometry.loc[geometry["family"] == "noise", "tokens"] == 13824).all()
        ),
    }
    data_quality["pass"] = bool(
        data_quality["geometry_rows"] == 300
        and data_quality["cell_keys"] == 150
        and data_quality["class_a_cells"] == 103
        and data_quality["duplicate_family_keys"] == 0
        and data_quality["nonfinite_numeric"] == 0
        and data_quality["max_ds_difference"] <= 1e-10
        and data_quality["max_kl_difference"] <= 1e-10
        and data_quality["max_nll_difference"] <= 1e-10
        and data_quality["max_margin_identity_error"] <= 1e-5
        and data_quality["all_harness_pass"]
        and data_quality["all_token_counts_exact"]
    )
    if not data_quality["pass"]:
        raise RuntimeError(f"ARC-007 data-quality failure: {data_quality}")

    primary = geometry[geometry["match_class"] == "A"].copy()
    for column in [
        "kl", "nll_damage", "intact_margin_mean", "delta_b_mean",
        "logit_delta_norm_mean", "abs_cosine_alignment_mean",
        "top1_to_intact_top2_rate",
    ]:
        mean = float(primary[column].mean())
        sd = float(primary[column].std(ddof=0))
        if not np.isfinite(sd) or sd <= 0:
            raise RuntimeError(f"invalid standardization scale for {column}")
        geometry[f"z_{column}"] = (geometry[column] - mean) / sd
    geometry["f_damage"] = (geometry["z_kl"] + geometry["z_nll_damage"]) / 2.0

    primary = geometry[geometry["match_class"] == "A"].copy()
    pair_metrics = [
        "ds", "kl", "nll_damage", "intact_margin_mean", "delta_b_mean",
        "logit_delta_norm_mean", "abs_cosine_alignment_mean",
        "top1_to_intact_top2_rate", "other_flip_rate",
        "margin_stratum_0_flip_rate", "margin_stratum_1_flip_rate",
        "margin_stratum_2_flip_rate",
    ]
    wide = primary.pivot(
        index=["target_id", "run_id", "step", "layer", "match_class"],
        columns="family", values=pair_metrics,
    )
    wide.columns = [f"{metric}_{family}" for metric, family in wide.columns]
    pairs = wide.reset_index()
    pairs["family_residual"] = pairs["ds_noise"] - pairs["ds_block"]
    pairs["delta_b_difference"] = pairs["delta_b_mean_noise"] - pairs["delta_b_mean_block"]
    pairs["log_norm_ratio"] = np.log(
        pairs["logit_delta_norm_mean_noise"] / pairs["logit_delta_norm_mean_block"]
    )
    pairs["abs_cosine_difference"] = (
        pairs["abs_cosine_alignment_mean_noise"] - pairs["abs_cosine_alignment_mean_block"]
    )
    pairs["intact_margin"] = pairs["intact_margin_mean_block"]
    for stratum in range(3):
        pairs[f"margin_stratum_{stratum}_residual"] = (
            pairs[f"margin_stratum_{stratum}_flip_rate_noise"]
            - pairs[f"margin_stratum_{stratum}_flip_rate_block"]
        )
    if float((pairs["family_residual"] - source[source["match_class"] == "A"].set_index("target_id").loc[pairs["target_id"], "family_residual"].to_numpy()).abs().max()) > 1e-10:
        raise RuntimeError("paired residual does not reproduce ARC-006")
    return geometry, pairs, data_quality, payloads


MODEL_SPECS = {
    "M0_damage": ["f_damage"],
    "M1_margin": ["f_damage", "z_intact_margin_mean"],
    "M2_boundary": ["f_damage", "z_intact_margin_mean", "z_delta_b_mean"],
    "M3_full_geometry": [
        "f_damage", "z_intact_margin_mean", "z_delta_b_mean",
        "z_logit_delta_norm_mean", "z_abs_cosine_alignment_mean",
    ],
    "M4_flip_diagnostic": [
        "f_damage", "z_intact_margin_mean", "z_delta_b_mean",
        "z_logit_delta_norm_mean", "z_abs_cosine_alignment_mean",
        "z_top1_to_intact_top2_rate",
    ],
}


def fit_model(frame: pd.DataFrame, predictors: list[str], fixed=("run_id", "step", "layer")) -> dict:
    columns = {"intercept": np.ones(len(frame), dtype=float)}
    for predictor in predictors:
        columns[predictor] = frame[predictor].to_numpy(float)
    columns["family"] = frame["family_indicator"].to_numpy(float)
    fixed_frame = pd.get_dummies(
        frame[list(fixed)].astype(str), prefix=list(fixed), drop_first=True, dtype=float
    ) if fixed else pd.DataFrame(index=frame.index)
    for column in fixed_frame.columns:
        columns[column] = fixed_frame[column].to_numpy(float)
    design_frame = pd.DataFrame(columns)
    keep = ["intercept"] + [
        column for column in design_frame.columns[1:]
        if float(design_frame[column].std(ddof=0)) > 1e-12
    ]
    design_frame = design_frame[keep]
    x = design_frame.to_numpy(float)
    y = frame["ds"].to_numpy(float)
    beta = np.linalg.lstsq(x, y, rcond=None)[0]
    return {
        "family_coefficient": float(beta[keep.index("family")]),
        "coefficients": {name: float(value) for name, value in zip(keep, beta)},
        "rank": int(np.linalg.matrix_rank(x)),
        "columns": int(x.shape[1]),
        "condition_number": float(np.linalg.cond(x)),
        "rmse": float(np.sqrt(np.mean((y - x @ beta) ** 2))),
    }


def bootstrap_patterns() -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(BOOT_SEED)
    draws = rng.integers(0, len(RUNS), size=(BOOT_SAMPLES, len(RUNS)))
    counts = np.stack([(draws == index).sum(axis=1) for index in range(len(RUNS))], axis=1)
    return np.unique(counts, axis=0, return_inverse=True)


def bootstrap_model(frame: pd.DataFrame, predictors: list[str], patterns: tuple[np.ndarray, np.ndarray]) -> np.ndarray:
    unique, inverse = patterns
    values = []
    for counts in unique:
        pieces = []
        for run_id, count in zip(RUNS, counts):
            part = frame[frame["run_id"] == run_id]
            pieces.extend([part] * int(count))
        sampled = pd.concat(pieces, ignore_index=True)
        values.append(fit_model(sampled, predictors)["family_coefficient"])
    return np.asarray(values, dtype=float)[inverse]


def interval(values: np.ndarray, level: float) -> list[float]:
    tail = (1.0 - level) / 2.0
    return [float(x) for x in np.quantile(values, [tail, 1.0 - tail])]


def vif_table(frame: pd.DataFrame, predictors: list[str]) -> list[dict]:
    values = frame[predictors + ["family_indicator"]].to_numpy(float)
    values = np.column_stack([np.ones(len(values)), values])
    names = ["intercept"] + predictors + ["family"]
    return [
        {"variable": name, "vif": float(variance_inflation_factor(values, index))}
        for index, name in enumerate(names) if name != "intercept"
    ]


def paired_run_summary(pairs: pd.DataFrame, column: str) -> dict:
    run_values = pairs.groupby("run_id")[column].median().reindex(RUNS)
    values = run_values.to_numpy(float)
    mean = float(values.mean())
    sign = 1 if mean >= 0 else -1
    return {
        "column": column,
        "mean_run_median": mean,
        "run_medians": {str(int(index)): float(value) for index, value in run_values.items()},
        "bootstrap_95_ci": bootstrap_mean(values, 0.95),
        "same_sign_runs": int((np.sign(values) == sign).sum()),
    }


def residual_summary(frame: pd.DataFrame, column: str) -> dict:
    run_values = frame.groupby("run_id")[column].median().reindex(RUNS).dropna()
    values = run_values.to_numpy(float)
    return {
        "cells": int(len(frame)),
        "runs": int(len(values)),
        "mean_run_median": float(values.mean()),
        "bootstrap_90_ci": bootstrap_mean(values, 0.90),
        "bootstrap_95_ci": bootstrap_mean(values, 0.95),
        "run_medians": {str(int(index)): float(value) for index, value in run_values.items()},
    }


def sign_reversal_analysis(pairs: pd.DataFrame) -> tuple[dict, pd.DataFrame]:
    data = pairs.copy()
    data["sign_reversal"] = (data["family_residual"] > 0).astype(int)
    features = ["intact_margin", "delta_b_difference", "log_norm_ratio", "abs_cosine_difference"]
    outputs = []
    for held_out in RUNS:
        train = data[data["run_id"] != held_out]
        test = data[data["run_id"] == held_out]
        scaler = StandardScaler().fit(train[features])
        model = LogisticRegression(
            C=1.0, class_weight="balanced", solver="liblinear", random_state=BOOT_SEED
        ).fit(scaler.transform(train[features]), train["sign_reversal"])
        probability = model.predict_proba(scaler.transform(test[features]))[:, 1]
        for target_id, truth, score in zip(test["target_id"], test["sign_reversal"], probability):
            outputs.append({
                "target_id": target_id, "run_id": held_out,
                "sign_reversal": int(truth), "predicted_probability": float(score),
            })
    predictions = pd.DataFrame(outputs)
    auc = float(roc_auc_score(predictions["sign_reversal"], predictions["predicted_probability"]))
    predicted = (predictions["predicted_probability"] >= 0.5).astype(int)
    balanced = float(balanced_accuracy_score(predictions["sign_reversal"], predicted))
    group = data.groupby("sign_reversal")[features].agg(["count", "mean", "median"])
    return {
        "negative_cells": int((data["sign_reversal"] == 0).sum()),
        "reversal_cells": int((data["sign_reversal"] == 1).sum()),
        "leave_one_run_out_auc": auc,
        "leave_one_run_out_balanced_accuracy": balanced,
        "predictively_informative": bool(auc >= 0.70 and balanced >= 0.65),
        "group_statistics": {
            str(label): {
                feature: {
                    stat: float(group.loc[label, (feature, stat)])
                    for stat in ["count", "mean", "median"]
                } for feature in features
            } for label in group.index
        },
    }, predictions


def style_axis(ax: plt.Axes) -> None:
    ax.grid(True, color=GRID, linewidth=0.8, alpha=0.7)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)


def add_blossom(fig: plt.Figure) -> None:
    x, y = 0.975, 0.965
    for dx, dy in [(-.006, 0), (.006, 0), (0, -.008), (0, .008)]:
        fig.add_artist(plt.Circle(
            (x + dx, y + dy), .004, transform=fig.transFigure, color=GOLD, alpha=.8
        ))


def create_figures(
    observations: pd.DataFrame,
    pairs: pd.DataFrame,
    model_table: pd.DataFrame,
    margin_table: pd.DataFrame,
    layer_table: pd.DataFrame,
    run_table: pd.DataFrame,
    sign_summary: dict,
) -> None:
    out = ARC_ROOT / "figures"
    out.mkdir(exist_ok=True)
    plt.rcParams.update({"font.size": 10, "axes.titlesize": 11, "axes.labelsize": 10})

    fig, axes = plt.subplots(1, 3, figsize=(12, 4.5))
    for ax, metric, label in [
        (axes[0], "delta_b_mean", "Mean $\\delta b$ (= $\\Delta$margin)"),
        (axes[1], "abs_cosine_alignment_mean", "Mean absolute boundary alignment"),
        (axes[2], "top1_flip_rate", "Top-1 flip rate ($D_S$)"),
    ]:
        grouped = observations.groupby(["run_id", "family"])[metric].median().unstack()
        for run_id, row in grouped.iterrows():
            ax.plot([0, 1], [row["block"], row["noise"]], color="#BBBBBB", alpha=.65)
            ax.scatter(0, row["block"], color=BLUE, marker="o", s=36)
            ax.scatter(1, row["noise"], facecolors="none", edgecolors=ORANGE, marker="^", s=48)
        ax.set_xticks([0, 1], ["Block", "Noise"])
        ax.set_ylabel(label)
        style_axis(ax)
    fig.suptitle("Decision-boundary geometry across intervention families")
    fig.text(.5, .92, "Class A cells; each thin line is one independent training run median", ha="center", color="#666666")
    add_blossom(fig); fig.tight_layout(rect=(0, 0, 1, .90)); fig.savefig(out / "fig1_family_geometry.png", dpi=240); plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.6, 5.0))
    markers = {2: "o", 3: "^", 5: "s", 6: "D", 8: "P"}
    for run_id in RUNS:
        subset = pairs[pairs["run_id"] == run_id]
        ax.scatter(subset["delta_b_difference"], subset["family_residual"],
                   marker=markers[run_id], s=42, alpha=.72, label=f"seed{run_id}")
    ax.axhspan(-BOUND, BOUND, color=GOLD, alpha=.16)
    ax.axhline(0, color=INK, linewidth=1)
    ax.axvline(0, color=INK, linewidth=.8, linestyle="--")
    ax.set_xlabel("Noise - block mean boundary displacement")
    ax.set_ylabel("Family residual $D_S$(noise) - $D_S$(block)")
    ax.set_title("Family residual and cross-family boundary displacement")
    ax.legend(frameon=False, ncol=3)
    style_axis(ax); add_blossom(fig); fig.tight_layout(); fig.savefig(out / "fig2_residual_vs_delta_b.png", dpi=240); plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.0, 4.8))
    ax.axvspan(-BOUND, BOUND, color=GOLD, alpha=.18)
    ax.axvline(0, color=INK, linewidth=1)
    y = np.arange(len(model_table))
    for index, row in model_table.iterrows():
        ax.errorbar(row["family_coefficient"], index,
                    xerr=[[row["family_coefficient"] - row["ci95_low"]], [row["ci95_high"] - row["family_coefficient"]]],
                    fmt="D" if row["model"] == "M2_boundary" else "o",
                    color=ORANGE if row["model"] == "M2_boundary" else BLUE, capsize=4)
    ax.set_yticks(y, model_table["model"])
    ax.set_xlabel("Geometry-adjusted family coefficient with run-bootstrap 95% CI")
    ax.set_title("Family residual across the frozen model sequence")
    style_axis(ax); add_blossom(fig); fig.tight_layout(); fig.savefig(out / "fig3_adjusted_residual.png", dpi=240); plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.2, 4.7))
    ax.axhspan(-BOUND, BOUND, color=GOLD, alpha=.18)
    ax.axhline(0, color=INK, linewidth=1)
    for index, row in margin_table.iterrows():
        ax.errorbar(index, row["estimate"],
                    yerr=[[row["estimate"] - row["ci95_low"]], [row["ci95_high"] - row["estimate"]]],
                    fmt="D", color=BLUE, capsize=4)
    ax.set_xticks(range(3), ["Low / near", "Medium", "High / far"])
    ax.set_ylabel("Family residual")
    ax.set_title("Family residual by intact-margin tertile")
    style_axis(ax); add_blossom(fig); fig.tight_layout(); fig.savefig(out / "fig4_margin_strata.png", dpi=240); plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.4, 4.8))
    ax.axhspan(-BOUND, BOUND, color=GOLD, alpha=.16)
    ax.axhline(0, color=INK, linewidth=1)
    for _, row in layer_table.iterrows():
        low = bool(row["low_support"])
        ax.plot([row["layer"] - .12, row["layer"] + .12], [row["raw_residual"], row["adjusted_residual"]], color="#BBBBBB")
        ax.scatter(row["layer"] - .12, row["raw_residual"], color=BLUE if not low else "white", edgecolor=BLUE, marker="o", s=42)
        ax.scatter(row["layer"] + .12, row["adjusted_residual"], color=ORANGE if not low else "white", edgecolor=ORANGE, marker="^", s=50)
    ax.set_xticks(range(1, 11))
    ax.set_xlabel("Interior layer (open marker: <8 Class A cells)")
    ax.set_ylabel("Raw / geometry-adjusted residual")
    ax.set_title("Layer heterogeneity before and after boundary adjustment")
    style_axis(ax); add_blossom(fig); fig.tight_layout(); fig.savefig(out / "fig5_layer_heterogeneity.png", dpi=240); plt.close(fig)

    features = ["delta_b_difference", "log_norm_ratio", "abs_cosine_difference", "intact_margin"]
    labels = ["$\\Delta\\delta b$", "log norm ratio", "$\\Delta$|cos|", "intact margin"]
    standardized = pairs[features].copy()
    standardized = (standardized - standardized.mean()) / standardized.std(ddof=0)
    reversal = pairs["family_residual"] > 0
    means_negative = standardized.loc[~reversal].mean()
    means_positive = standardized.loc[reversal].mean()
    x = np.arange(len(features))
    fig, ax = plt.subplots(figsize=(8.0, 4.8))
    ax.axhline(0, color=INK, linewidth=1)
    ax.scatter(x - .10, means_negative, color=BLUE, marker="o", s=52,
               label=f"Residual negative (n={int((~reversal).sum())})")
    ax.scatter(x + .10, means_positive, facecolors="none", edgecolors=ORANGE,
               marker="^", s=62, label=f"Sign reversal (n={int(reversal.sum())})")
    ax.set_xticks(x, labels)
    ax.set_ylabel("Group mean, standardized over Class A cells")
    ax.set_title("Geometry of residual-negative and sign-reversal cells")
    ax.legend(frameon=False)
    style_axis(ax); add_blossom(fig); fig.tight_layout(); fig.savefig(out / "fig6_sign_reversals.png", dpi=240); plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.8, 4.8))
    ax.axhspan(-BOUND, BOUND, color=GOLD, alpha=.17)
    ax.axhline(0, color=INK, linewidth=1)
    for _, row in run_table.iterrows():
        ax.plot([0, 1], [row["m0_coefficient"], row["m2_coefficient"]], color="#BBBBBB")
        ax.scatter(0, row["m0_coefficient"], color=BLUE, marker="o", s=45)
        ax.scatter(1, row["m2_coefficient"], facecolors="none", edgecolors=ORANGE, marker="^", s=58)
        ax.text(1.04, row["m2_coefficient"], f"seed{int(row['run_id'])}", va="center", fontsize=8)
    ax.set_xlim(-.25, 1.30)
    ax.set_xticks([0, 1], ["M0 damage", "M2 boundary"])
    ax.set_ylabel("Run-specific family coefficient")
    ax.set_title("Run-level counterevidence to geometry explanation")
    style_axis(ax); add_blossom(fig); fig.tight_layout(); fig.savefig(out / "fig7_strongest_counterevidence.png", dpi=240); plt.close(fig)


def main() -> None:
    observations, pairs, data_quality, payloads = prepare_data()
    primary = observations[observations["match_class"] == "A"].copy()
    patterns = bootstrap_patterns()
    model_rows, bootstrap_values = [], {}
    for name, predictors in MODEL_SPECS.items():
        fit = fit_model(primary, predictors)
        boot = bootstrap_model(primary, predictors, patterns)
        bootstrap_values[name] = boot
        model_rows.append({
            "model": name,
            "family_coefficient": fit["family_coefficient"],
            "ci90_low": interval(boot, .90)[0], "ci90_high": interval(boot, .90)[1],
            "ci95_low": interval(boot, .95)[0], "ci95_high": interval(boot, .95)[1],
            "rank": fit["rank"], "columns": fit["columns"],
            "condition_number": fit["condition_number"], "rmse": fit["rmse"],
        })
    model_table = pd.DataFrame(model_rows)
    fits = {row["model"]: row for row in model_rows}

    separate_damage = fit_model(
        primary,
        ["z_kl", "z_nll_damage", "z_intact_margin_mean", "z_delta_b_mean"],
    )
    vifs_m2 = vif_table(primary, MODEL_SPECS["M2_boundary"])
    vifs_separate = vif_table(
        primary, ["z_kl", "z_nll_damage", "z_intact_margin_mean", "z_delta_b_mean"]
    )
    correlation_columns = [
        "kl", "nll_damage", "intact_margin_mean", "delta_b_mean",
        "logit_delta_norm_mean", "abs_cosine_alignment_mean",
        "top1_to_intact_top2_rate",
    ]
    correlations = primary[correlation_columns].corr()

    geometry_differences = {
        name: paired_run_summary(pairs, name) for name in [
            "delta_b_difference", "log_norm_ratio", "abs_cosine_difference",
        ]
    }
    for name, summary in geometry_differences.items():
        ci = summary["bootstrap_95_ci"]
        summary["systematic"] = bool(
            (ci[0] > 0 or ci[1] < 0) and summary["same_sign_runs"] >= 4
        )
    systematic_geometry = bool(any(
        summary["systematic"] for summary in geometry_differences.values()
    ))

    m0 = fits["M0_damage"]["family_coefficient"]
    m2 = fits["M2_boundary"]["family_coefficient"]
    m2_boot = bootstrap_values["M2_boundary"]
    primary_shrinkage = float(1.0 - abs(m2) / abs(FROZEN_RESIDUAL))
    model_shrinkage = float(1.0 - abs(m2) / abs(m0))
    shrinkage_boot = 1.0 - np.abs(m2_boot) / abs(FROZEN_RESIDUAL)
    m2_ci90 = interval(m2_boot, .90)
    equivalence = bool(abs(m2) <= BOUND and m2_ci90[0] >= -BOUND and m2_ci90[1] <= BOUND)

    run_rows = []
    for run_id in RUNS:
        subset = primary[primary["run_id"] == run_id]
        fit0 = fit_model(subset, MODEL_SPECS["M0_damage"], fixed=("step", "layer"))
        fit2 = fit_model(subset, MODEL_SPECS["M2_boundary"], fixed=("step", "layer"))
        run_rows.append({
            "run_id": run_id, "m0_coefficient": fit0["family_coefficient"],
            "m2_coefficient": fit2["family_coefficient"],
            "shrank_toward_zero": abs(fit2["family_coefficient"]) < abs(fit0["family_coefficient"]),
        })
    run_table = pd.DataFrame(run_rows)
    run_shrink_count = int(run_table["shrank_toward_zero"].sum())
    loo_run = []
    for run_id in RUNS:
        fit = fit_model(primary[primary["run_id"] != run_id], MODEL_SPECS["M2_boundary"])
        loo_run.append({"excluded_run": run_id, "family_coefficient": fit["family_coefficient"]})
    loo_layer = []
    for layer in range(1, 11):
        fit = fit_model(primary[primary["layer"] != layer], MODEL_SPECS["M2_boundary"])
        loo_layer.append({"excluded_layer": layer, "family_coefficient": fit["family_coefficient"]})

    beta_delta_b = fits["M2_boundary"]["coefficients"]["z_delta_b_mean"] if "coefficients" in fits["M2_boundary"] else fit_model(primary, MODEL_SPECS["M2_boundary"])["coefficients"]["z_delta_b_mean"]
    # Use the frozen full-sample standardization to express within-pair geometry differences.
    delta_b_sd = float(primary["delta_b_mean"].std(ddof=0))
    pairs["adjusted_residual"] = pairs["family_residual"] - beta_delta_b * pairs["delta_b_difference"] / delta_b_sd
    layer_table = pairs.groupby("layer", as_index=False).agg(
        cells=("family_residual", "size"),
        raw_residual=("family_residual", "median"),
        adjusted_residual=("adjusted_residual", "median"),
    )
    layer_table["low_support"] = layer_table["cells"] < 8
    weights = layer_table["cells"].to_numpy(float)
    def weighted_sd(values):
        mean = np.average(values, weights=weights)
        return float(np.sqrt(np.average((values - mean) ** 2, weights=weights)))
    raw_layer_sd = weighted_sd(layer_table["raw_residual"].to_numpy(float))
    adjusted_layer_sd = weighted_sd(layer_table["adjusted_residual"].to_numpy(float))
    layer_shrinkage = float(1.0 - adjusted_layer_sd / raw_layer_sd)

    margin_rows = []
    for stratum, label in enumerate(["low", "medium", "high"]):
        column = f"margin_stratum_{stratum}_residual"
        result = residual_summary(pairs, column)
        margin_rows.append({
            "stratum": stratum, "label": label, "estimate": result["mean_run_median"],
            "ci90_low": result["bootstrap_90_ci"][0], "ci90_high": result["bootstrap_90_ci"][1],
            "ci95_low": result["bootstrap_95_ci"][0], "ci95_high": result["bootstrap_95_ci"][1],
        })
    margin_table = pd.DataFrame(margin_rows)
    margin_concentration = float(
        abs(margin_table.loc[margin_table["stratum"] == 0, "estimate"].iloc[0])
        - abs(margin_table.loc[margin_table["stratum"] == 2, "estimate"].iloc[0])
    )

    pairs["mean_family_damage"] = (pairs["ds_noise"] + pairs["ds_block"]) / 2.0
    pairs["flip_damage_tertile"] = pd.qcut(
        pairs["mean_family_damage"], 3, labels=False, duplicates="drop"
    )
    flip_conditioned = []
    for tertile, group in pairs.groupby("flip_damage_tertile"):
        result = residual_summary(group, "family_residual")
        result["tertile"] = int(tertile)
        flip_conditioned.append(result)

    match_quality = json.loads((ARC_ROOT / "geometry_match_quality.json").read_text(encoding="utf-8"))
    match_manifest = pd.read_csv(ARC_ROOT / "geometry_match_manifest.csv")
    matched_pairs = pairs.merge(
        match_manifest[["target_id", "geometry_match"]], on="target_id", validate="one_to_one"
    )
    matched_pairs = matched_pairs[matched_pairs["geometry_match"]]
    geometry_matched_residual = residual_summary(matched_pairs, "family_residual") if len(matched_pairs) else None

    sign_summary, sign_predictions = sign_reversal_analysis(pairs)

    # Frozen family-by-damage interaction diagnostic.
    primary["family_damage_interaction"] = primary["family_indicator"] * primary["f_damage"]
    interaction_base = fit_model(primary, ["f_damage", "family_damage_interaction"])
    interaction_geometry = fit_model(
        primary, ["f_damage", "family_damage_interaction", "z_intact_margin_mean", "z_delta_b_mean"]
    )
    base_interaction = interaction_base["coefficients"]["family_damage_interaction"]
    geometry_interaction = interaction_geometry["coefficients"]["family_damage_interaction"]
    interaction_shrinkage = float(1.0 - abs(geometry_interaction) / (abs(base_interaction) + 1e-12))

    max_vif = max(row["vif"] for row in vifs_m2)
    identified = bool(
        data_quality["pass"]
        and fits["M2_boundary"]["rank"] == fits["M2_boundary"]["columns"]
        and fits["M2_boundary"]["condition_number"] <= 250
        and max_vif <= 25
        and np.isfinite(m2_boot).all()
    )
    go = bool(
        identified and systematic_geometry and primary_shrinkage >= 0.50
        and equivalence and run_shrink_count >= 4
    )
    partial = bool(
        identified and not go and (
            primary_shrinkage >= 0.20 or layer_shrinkage >= 0.25
            or sign_summary["predictively_informative"]
        )
    )
    if not identified:
        verdict = "GEOMETRY-NONIDENTIFIABLE"
    elif go:
        verdict = "GEOMETRY-GO"
    elif partial:
        verdict = "GEOMETRY-PARTIAL"
    else:
        verdict = "GEOMETRY-NO"

    weakest_run = run_table.iloc[np.argmax(np.abs(run_table["m2_coefficient"]) - np.abs(run_table["m0_coefficient"]))]
    strongest_counterevidence = {
        "least_favorable_run": {
            "run_id": int(weakest_run["run_id"]),
            "m0_coefficient": float(weakest_run["m0_coefficient"]),
            "m2_coefficient": float(weakest_run["m2_coefficient"]),
        },
        "largest_absolute_adjusted_layer": layer_table.loc[
            layer_table["adjusted_residual"].abs().idxmax()
        ].to_dict(),
        "geometry_match_support_adequate": bool(match_quality["support_adequate"]),
        "sign_reversal_predictively_informative": bool(sign_summary["predictively_informative"]),
        "m2_equivalence": equivalence,
    }

    resources = {
        "checkpoint_runtime_seconds_sum": float(sum(
            checkpoint["runtime_seconds"] for payload in payloads for checkpoint in payload["checkpoints"]
        )),
        "peak_cuda_bytes": int(max(
            checkpoint["peak_cuda_bytes"] for payload in payloads for checkpoint in payload["checkpoints"]
        )),
        "api_cost_usd": 0,
        "external_compute_cost_usd": 0,
    }

    summary = {
        "arc": "ARC-20260826-5060-007",
        "verdict": verdict,
        "data_quality": data_quality,
        "frozen_arc006_residual": FROZEN_RESIDUAL,
        "models": model_rows,
        "primary_adjusted_residual": m2,
        "primary_adjusted_bootstrap_90_ci": m2_ci90,
        "primary_adjusted_bootstrap_95_ci": interval(m2_boot, .95),
        "primary_shrinkage": primary_shrinkage,
        "primary_shrinkage_bootstrap_95_ci": interval(shrinkage_boot, .95),
        "model_relative_shrinkage": model_shrinkage,
        "equivalence_pass": equivalence,
        "run_shrink_count": run_shrink_count,
        "run_results": run_rows,
        "leave_one_run_out": loo_run,
        "leave_one_layer_out": loo_layer,
        "geometry_differences": geometry_differences,
        "systematic_geometry_difference": systematic_geometry,
        "geometry_matched_quality": match_quality,
        "geometry_matched_residual": geometry_matched_residual,
        "margin_strata": margin_rows,
        "near_minus_far_absolute_residual": margin_concentration,
        "flip_conditioned": flip_conditioned,
        "layer_heterogeneity": {
            "raw_weighted_sd": raw_layer_sd,
            "adjusted_weighted_sd": adjusted_layer_sd,
            "shrinkage": layer_shrinkage,
            "rows": layer_table.to_dict("records"),
        },
        "sign_reversal": sign_summary,
        "family_damage_interaction": {
            "baseline_coefficient": base_interaction,
            "geometry_coefficient": geometry_interaction,
            "shrinkage": interaction_shrinkage,
        },
        "multicollinearity": {
            "m2_vif": vifs_m2,
            "m2_max_vif": max_vif,
            "separate_kl_nll_vif": vifs_separate,
            "separate_damage_family_coefficient": separate_damage["family_coefficient"],
            "correlation_matrix": correlations.to_dict(),
        },
        "identified": identified,
        "strongest_counterevidence": strongest_counterevidence,
        "resources": resources,
        "raw_geometry_sha256": {
            path.name: sha256(path) for path in sorted((ARC_ROOT / "raw" / "geometry").glob("*.json"))
        },
    }

    processed = ARC_ROOT / "processed"
    processed.mkdir(exist_ok=True)
    observations.to_csv(processed / "geometry_observations.csv", index=False)
    pairs.to_csv(processed / "class_a_geometry_pairs.csv", index=False)
    model_table.to_csv(processed / "model_coefficients.csv", index=False)
    margin_table.to_csv(processed / "margin_strata.csv", index=False)
    layer_table.to_csv(processed / "layer_effects.csv", index=False)
    run_table.to_csv(processed / "run_effects.csv", index=False)
    sign_predictions.to_csv(processed / "sign_reversal_predictions.csv", index=False)
    correlations.to_csv(processed / "geometry_correlation_matrix.csv")
    pd.DataFrame(vifs_m2).to_csv(processed / "m2_vif.csv", index=False)
    results = ARC_ROOT / "results"
    results.mkdir(exist_ok=True)
    (results / "geometry_summary.json").write_text(
        json.dumps(summary, indent=2, default=native), encoding="utf-8"
    )
    create_figures(primary, pairs, model_table, margin_table, layer_table, run_table, sign_summary)
    print(json.dumps({
        "verdict": verdict,
        "identified": identified,
        "baseline_residual": FROZEN_RESIDUAL,
        "adjusted_residual": m2,
        "adjusted_ci90": m2_ci90,
        "shrinkage": primary_shrinkage,
        "equivalence": equivalence,
        "systematic_geometry": systematic_geometry,
        "run_shrink_count": run_shrink_count,
        "layer_heterogeneity_shrinkage": layer_shrinkage,
        "sign_reversal": sign_summary,
        "strongest_counterevidence": strongest_counterevidence,
        "data_quality": data_quality,
    }, indent=2, default=native))


if __name__ == "__main__":
    main()

