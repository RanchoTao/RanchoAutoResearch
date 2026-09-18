"""Deterministic feasibility and final analysis for ARC-004."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import spearmanr


ARC_ROOT = Path(__file__).resolve().parents[1]
RUN_IDS = [1, 4, 9, 6, 7, 8]
PILOT_IDS = [1, 4, 9]
CONFIRM_IDS = [6, 7, 8]
BOOTSTRAP_SEED = 20260826


def load_rows(run_ids: list[int]) -> tuple[pd.DataFrame, pd.DataFrame, list[dict]]:
    scalar_rows: list[dict] = []
    bin_rows: list[dict] = []
    payloads = []
    for run_id in run_ids:
        path = ARC_ROOT / "raw" / f"pythia-160m-seed{run_id}.json"
        if not path.exists():
            raise FileNotFoundError(path)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payloads.append(payload)
        if len(payload["checkpoints"]) != 3:
            raise RuntimeError(f"run {run_id} has {len(payload['checkpoints'])} checkpoints")
        for checkpoint in payload["checkpoints"]:
            if not checkpoint["harness_validation"]["pass"]:
                raise RuntimeError(f"harness failed in run {run_id}, step {checkpoint['step']}")
            for evaluation in checkpoint["evaluation_results"]:
                for row in evaluation["interventions"]:
                    common = {
                        "run_id": run_id,
                        "stage": payload["stage"],
                        "step": checkpoint["step"],
                        "progress": checkpoint["normalized_progress"],
                        "evaluation_seed": evaluation["evaluation_seed"],
                        "tokens": evaluation["tokens"],
                        "baseline_nll": evaluation["baseline_nll"],
                        "baseline_confidence": evaluation["baseline_top1_confidence"],
                        "layer": row["layer"],
                        "alpha": row["alpha"],
                    }
                    scalar_rows.append(common | {
                        key: row[key] for key in [
                            "top1_agreement", "top1_damage", "nll_damage", "kl",
                            "activation_relative_magnitude", "activation_absolute_rms",
                            "intact_update_rms", "layer_parameter_l2",
                            "alpha_layer_parameter_l2_proxy",
                            "alpha_layer_parameter_l2_relative_model",
                        ]
                    })
                    for index, bin_row in enumerate(row["confidence_bins"]):
                        bin_rows.append(common | {
                            "bin_index": index,
                            "bin_low": bin_row["low"],
                            "bin_high": bin_row["high"],
                            "bin_count": bin_row["count"],
                            "bin_agreement": bin_row["agreement"],
                        })
    scalar = pd.DataFrame(scalar_rows)
    bins = pd.DataFrame(bin_rows)
    return scalar, bins, payloads


def aggregate_interventions(scalar: pd.DataFrame) -> pd.DataFrame:
    group = ["run_id", "stage", "step", "progress", "layer", "alpha"]
    mean_cols = [
        "top1_agreement", "top1_damage", "nll_damage", "kl",
        "activation_relative_magnitude", "activation_absolute_rms",
        "intact_update_rms", "layer_parameter_l2",
        "alpha_layer_parameter_l2_proxy", "alpha_layer_parameter_l2_relative_model",
        "baseline_nll", "baseline_confidence",
    ]
    return scalar.groupby(group, as_index=False)[mean_cols].mean()


def aggregate_bins(bins: pd.DataFrame) -> pd.DataFrame:
    bins = bins.copy()
    bins["bin_agree_count"] = bins["bin_agreement"] * bins["bin_count"]
    group = [
        "run_id", "stage", "step", "progress", "layer", "alpha",
        "bin_index", "bin_low", "bin_high",
    ]
    out = bins.groupby(group, as_index=False)[["bin_count", "bin_agree_count"]].sum()
    out["bin_agreement"] = out["bin_agree_count"] / out["bin_count"]
    out["bin_damage"] = 1.0 - out["bin_agreement"]
    return out


def symmetric_log_ratio(a: float, b: float) -> float:
    return abs(math.log(a / b))


def greedy_match(
    group: pd.DataFrame, kind: str, magnitude_col: str = "activation_relative_magnitude"
) -> list[dict]:
    candidates = []
    rows = list(group.to_dict("records"))
    for left, right in itertools.combinations(rows, 2):
        if left["layer"] == right["layer"] and left["alpha"] == right["alpha"]:
            continue
        mag_gap = symmetric_log_ratio(
            left[magnitude_col], right[magnitude_col]
        )
        kl_gap = abs(left["kl"] - right["kl"])
        nll_gap = abs(left["nll_damage"] - right["nll_damage"])
        if kind == "A":
            if mag_gap > math.log(1.10) or kl_gap < 0.03:
                continue
            score = mag_gap / math.log(1.10) - 0.01 * kl_gap
            high, low = (left, right) if left["kl"] >= right["kl"] else (right, left)
            contrast = high["top1_damage"] - low["top1_damage"]
        elif kind == "B":
            mean_kl = (abs(left["kl"]) + abs(right["kl"])) / 2
            mean_nll = (abs(left["nll_damage"]) + abs(right["nll_damage"])) / 2
            kl_caliper = max(0.01, 0.10 * mean_kl)
            nll_caliper = max(0.015, 0.10 * mean_nll)
            mag_ratio = math.exp(mag_gap)
            separated = abs(left["layer"] - right["layer"]) >= 3 or mag_ratio >= 1.25
            if kl_gap > kl_caliper or nll_gap > nll_caliper or not separated:
                continue
            score = kl_gap / kl_caliper + nll_gap / nll_caliper
            high, low = (
                (left, right)
                if left[magnitude_col] >= right[magnitude_col]
                else (right, left)
            )
            contrast = high["top1_damage"] - low["top1_damage"]
        else:
            raise ValueError(kind)
        candidates.append((score, -kl_gap if kind == "A" else mag_gap, high, low, contrast))

    candidates.sort(key=lambda item: (
        item[0], item[1], item[2]["layer"], item[2]["alpha"],
        item[3]["layer"], item[3]["alpha"],
    ))
    used: set[tuple[int, float]] = set()
    pairs = []
    for score, _, high, low, contrast in candidates:
        high_key = (int(high["layer"]), float(high["alpha"]))
        low_key = (int(low["layer"]), float(low["alpha"]))
        if high_key in used or low_key in used:
            continue
        used.update([high_key, low_key])
        pairs.append({
            "experiment": kind,
            "magnitude_definition": magnitude_col,
            "run_id": int(high["run_id"]),
            "stage": high["stage"],
            "step": int(high["step"]),
            "high_layer": int(high["layer"]),
            "high_alpha": float(high["alpha"]),
            "low_layer": int(low["layer"]),
            "low_alpha": float(low["alpha"]),
            "high_top1_damage": high["top1_damage"],
            "low_top1_damage": low["top1_damage"],
            "directional_ds_contrast": contrast,
            "high_kl": high["kl"],
            "low_kl": low["kl"],
            "absolute_kl_gap": abs(high["kl"] - low["kl"]),
            "high_nll_damage": high["nll_damage"],
            "low_nll_damage": low["nll_damage"],
            "absolute_nll_gap": abs(high["nll_damage"] - low["nll_damage"]),
            "high_magnitude": high[magnitude_col],
            "low_magnitude": low[magnitude_col],
            "magnitude_log_gap": symmetric_log_ratio(
                high[magnitude_col], low[magnitude_col]
            ),
            "magnitude_ratio": max(
                high[magnitude_col], low[magnitude_col]
            ) / min(high[magnitude_col], low[magnitude_col]),
            "match_score": score,
        })
    return pairs


def all_matches(
    interventions: pd.DataFrame, kind: str, magnitude_col: str = "activation_relative_magnitude"
) -> pd.DataFrame:
    pairs = []
    for _, group in interventions.groupby(["run_id", "step"], sort=True):
        pairs.extend(greedy_match(group, kind, magnitude_col))
    return pd.DataFrame(pairs)


def feasibility_summary(a: pd.DataFrame, b: pd.DataFrame) -> dict:
    by_run = []
    passed = True
    for run_id in PILOT_IDS:
        count_a = int((a["run_id"] == run_id).sum()) if not a.empty else 0
        count_b = int((b["run_id"] == run_id).sum()) if not b.empty else 0
        run_pass = count_a >= 6 and count_b >= 6
        passed = passed and run_pass
        by_run.append({
            "run_id": run_id,
            "experiment_a_pairs": count_a,
            "experiment_b_pairs": count_b,
            "pass": run_pass,
        })
    return {
        "pilot_runs": by_run,
        "pooled_a_pairs": len(a),
        "pooled_b_pairs": len(b),
        "median_a_magnitude_ratio": float(a["magnitude_ratio"].median()) if len(a) else None,
        "median_b_absolute_kl_gap": float(b["absolute_kl_gap"].median()) if len(b) else None,
        "median_b_absolute_nll_gap": float(b["absolute_nll_gap"].median()) if len(b) else None,
        "feasibility_pass": passed,
    }


def bootstrap_run_mean(values: np.ndarray, samples: int = 100_000) -> list[float]:
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    draws = rng.choice(values, size=(samples, len(values)), replace=True).mean(axis=1)
    return [float(x) for x in np.quantile(draws, [0.025, 0.975])]


def summarize_pairs(pairs: pd.DataFrame) -> dict:
    run_stats = pairs.groupby(["run_id", "stage"], as_index=False).agg(
        median_contrast=("directional_ds_contrast", "median"),
        mean_contrast=("directional_ds_contrast", "mean"),
        pairs=("directional_ds_contrast", "size"),
    )
    values = run_stats["median_contrast"].to_numpy(float)
    confirm = run_stats[run_stats["stage"] == "confirmatory"]
    loo_means = []
    for run_id in run_stats["run_id"]:
        loo_means.append(float(run_stats.loc[run_stats["run_id"] != run_id, "median_contrast"].mean()))
    by_checkpoint = pairs.groupby("step", as_index=False).agg(
        mean_contrast=("directional_ds_contrast", "mean"),
        median_contrast=("directional_ds_contrast", "median"),
        pairs=("directional_ds_contrast", "size"),
    )
    return {
        "pairs": int(len(pairs)),
        "run_statistics": run_stats.to_dict("records"),
        "positive_runs": int((values > 0).sum()),
        "mean_run_median_contrast": float(values.mean()),
        "median_run_median_contrast": float(np.median(values)),
        "run_bootstrap_95_ci_mean": bootstrap_run_mean(values),
        "confirmatory_positive_runs": int((confirm["median_contrast"] > 0).sum()),
        "confirmatory_mean_run_median_contrast": float(confirm["median_contrast"].mean()),
        "leave_one_run_out_mean_range": [float(min(loo_means)), float(max(loo_means))],
        "leave_one_run_out_all_positive": bool(min(loo_means) > 0),
        "checkpoint_statistics": by_checkpoint.to_dict("records"),
        "median_magnitude_ratio": float(pairs["magnitude_ratio"].median()),
        "median_absolute_kl_gap": float(pairs["absolute_kl_gap"].median()),
        "median_absolute_nll_gap": float(pairs["absolute_nll_gap"].median()),
        "higher_kl_also_higher_nll_fraction": float(
            ((pairs["high_nll_damage"] - pairs["low_nll_damage"]) > 0).mean()
        ),
    }


def design_matrix(
    df: pd.DataFrame, damage: str, joint: bool = False, longitudinal: bool = False
) -> tuple[np.ndarray, list[str]]:
    continuous = [damage, "activation_relative_magnitude"]
    if joint:
        continuous = ["kl", "nll_damage", "activation_relative_magnitude"]
    if longitudinal:
        continuous.append("progress")
    pieces = []
    names = []
    for column in continuous:
        values = df[column].to_numpy(float)
        std = values.std(ddof=0)
        pieces.append(((values - values.mean()) / std)[:, None])
        names.append(column)
    categorical_columns = ["run_id", "layer"] if longitudinal else ["run_id", "step", "layer"]
    categorical = pd.get_dummies(
        df[categorical_columns].astype(str), drop_first=True, dtype=float
    )
    pieces.append(categorical.to_numpy())
    names.extend(categorical.columns.tolist())
    pieces.append(np.ones((len(df), 1)))
    names.append("intercept")
    return np.hstack(pieces), names


def fit_model(
    df: pd.DataFrame, damage: str, joint: bool = False, longitudinal: bool = False,
    include_loo: bool = True,
) -> dict:
    x, names = design_matrix(df, damage, joint, longitudinal)
    y = df["top1_damage"].to_numpy(float)
    coef, _, rank, singular = np.linalg.lstsq(x, y, rcond=None)
    pred = x @ coef
    ss_total = ((y - y.mean()) ** 2).sum()
    lookup = dict(zip(names, coef))
    result = {
        "damage_specification": "joint" if joint else damage,
        "longitudinal": longitudinal,
        "n": len(df),
        "rank": int(rank),
        "condition_number": float(singular.max() / singular.min()),
        "r_squared": float(1 - ((y - pred) ** 2).sum() / ss_total),
        "standardized_continuous_coefficients": {
            key: float(lookup[key]) for key in [
                item for item in ["kl", "nll_damage", "activation_relative_magnitude", "progress"]
                if item in lookup
            ]
        },
    }
    if include_loo:
        result["leave_one_run_out_continuous_coefficients"] = [
            {
                "excluded_run": int(run_id),
                **fit_model(
                    df[df["run_id"] != run_id], damage, joint, longitudinal, include_loo=False
                )["standardized_continuous_coefficients"],
            }
            for run_id in sorted(df["run_id"].unique())
        ]
    return result


def simple_associations(interventions: pd.DataFrame) -> dict:
    predictors = [
        "kl", "nll_damage", "activation_relative_magnitude", "activation_absolute_rms",
        "alpha_layer_parameter_l2_proxy",
    ]
    out = {}
    for predictor in predictors:
        overall = interventions[[predictor, "top1_damage"]].corr()
        run_spearman = []
        for _, group in interventions.groupby("run_id"):
            run_spearman.append(float(spearmanr(group[predictor], group["top1_damage"]).statistic))
        out[predictor] = {
            "pearson": float(overall.loc[predictor, "top1_damage"]),
            "spearman": float(spearmanr(interventions[predictor], interventions["top1_damage"]).statistic),
            "per_run_spearman": run_spearman,
            "median_per_run_spearman": float(np.median(run_spearman)),
        }
    return out


def residual_location(interventions: pd.DataFrame) -> dict:
    df = interventions.copy()
    # Checkpoint fixed effects already encode the three progress values; do not
    # include numeric progress in this residual-location design.
    continuous = ["kl", "nll_damage", "activation_relative_magnitude"]
    x_parts = []
    for column in continuous:
        values = df[column].to_numpy(float)
        x_parts.append(((values - values.mean()) / values.std(ddof=0))[:, None])
    categorical = pd.get_dummies(df[["run_id", "step"]].astype(str), drop_first=True, dtype=float)
    x = np.hstack(x_parts + [categorical.to_numpy(), np.ones((len(df), 1))])
    y = df["top1_damage"].to_numpy(float)
    coef = np.linalg.lstsq(x, y, rcond=None)[0]
    df["residual"] = y - x @ coef
    profiles = df.groupby(["run_id", "layer"])["residual"].mean().unstack()
    correlations = []
    for left, right in itertools.combinations(profiles.index, 2):
        correlations.append(float(spearmanr(profiles.loc[left], profiles.loc[right]).statistic))
    observed = float(df.groupby("layer")["residual"].mean().agg(lambda x: x.max() - x.min()))
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    permuted = []
    for _ in range(2_000):
        work = df[["run_id", "step", "layer", "residual"]].copy()
        work["permuted_layer"] = work.groupby(["run_id", "step"])["layer"].transform(
            lambda values: rng.permutation(values.to_numpy())
        )
        means = work.groupby("permuted_layer")["residual"].mean()
        permuted.append(float(means.max() - means.min()))
    threshold = float(np.quantile(permuted, 0.95))
    layer_means = df.groupby("layer", as_index=False)["residual"].mean()
    return {
        "observed_residual_layer_range": observed,
        "permutation_95_percentile": threshold,
        "range_exceeds_permutation_95": bool(observed > threshold),
        "median_pairwise_run_spearman": float(np.median(correlations)),
        "pairwise_run_spearman": correlations,
        "location_support": bool(observed > threshold and np.median(correlations) > 0),
        "layer_means": layer_means.to_dict("records"),
    }


def confidence_analysis(a_pairs: pd.DataFrame, bins: pd.DataFrame) -> pd.DataFrame:
    index = bins.set_index(["run_id", "step", "layer", "alpha", "bin_index"])
    rows = []
    for pair in a_pairs.to_dict("records"):
        for bin_index in range(5):
            high_key = (
                pair["run_id"], pair["step"], pair["high_layer"], pair["high_alpha"], bin_index
            )
            low_key = (
                pair["run_id"], pair["step"], pair["low_layer"], pair["low_alpha"], bin_index
            )
            if high_key not in index.index or low_key not in index.index:
                continue
            high = index.loc[high_key]
            low = index.loc[low_key]
            if high["bin_count"] < 100 or low["bin_count"] < 100:
                continue
            rows.append({
                "run_id": pair["run_id"], "stage": pair["stage"], "step": pair["step"],
                "bin_index": bin_index, "bin_low": high["bin_low"], "bin_high": high["bin_high"],
                "contrast": high["bin_damage"] - low["bin_damage"],
                "high_count": int(high["bin_count"]), "low_count": int(low["bin_count"]),
            })
    return pd.DataFrame(rows)


def create_figures(interventions: pd.DataFrame, a_pairs: pd.DataFrame, b_pairs: pd.DataFrame) -> None:
    figure_dir = ARC_ROOT / "figures"
    figure_dir.mkdir(exist_ok=True)
    plt.style.use("seaborn-v0_8-whitegrid")
    colors = {14000: "#4477AA", 72000: "#EE7733", 143000: "#228833"}

    for xcol, xlabel, filename in [
        ("kl", "KL(p intact || p intervened)", "fig_a_ds_vs_functional_damage.png"),
        ("activation_relative_magnitude", "Local relative activation change", "fig_b_ds_vs_magnitude.png"),
    ]:
        fig, ax = plt.subplots(figsize=(7.2, 4.8))
        for step, group in interventions.groupby("step"):
            ax.scatter(group[xcol], group["top1_damage"], s=16, alpha=0.48,
                       label=f"step {step:,}", color=colors[step])
        ax.set_xlabel(xlabel)
        ax.set_ylabel("Top-1 damage $D_S = 1-S$")
        ax.legend(frameon=False)
        fig.tight_layout()
        fig.savefig(figure_dir / filename, dpi=220)
        plt.close(fig)

    for pairs, title, filename in [
        (a_pairs, "Magnitude-matched: higher minus lower KL", "fig_c_magnitude_matched.png"),
        (b_pairs, "Damage-matched: higher minus lower magnitude", "fig_d_damage_matched.png"),
    ]:
        fig, ax = plt.subplots(figsize=(7.2, 4.8))
        rng = np.random.default_rng(7)
        for i, (run_id, group) in enumerate(pairs.groupby("run_id")):
            x = np.full(len(group), i) + rng.uniform(-0.12, 0.12, len(group))
            ax.scatter(x, group["directional_ds_contrast"], s=22, alpha=0.65)
            ax.plot(i, group["directional_ds_contrast"].median(), marker="D", color="black")
        ax.axhline(0, color="black", linewidth=1)
        ax.set_xticks(range(pairs["run_id"].nunique()), [
            f"seed{x}" for x in sorted(pairs["run_id"].unique())
        ])
        ax.set_ylabel("Matched $D_S$ contrast")
        ax.set_title(title)
        fig.tight_layout()
        fig.savefig(figure_dir / filename, dpi=220)
        plt.close(fig)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["feasibility", "final"], required=True)
    args = parser.parse_args()
    run_ids = PILOT_IDS if args.mode == "feasibility" else RUN_IDS
    scalar, raw_bins, payloads = load_rows(run_ids)
    interventions = aggregate_interventions(scalar)
    bins = aggregate_bins(raw_bins)
    a_pairs = all_matches(interventions, "A")
    b_pairs = all_matches(interventions, "B")

    if args.mode == "feasibility":
        summary = feasibility_summary(a_pairs, b_pairs)
        target = ARC_ROOT / "matching_diagnostics" / "pilot_feasibility.json"
        target.parent.mkdir(exist_ok=True)
        target.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        print(json.dumps(summary, indent=2))
        return

    processed = ARC_ROOT / "processed"
    diagnostics = ARC_ROOT / "matching_diagnostics"
    results = ARC_ROOT / "results"
    for directory in [processed, diagnostics, results]:
        directory.mkdir(exist_ok=True)
    interventions.to_csv(processed / "intervention_metrics.csv", index=False)
    bins.to_csv(processed / "confidence_bin_metrics.csv", index=False)
    a_pairs.to_csv(diagnostics / "magnitude_matched_pairs.csv", index=False)
    b_pairs.to_csv(diagnostics / "damage_matched_pairs.csv", index=False)
    b_magnitude_separated = b_pairs[b_pairs["magnitude_ratio"] >= 1.25].copy()
    b_location_separated = b_pairs[
        (b_pairs["high_layer"] - b_pairs["low_layer"]).abs() >= 3
    ].copy()
    b_magnitude_separated.to_csv(
        diagnostics / "damage_matched_magnitude_separated_pairs.csv", index=False
    )
    b_location_separated.to_csv(
        diagnostics / "damage_matched_location_separated_pairs.csv", index=False
    )
    a_absolute_pairs = all_matches(interventions, "A", "activation_absolute_rms")
    a_absolute_pairs.to_csv(
        diagnostics / "absolute_magnitude_matched_pairs.csv", index=False
    )
    confidence = confidence_analysis(a_pairs, bins)
    confidence.to_csv(diagnostics / "magnitude_matched_confidence.csv", index=False)

    summary_a = summarize_pairs(a_pairs)
    summary_b = summarize_pairs(b_pairs)
    summary_b_magnitude = summarize_pairs(b_magnitude_separated)
    summary_b_location = summarize_pairs(b_location_separated)
    summary_a_absolute = summarize_pairs(a_absolute_pairs)
    location = residual_location(interventions)
    regressions = [
        fit_model(interventions, "kl"),
        fit_model(interventions, "nll_damage"),
        fit_model(interventions, "kl", joint=True),
        fit_model(interventions, "kl", longitudinal=True),
    ]
    conf_summary = {
        "eligible_pair_bins": int(len(confidence)),
        "positive_pair_bins": int((confidence["contrast"] > 0).sum()),
        "mean_contrast_by_bin": (
            confidence.groupby("bin_index")["contrast"].mean().to_dict()
            if len(confidence) else {}
        ),
    }
    feasibility = feasibility_summary(
        a_pairs[a_pairs["run_id"].isin(PILOT_IDS)],
        b_pairs[b_pairs["run_id"].isin(PILOT_IDS)],
    )
    h_damage = bool(
        summary_a["positive_runs"] >= 5
        and summary_a["run_bootstrap_95_ci_mean"][0] > 0
        and summary_a["confirmatory_mean_run_median_contrast"] > 0
        and (
            summary_b["run_bootstrap_95_ci_mean"][0] <= 0 <= summary_b["run_bootstrap_95_ci_mean"][1]
            or abs(summary_b["mean_run_median_contrast"]) < 0.5 * abs(summary_a["mean_run_median_contrast"])
        )
    )
    absolute_magnitude_support = bool(
        summary_a_absolute["positive_runs"] >= 5
        and summary_a_absolute["run_bootstrap_95_ci_mean"][0] > 0
        and summary_a_absolute["confirmatory_mean_run_median_contrast"] > 0
    )
    h_magnitude = bool(
        summary_b["positive_runs"] >= 5
        and summary_b["run_bootstrap_95_ci_mean"][0] > 0
        and summary_b["confirmatory_mean_run_median_contrast"] > 0
        and summary_a["run_bootstrap_95_ci_mean"][0] <= 0
    )
    if h_damage and absolute_magnitude_support and not h_magnitude:
        verdict = "MECHANISM-GO"
        survivor = "H_damage"
    elif h_magnitude and not h_damage:
        verdict = "MECHANISM-GO"
        survivor = "H_magnitude"
    else:
        verdict = "MECHANISM-AMBIGUOUS"
        survivor = "none uniquely discriminated"

    total_gpu_seconds = float(sum(
        checkpoint["runtime_seconds"]
        for payload in payloads for checkpoint in payload["checkpoints"]
    ))
    peak_cuda = int(max(
        checkpoint["peak_cuda_bytes"]
        for payload in payloads for checkpoint in payload["checkpoints"]
    ))
    summary = {
        "arc": "ARC-20260826-5060-004",
        "feasibility": feasibility,
        "experiment_a_magnitude_matched": summary_a,
        "experiment_a_absolute_magnitude_sensitivity": summary_a_absolute,
        "experiment_b_damage_matched": summary_b,
        "experiment_b_magnitude_separated_subset": summary_b_magnitude,
        "experiment_b_location_separated_subset": summary_b_location,
        "confidence_control": conf_summary,
        "regressions": regressions,
        "simple_associations": simple_associations(interventions),
        "location_analysis": location,
        "prespecified_h_damage_pass": h_damage,
        "absolute_magnitude_sensitivity_pass": absolute_magnitude_support,
        "prespecified_h_magnitude_pass": h_magnitude,
        "prespecified_h_location_support": location["location_support"],
        "best_surviving_hypothesis": survivor,
        "verdict": verdict,
        "resources": {
            "checkpoint_runtime_seconds_sum": total_gpu_seconds,
            "peak_cuda_bytes": peak_cuda,
            "api_cost_usd": 0,
        },
        "raw_sha256": {
            path.name: sha256(path) for path in sorted((ARC_ROOT / "raw").glob("*.json"))
        },
    }
    target = results / "mechanism_summary.json"
    target.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    create_figures(interventions, a_pairs, b_pairs)
    print(json.dumps({
        "verdict": verdict,
        "survivor": survivor,
        "experiment_a": summary_a,
        "experiment_b": summary_b,
        "location_support": location["location_support"],
        "output": str(target),
    }, indent=2))


if __name__ == "__main__":
    main()
