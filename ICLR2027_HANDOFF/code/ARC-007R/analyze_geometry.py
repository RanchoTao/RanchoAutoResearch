"""Frozen corrected-outcome analysis for ARC-20260827-5060-007R."""

from __future__ import annotations

import json
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


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
ARC006R = ROOT.parent / "arc_20260827_5060_006R"
ARC007 = ROOT.parent / "arc_20260826_5060_007"
RUNS = [2, 3, 5, 6, 8]
STEPS = [14000, 72000, 143000]
BOUND = 0.0107421875
R0 = -0.01683304398148147
BOOT_SEED = 20260827
BOOT_DRAWS = 100_000

BLUE, ORANGE, GOLD, INK, GRID = "#4477AA", "#EE7733", "#CCAA44", "#2B2B2B", "#D9D9D9"


def native(value):
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    if isinstance(value, np.bool_):
        return bool(value)
    raise TypeError(type(value).__name__)


def interval(values: np.ndarray, level: float) -> list[float]:
    tail = (1.0 - level) / 2.0
    return [float(x) for x in np.quantile(values, [tail, 1.0 - tail])]


def bootstrap_run_mean(values: np.ndarray, level: float = .95) -> list[float]:
    rng = np.random.default_rng(BOOT_SEED)
    values = np.asarray(values, float)
    draws = rng.choice(values, (BOOT_DRAWS, len(values)), replace=True).mean(1)
    return interval(draws, level)


def load_geometry() -> pd.DataFrame:
    rows = []
    for path in sorted((ARC007 / "raw" / "geometry").glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        for checkpoint in payload["checkpoints"]:
            if not checkpoint["harness_validation"]["pass"]:
                raise RuntimeError(f"geometry harness failure: {path.name}")
            for source in checkpoint["geometry_rows"]:
                row = dict(source)
                for item in row.pop("boundary_strata"):
                    row[f"stratum_{item['stratum']}_count"] = item["count"]
                    row[f"stratum_{item['stratum']}_flip_rate"] = item["flip_rate"]
                rows.append(row)
    frame = pd.DataFrame(rows)
    if len(frame) != 300 or frame[["target_id", "family"]].duplicated().any():
        raise RuntimeError("geometry grain failure")
    return frame


def prepare() -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    geometry = load_geometry()
    corrected = pd.read_csv(ARC006R / "corrected_results.csv")
    primary_corrected = corrected[corrected.match_class == "A"].copy()
    run_medians = primary_corrected.groupby("run_id").corrected_residual.median().reindex(RUNS)
    reproduced = float(run_medians.mean())
    baseline = {
        "expected": R0,
        "reproduced": reproduced,
        "absolute_error": abs(reproduced - R0),
        "run_medians": {str(int(k)): float(v) for k, v in run_medians.items()},
        "pass": abs(reproduced - R0) <= 1e-12,
    }
    if not baseline["pass"]:
        raise RuntimeError(f"CORRECTED_BASELINE_MISMATCH: {baseline}")

    source = corrected[[
        "target_id", "run_id", "step", "layer", "match_class", "reveal_kl",
        "reveal_nll_damage", "block_kl", "block_nll_damage", "corrected_block_ds",
        "corrected_noise_ds", "corrected_residual", "corrected_reversal",
    ]]
    geometry = geometry.merge(source, on=["target_id", "run_id", "step", "layer", "match_class"], validate="many_to_one")
    geometry["ds"] = np.where(geometry.family.eq("noise"), geometry.corrected_noise_ds, geometry.corrected_block_ds)
    geometry["source_kl"] = np.where(geometry.family.eq("noise"), geometry.reveal_kl, geometry.block_kl)
    geometry["source_nll"] = np.where(geometry.family.eq("noise"), geometry.reveal_nll_damage, geometry.block_nll_damage)
    geometry["family_indicator"] = geometry.family.eq("noise").astype(float)
    quality = {
        "rows": int(len(geometry)),
        "cells": int(geometry.target_id.nunique()),
        "class_a_cells": int(geometry.loc[geometry.match_class.eq("A"), "target_id"].nunique()),
        "duplicate_keys": int(geometry[["target_id", "family"]].duplicated().sum()),
        "max_kl_source_error": float((geometry.kl - geometry.source_kl).abs().max()),
        "max_nll_source_error": float((geometry.nll_damage - geometry.source_nll).abs().max()),
        "max_corrected_flip_error": float((geometry.top1_flip_rate - geometry.ds).abs().max()),
        "max_margin_identity_error": float((geometry.delta_margin_mean - geometry.delta_b_mean).abs().max()),
        "baseline": baseline,
    }
    quality["pass"] = bool(
        quality["rows"] == 300 and quality["cells"] == 150 and quality["class_a_cells"] == 103
        and quality["duplicate_keys"] == 0 and quality["max_kl_source_error"] <= 1e-10
        and quality["max_nll_source_error"] <= 1e-10
        and quality["max_corrected_flip_error"] <= 1e-10
        and quality["max_margin_identity_error"] <= 1e-8 and baseline["pass"]
    )
    if not quality["pass"]:
        raise RuntimeError(f"corrected geometry integrity failure: {quality}")

    primary = geometry[geometry.match_class.eq("A")].copy()
    for column in ["kl", "nll_damage", "intact_margin_mean", "delta_b_mean", "logit_delta_norm_mean", "abs_cosine_alignment_mean"]:
        mean, sd = float(primary[column].mean()), float(primary[column].std(ddof=0))
        geometry[f"z_{column}"] = (geometry[column] - mean) / sd
    geometry["f_damage"] = (geometry.z_kl + geometry.z_nll_damage) / 2
    primary = geometry[geometry.match_class.eq("A")].copy()

    metrics = ["ds", "corrected_residual", "corrected_reversal", "intact_margin_mean", "delta_b_mean", "logit_delta_norm_mean", "abs_cosine_alignment_mean"]
    metrics += [f"stratum_{i}_flip_rate" for i in range(3)]
    wide = primary.pivot(index=["target_id", "run_id", "step", "layer", "match_class"], columns="family", values=metrics)
    wide.columns = [f"{metric}_{family}" for metric, family in wide.columns]
    pairs = wide.reset_index()
    # Pivoting corrected boolean labels with numeric metrics gives pandas an
    # object block. Restore numeric dtype before arithmetic; values are unchanged.
    numeric_pair_columns = [column for column in pairs.columns if column not in {
        "target_id", "run_id", "step", "layer", "match_class",
        "corrected_reversal_block", "corrected_reversal_noise",
    }]
    pairs[numeric_pair_columns] = pairs[numeric_pair_columns].astype(float)
    pairs["family_residual"] = pairs.ds_noise - pairs.ds_block
    pairs["delta_boundary_difference"] = pairs.delta_b_mean_noise - pairs.delta_b_mean_block
    pairs["log_norm_ratio"] = np.log(pairs.logit_delta_norm_mean_noise / pairs.logit_delta_norm_mean_block)
    pairs["abs_cosine_difference"] = pairs.abs_cosine_alignment_mean_noise - pairs.abs_cosine_alignment_mean_block
    pairs["intact_margin"] = pairs.intact_margin_mean_block
    expected = primary_corrected.set_index("target_id").loc[pairs.target_id, "corrected_residual"].to_numpy()
    if float(np.max(np.abs(pairs.family_residual - expected))) > 1e-12:
        raise RuntimeError("corrected pair residual mismatch")
    for i in range(3):
        pairs[f"stratum_{i}_residual"] = pairs[f"stratum_{i}_flip_rate_noise"] - pairs[f"stratum_{i}_flip_rate_block"]
    return geometry, pairs, quality


SPECS = {
    "M0_damage": ["f_damage"],
    "M1_margin": ["f_damage", "z_intact_margin_mean"],
    "M2_boundary": ["f_damage", "z_intact_margin_mean", "z_delta_b_mean"],
    "M3_full_geometry": ["f_damage", "z_intact_margin_mean", "z_delta_b_mean", "z_logit_delta_norm_mean", "z_abs_cosine_alignment_mean"],
}


def design(frame: pd.DataFrame, predictors: list[str], fixed=("step", "layer")) -> tuple[pd.DataFrame, np.ndarray]:
    out = pd.DataFrame({"intercept": np.ones(len(frame)), **{p: frame[p].to_numpy(float) for p in predictors}, "family": frame.family_indicator.to_numpy(float)})
    if fixed:
        dummy = pd.get_dummies(frame[list(fixed)].astype(str), prefix=list(fixed), drop_first=True, dtype=float).reset_index(drop=True)
        out = pd.concat([out.reset_index(drop=True), dummy], axis=1)
    out = out.loc[:, [c == "intercept" or float(out[c].std(ddof=0)) > 1e-12 for c in out.columns]]
    return out, frame.ds.to_numpy(float)


def fit(frame: pd.DataFrame, predictors: list[str], fixed=("step", "layer")) -> dict:
    xdf, y = design(frame, predictors, fixed)
    x = xdf.to_numpy(float)
    beta = np.linalg.lstsq(x, y, rcond=None)[0]
    return {
        "family_coefficient": float(beta[list(xdf.columns).index("family")]),
        "coefficients": {str(k): float(v) for k, v in zip(xdf.columns, beta)},
        "rank": int(np.linalg.matrix_rank(x)), "columns": int(x.shape[1]),
        "condition_number": float(np.linalg.cond(x)),
        "rmse": float(np.sqrt(np.mean((y - x @ beta) ** 2))),
    }


def run_coefficients(frame: pd.DataFrame, predictors: list[str]) -> dict[int, float]:
    return {run: fit(frame[frame.run_id.eq(run)], predictors)["family_coefficient"] for run in RUNS}


def bootstrap_coefficients(coefficients: dict[int, float]) -> np.ndarray:
    values = np.asarray([coefficients[r] for r in RUNS], float)
    rng = np.random.default_rng(BOOT_SEED)
    return rng.choice(values, (BOOT_DRAWS, len(values)), replace=True).mean(1)


def paired_summary(pairs: pd.DataFrame, column: str) -> dict:
    by_run = pairs.groupby("run_id")[column].median().reindex(RUNS)
    values = by_run.to_numpy(float)
    sign = -1 if values.mean() < 0 else 1
    layers = pairs.groupby("layer")[column].mean()
    ci = bootstrap_run_mean(values)
    return {
        "metric": column, "paired_cell_mean": float(pairs[column].mean()),
        "mean_run_median": float(values.mean()), "run_medians": {str(int(k)): float(v) for k, v in by_run.items()},
        "bootstrap_95_ci": ci, "same_sign_runs": int((np.sign(values) == sign).sum()),
        "same_sign_layers": int((np.sign(layers) == sign).sum()),
        "systematic": bool((ci[0] > 0 or ci[1] < 0) and (np.sign(values) == sign).sum() >= 4),
    }


def residual_summary(frame: pd.DataFrame, column: str) -> dict:
    run = frame.groupby("run_id")[column].median().reindex(RUNS).dropna()
    values = run.to_numpy(float)
    return {"cells": int(len(frame)), "runs": int(len(values)), "estimate": float(values.mean()),
            "ci90": bootstrap_run_mean(values, .90), "ci95": bootstrap_run_mean(values, .95),
            "run_medians": {str(int(k)): float(v) for k, v in run.items()}}


def reversal_analysis(pairs: pd.DataFrame) -> tuple[dict, pd.DataFrame]:
    data = pairs.copy()
    data["reversal"] = data.family_residual.gt(0).astype(int)
    features = ["intact_margin", "delta_boundary_difference", "log_norm_ratio", "abs_cosine_difference"]
    rows = []
    for held in RUNS:
        train, test = data[~data.run_id.eq(held)], data[data.run_id.eq(held)]
        scale = StandardScaler().fit(train[features])
        model = LogisticRegression(C=1, class_weight="balanced", solver="liblinear", random_state=BOOT_SEED)
        model.fit(scale.transform(train[features]), train.reversal)
        prob = model.predict_proba(scale.transform(test[features]))[:, 1]
        rows.extend({"target_id": t, "run_id": held, "reversal": int(y), "probability": float(p)} for t, y, p in zip(test.target_id, test.reversal, prob))
    pred = pd.DataFrame(rows)
    auc = float(roc_auc_score(pred.reversal, pred.probability))
    bal = float(balanced_accuracy_score(pred.reversal, pred.probability.ge(.5)))
    groups = data.groupby("reversal")[features].agg(["count", "mean", "median"])
    stats = {str(int(g)): {f: {s: float(groups.loc[g, (f, s)]) for s in ["count", "mean", "median"]} for f in features} for g in groups.index}
    return {"reversals": int(data.reversal.sum()), "non_reversals": int((1-data.reversal).sum()), "loo_auc": auc,
            "loo_balanced_accuracy": bal, "informative": bool(auc >= .70 and bal >= .65), "group_statistics": stats}, pred


def vif(frame: pd.DataFrame, predictors: list[str]) -> list[dict]:
    x = frame[predictors + ["family_indicator"]].to_numpy(float)
    x = np.column_stack([np.ones(len(x)), x])
    names = ["intercept"] + predictors + ["family"]
    return [{"variable": names[i], "vif": float(variance_inflation_factor(x, i))} for i in range(1, len(names))]


def weighted_sd(values: np.ndarray, weights: np.ndarray) -> float:
    mean = np.average(values, weights=weights)
    return float(np.sqrt(np.average((values - mean) ** 2, weights=weights)))


def make_figures(primary: pd.DataFrame, pairs: pd.DataFrame, models: pd.DataFrame, layers: pd.DataFrame, reversal: dict) -> None:
    out = ROOT / "figures"; out.mkdir(exist_ok=True)
    plt.rcParams.update({"font.size": 9.5, "axes.titlesize": 11})
    def style(ax):
        ax.grid(True, color=GRID, alpha=.65); ax.set_axisbelow(True); ax.spines[["top", "right"]].set_visible(False)
    def blossom(fig):
        x, y = .975, .965
        for dx, dy in [(-.006, 0), (.006, 0), (0, -.008), (0, .008)]:
            fig.add_artist(plt.Circle((x+dx, y+dy), .004, transform=fig.transFigure, color=GOLD, alpha=.8))

    fig, axes = plt.subplots(1, 3, figsize=(12, 4.2))
    for ax, metric, label in [
        (axes[0], "delta_boundary_difference", "Boundary displacement"),
        (axes[1], "log_norm_ratio", "Log norm ratio"),
        (axes[2], "abs_cosine_difference", "Absolute alignment difference"),
    ]:
        run = pairs.groupby("run_id")[metric].median().reindex(RUNS).to_numpy(float)
        estimate, ci = float(run.mean()), bootstrap_run_mean(run)
        ax.axvline(0, color=INK, lw=1)
        ax.errorbar(estimate, 0, xerr=[[estimate-ci[0]], [ci[1]-estimate]], fmt="D", color=BLUE, capsize=5)
        ax.scatter(run, np.linspace(-.08, .08, len(run)), facecolors="none", edgecolors=ORANGE, marker="^", zorder=3)
        ax.set_yticks([]); ax.set_xlabel(f"Noise - block {label.lower()}"); ax.set_title(label); style(ax)
    fig.suptitle("Outcome-blind family differences: run medians and 95% run-bootstrap intervals")
    blossom(fig); fig.tight_layout(); fig.savefig(out / "fig1_family_geometry.png", dpi=240); plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.5, 4.9))
    for run, marker in zip(RUNS, ["o", "^", "s", "D", "P"]):
        part = pairs[pairs.run_id.eq(run)]; ax.scatter(part.delta_boundary_difference, part.family_residual, marker=marker, alpha=.72, label=f"seed{run}")
    ax.axhspan(-BOUND, BOUND, color=GOLD, alpha=.18); ax.axhline(0, color=INK); ax.axvline(0, color=INK, ls="--", lw=.8)
    ax.set_xlabel("Noise - block boundary displacement"); ax.set_ylabel("Corrected family residual"); ax.legend(frameon=False, ncol=3); style(ax); blossom(fig); fig.tight_layout(); fig.savefig(out / "fig2_residual_boundary.png", dpi=240); plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.8, 4.6)); ax.axvspan(-BOUND, BOUND, color=GOLD, alpha=.18); ax.axvline(0, color=INK)
    for i, row in models.iterrows():
        ax.errorbar(row.estimate, i, xerr=[[row.estimate-row.ci95_low], [row.ci95_high-row.estimate]], fmt="D" if row.model == "M2_boundary" else "o", color=ORANGE if row.model == "M2_boundary" else BLUE, capsize=4)
    ax.set_yticks(range(len(models)), models.model); ax.set_xlabel("Mean within-run family coefficient, 95% run bootstrap CI"); style(ax); blossom(fig); fig.tight_layout(); fig.savefig(out / "fig3_model_sequence.png", dpi=240); plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.1, 4.7)); ax.axhspan(-BOUND, BOUND, color=GOLD, alpha=.16); ax.axhline(0, color=INK)
    for _, row in layers.iterrows():
        ax.plot([row.layer-.12, row.layer+.12], [row.m0, row.m3], color="#BBBBBB")
        ax.scatter(row.layer-.12, row.m0, color=BLUE if not row.low_support else "white", edgecolor=BLUE)
        ax.scatter(row.layer+.12, row.m3, color=ORANGE if not row.low_support else "white", edgecolor=ORANGE, marker="^")
    ax.set_xticks(range(1, 11)); ax.set_xlabel("Layer (open: <8 cells)"); ax.set_ylabel("Family coefficient"); style(ax); blossom(fig); fig.tight_layout(); fig.savefig(out / "fig4_layer_adjustment.png", dpi=240); plt.close(fig)

    features = ["delta_boundary_difference", "log_norm_ratio", "abs_cosine_difference", "intact_margin"]
    z = (pairs[features] - pairs[features].mean()) / pairs[features].std(ddof=0); rev = pairs.family_residual.gt(0)
    fig, ax = plt.subplots(figsize=(7.8, 4.7)); x = np.arange(4); ax.axhline(0, color=INK)
    rng = np.random.default_rng(BOOT_SEED)
    for index, feature in enumerate(features):
        negative = z.loc[~rev, feature].to_numpy(); positive = z.loc[rev, feature].to_numpy()
        ax.boxplot([negative, positive], positions=[index-.14, index+.14], widths=.22,
                   patch_artist=True, showfliers=False,
                   boxprops={"facecolor": "white", "edgecolor": BLUE},
                   medianprops={"color": INK}, whiskerprops={"color": "#888888"}, capprops={"color": "#888888"})
        ax.scatter(index-.14+rng.normal(0,.025,len(negative)), negative, s=12, color=BLUE, alpha=.32)
        ax.scatter(index+.14+rng.normal(0,.025,len(positive)), positive, s=18, facecolors="none", edgecolors=ORANGE, marker="^", alpha=.65)
    ax.scatter([], [], color=BLUE, label=f"Negative (n={int((~rev).sum())})")
    ax.scatter([], [], facecolors="none", edgecolors=ORANGE, marker="^", label=f"Reversal (n={int(rev.sum())})")
    ax.set_xticks(x, ["Boundary", "Norm ratio", "Abs cosine", "Margin"]); ax.set_ylabel("Cell value (standardized)"); ax.legend(frameon=False); style(ax); blossom(fig); fig.tight_layout(); fig.savefig(out / "fig5_reversal_geometry.png", dpi=240); plt.close(fig)


def main() -> None:
    observations, pairs, quality = prepare()
    primary = observations[observations.match_class.eq("A")].copy()

    blind = json.loads((ROOT / "outcome_blind_summary.json").read_text(encoding="utf-8"))
    blind_match = pd.read_csv(ROOT / "geometry_match_manifest.csv")
    historical = pd.read_csv(ARC007 / "geometry_match_manifest.csv")
    exact_match = blind_match.merge(historical[["target_id", "geometry_match"]].rename(columns={"geometry_match": "historical"}), on="target_id", validate="one_to_one")
    if not (exact_match.geometry_match == exact_match.historical).all():
        raise RuntimeError("geometry match seal mismatch")

    model_rows, run_tables, boots = [], {}, {}
    for name, predictors in SPECS.items():
        coefficients = run_coefficients(primary, predictors)
        boot = bootstrap_coefficients(coefficients); estimate = float(np.mean(list(coefficients.values())))
        pooled = fit(primary, predictors, fixed=("run_id", "step", "layer"))
        model_rows.append({"model": name, "estimate": estimate, "ci90_low": interval(boot, .90)[0], "ci90_high": interval(boot, .90)[1],
                           "ci95_low": interval(boot, .95)[0], "ci95_high": interval(boot, .95)[1], "pooled_rank": pooled["rank"],
                           "pooled_columns": pooled["columns"], "pooled_condition": pooled["condition_number"], "pooled_rmse": pooled["rmse"]})
        run_tables[name], boots[name] = coefficients, boot
    models = pd.DataFrame(model_rows)
    m0 = float(models.loc[models.model.eq("M0_damage"), "estimate"].iloc[0])
    m2 = float(models.loc[models.model.eq("M2_boundary"), "estimate"].iloc[0])
    m3 = float(models.loc[models.model.eq("M3_full_geometry"), "estimate"].iloc[0])
    shrink2, shrink3 = 1-abs(m2)/abs(R0), 1-abs(m3)/abs(R0)
    ci90_m2 = interval(boots["M2_boundary"], .90)
    equivalence = bool(abs(m2) <= BOUND and ci90_m2[0] >= -BOUND and ci90_m2[1] <= BOUND)
    run_shrink = sum(abs(run_tables["M2_boundary"][r]) < abs(run_tables["M0_damage"][r]) for r in RUNS)
    loo = [{"excluded_run": r, "estimate": float(np.mean([run_tables["M2_boundary"][k] for k in RUNS if k != r]))} for r in RUNS]

    vifs = vif(primary, SPECS["M2_boundary"])
    max_vif = max(x["vif"] for x in vifs)
    m2_row = models[models.model.eq("M2_boundary")].iloc[0]
    identified = bool(m2_row.pooled_rank == m2_row.pooled_columns and m2_row.pooled_condition <= 250 and max_vif <= 25 and np.isfinite(boots["M2_boundary"]).all())

    selected_ids = set(blind_match.loc[blind_match.geometry_match, "target_id"])
    matched = pairs[pairs.target_id.isin(selected_ids)]
    matching = {"quality": blind["matching"], "corrected_residual": residual_summary(matched, "family_residual")}

    reversal, predictions = reversal_analysis(pairs)
    strata = [dict(stratum=i, **residual_summary(pairs, f"stratum_{i}_residual")) for i in range(3)]

    layer_rows = []
    for layer in range(1, 11):
        subset = primary[primary.layer.eq(layer)]
        cells = int(subset.target_id.nunique())
        if cells >= 2 and subset.family.nunique() == 2:
            layer_rows.append({"layer": layer, "cells": cells, "runs": int(subset.run_id.nunique()),
                               "m0": fit(subset, SPECS["M0_damage"], fixed=("run_id", "step"))["family_coefficient"],
                               "m3": fit(subset, SPECS["M3_full_geometry"], fixed=("run_id", "step"))["family_coefficient"], "low_support": cells < 8})
    layers = pd.DataFrame(layer_rows)
    weights = layers.cells.to_numpy(float)
    raw_sd = weighted_sd(layers.m0.to_numpy(float), weights); adjusted_sd = weighted_sd(layers.m3.to_numpy(float), weights)
    layer_shrink = 1-adjusted_sd/raw_sd

    correlations = primary[["kl", "nll_damage", "intact_margin_mean", "delta_b_mean", "logit_delta_norm_mean", "abs_cosine_alignment_mean"]].corr()
    separate_vif = vif(primary, ["z_kl", "z_nll_damage", "z_intact_margin_mean", "z_delta_b_mean"])
    family_comparisons = {x["metric"]: x for x in blind["family_comparisons"]}
    systematic = bool(blind["systematic_metrics"])

    go = bool(identified and systematic and shrink2 >= .50 and equivalence and run_shrink >= 4 and (layer_shrink >= .25 or reversal["informative"]))
    partial = bool(identified and not go and (shrink2 >= .20 or shrink3 >= .20 or layer_shrink >= .25 or reversal["informative"]))
    verdict = "GEOMETRY-NONIDENTIFIABLE" if not identified else "GEOMETRY-GO" if go else "GEOMETRY-PARTIAL" if partial else "GEOMETRY-NO"

    strongest_counter = {
        "m2_residual": m2, "m2_ci95": interval(boots["M2_boundary"], .95), "m2_equivalence": equivalence,
        "runs_not_shrinking": [r for r in RUNS if abs(run_tables["M2_boundary"][r]) >= abs(run_tables["M0_damage"][r])],
        "largest_adjusted_layer": layers.loc[layers.m3.abs().idxmax()].to_dict(),
        "sign_reversal_informative": reversal["informative"], "matched_support": len(matched),
    }
    summary = {
        "arc": "ARC-20260827-5060-007R", "verdict": verdict, "quality": quality,
        "corrected_baseline": R0, "equivalence_bound": BOUND, "outcome_blind": blind,
        "models": model_rows, "run_coefficients": {m: {str(k): v for k, v in c.items()} for m, c in run_tables.items()},
        "m2_shrinkage": shrink2, "m3_shrinkage": shrink3, "m2_equivalence": equivalence, "m2_runs_shrinking": run_shrink,
        "leave_one_run_out_m2": loo, "identified": identified, "matching": matching, "sign_reversal": reversal,
        "margin_strata": strata, "layer": {"raw_weighted_sd": raw_sd, "adjusted_weighted_sd": adjusted_sd, "shrinkage": layer_shrink, "rows": layers.to_dict("records")},
        "multicollinearity": {"m2_vif": vifs, "m2_max_vif": max_vif, "separate_kl_nll_vif": separate_vif, "correlations": correlations.to_dict()},
        "family_comparisons": family_comparisons, "strongest_counterevidence": strongest_counter,
    }

    processed = ROOT / "processed"; results = ROOT / "results"; processed.mkdir(exist_ok=True); results.mkdir(exist_ok=True)
    observations.to_csv(ROOT / "geometry_data.csv", index=False)
    pairs.to_csv(processed / "geometry_pairs_corrected.csv", index=False)
    models.to_csv(processed / "model_sequence.csv", index=False)
    layers.to_csv(processed / "layer_geometry.csv", index=False)
    predictions.to_csv(processed / "reversal_predictions.csv", index=False)
    correlations.to_csv(processed / "geometry_correlations.csv")
    pd.DataFrame(vifs).to_csv(processed / "m2_vif.csv", index=False)
    (results / "geometry_summary.json").write_text(json.dumps(summary, indent=2, default=native), encoding="utf-8")
    make_figures(primary, pairs, models, layers, reversal)
    print(json.dumps({"verdict": verdict, "baseline": quality["baseline"], "models": model_rows, "m2_shrinkage": shrink2,
                      "m3_shrinkage": shrink3, "equivalence": equivalence, "runs_shrinking": run_shrink, "identified": identified,
                      "reversal": reversal, "layer_shrinkage": layer_shrink, "strongest_counterevidence": strongest_counter}, indent=2, default=native))


if __name__ == "__main__":
    main()
