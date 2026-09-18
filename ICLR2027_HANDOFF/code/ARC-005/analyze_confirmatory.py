"""Frozen confirmatory analysis and figures for ARC-005."""

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
import yaml


ARC_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ARC_ROOT.parents[1]
RUNS = [2, 3, 5, 6, 8]
STEPS = [14000, 72000, 143000]
LAYERS = list(range(1, 11))
BOOT_SEED = 20260826

BLUE = "#4477AA"
ORANGE = "#EE7733"
INK = "#2B2B2B"
GRID = "#D9D9D9"
GOLD = "#CCAA44"


def anchor_path(run_id: int) -> Path:
    if run_id <= 5:
        base = REPO_ROOT / "meta_arc05" / "ARC-20260825-5060-002" / "experiments" / "raw"
    else:
        base = REPO_ROOT / "meta_arc05" / "ARC-20260826-5060-003" / "experiments" / "raw"
    return base / f"pythia-160m-seed{run_id}.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def json_scalar(value):
    """Serialize NumPy/Pandas scalar wrappers without changing numeric values."""
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    if isinstance(value, np.bool_):
        return bool(value)
    raise TypeError(f"Object of type {value.__class__.__name__} is not JSON serializable")


def bootstrap_mean(values: np.ndarray, level: float, samples: int = 100_000) -> list[float]:
    values = np.asarray(values, dtype=float)
    rng = np.random.default_rng(BOOT_SEED)
    draws = rng.choice(values, size=(samples, len(values)), replace=True).mean(axis=1)
    tail = (1.0 - level) / 2
    return [float(value) for value in np.quantile(draws, [tail, 1 - tail])]


def load_noise() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, list[dict]]:
    scalar_rows = []
    bin_rows = []
    baseline_rows = []
    payloads = []
    raw_dir = ARC_ROOT / "raw" / "confirmatory"
    for run_id in RUNS:
        payload = json.loads((raw_dir / f"pythia-160m-seed{run_id}.json").read_text())
        payloads.append(payload)
        if len(payload["checkpoints"]) != 3:
            raise RuntimeError(f"run {run_id} is incomplete")
        for checkpoint in payload["checkpoints"]:
            if not checkpoint["harness_validation"]["pass"]:
                raise RuntimeError(f"harness failure run {run_id}, step {checkpoint['step']}")
            for evaluation in checkpoint["evaluation_results"]:
                baseline_rows.append({
                    "run_id": run_id,
                    "step": checkpoint["step"],
                    "evaluation_seed": evaluation["evaluation_seed"],
                    "baseline_nll": evaluation["baseline_nll"],
                    "baseline_confidence": evaluation["baseline_top1_confidence"],
                    "tokens": evaluation["tokens"],
                })
                for row in evaluation["interventions"]:
                    common = {
                        "run_id": run_id,
                        "step": checkpoint["step"],
                        "progress": checkpoint["normalized_progress"],
                        "evaluation_seed": evaluation["evaluation_seed"],
                        "layer": row["layer"],
                        "beta": row["beta"],
                        "direction_id": row["noise_direction_id"],
                        "tokens": evaluation["tokens"],
                    }
                    scalar_rows.append(common | {
                        key: row[key] for key in [
                            "top1_agreement", "top1_damage", "intervened_nll",
                            "nll_damage", "kl", "activation_relative_magnitude",
                            "activation_absolute_rms",
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
    return pd.DataFrame(scalar_rows), pd.DataFrame(bin_rows), pd.DataFrame(baseline_rows), payloads


def load_block() -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    baselines = []
    for run_id in RUNS:
        payload = json.loads(anchor_path(run_id).read_text())
        checkpoints = {row["step"]: row for row in payload["checkpoints"]}
        for step in STEPS:
            checkpoint = checkpoints[step]
            for evaluation in checkpoint["seed_results"]:
                baselines.append({
                    "run_id": run_id,
                    "step": step,
                    "evaluation_seed": evaluation["evaluation_seed"],
                    "baseline_nll": evaluation["baseline_nll"],
                })
                for row in evaluation["layers"]:
                    rows.append({
                        "run_id": run_id,
                        "step": step,
                        "progress": checkpoint["normalized_progress"],
                        "evaluation_seed": evaluation["evaluation_seed"],
                        "layer": row["layer"],
                        "top1_agreement": row["top1_agreement"],
                        "top1_damage": 1.0 - row["top1_agreement"],
                        "nll_damage": row["nll_damage"],
                        "kl": row["kl"],
                    })
    return pd.DataFrame(rows), pd.DataFrame(baselines)


def aggregate_noise(raw: pd.DataFrame) -> pd.DataFrame:
    group = ["run_id", "step", "progress", "layer", "beta"]
    columns = [
        "top1_agreement", "top1_damage", "intervened_nll", "nll_damage", "kl",
        "activation_relative_magnitude", "activation_absolute_rms",
    ]
    out = raw.groupby(group, as_index=False)[columns].mean()
    out["family"] = "activation_noise"
    out["catastrophic"] = (
        (out["intervened_nll"] > 8.0) | (out["kl"] > 2.5) | (out["top1_agreement"] < 0.20)
    )
    return out


def aggregate_block(raw: pd.DataFrame) -> pd.DataFrame:
    group = ["run_id", "step", "progress", "layer"]
    columns = ["top1_agreement", "top1_damage", "nll_damage", "kl"]
    out = raw.groupby(group, as_index=False)[columns].mean()
    out["family"] = "block_deletion"
    out["catastrophic"] = False
    return out


def aggregate_confidence(raw: pd.DataFrame) -> pd.DataFrame:
    data = raw.copy()
    data["agree_count"] = data["bin_agreement"] * data["bin_count"]
    group = ["run_id", "step", "bin_index", "bin_low", "bin_high"]
    out = data.groupby(group, as_index=False)[["agree_count", "bin_count"]].sum()
    out["agreement"] = out["agree_count"] / out["bin_count"]
    return out


def calipers(left: dict, right: dict, relative: float) -> tuple[bool, dict]:
    kl_gap = abs(left["kl"] - right["kl"])
    nll_gap = abs(left["nll_damage"] - right["nll_damage"])
    kl_mean = (abs(left["kl"]) + abs(right["kl"])) / 2
    nll_mean = (abs(left["nll_damage"]) + abs(right["nll_damage"])) / 2
    kl_caliper = max(0.01, relative * kl_mean)
    nll_caliper = max(0.015, relative * nll_mean)
    return kl_gap <= kl_caliper and nll_gap <= nll_caliper, {
        "absolute_kl_gap": kl_gap,
        "absolute_nll_gap": nll_gap,
        "relative_kl_gap": kl_gap / (kl_mean + 1e-12),
        "relative_nll_gap": nll_gap / (nll_mean + 1e-12),
        "kl_caliper": kl_caliper,
        "nll_caliper": nll_caliper,
    }


def match_cross_family(
    noise: pd.DataFrame, block: pd.DataFrame, relative: float = 0.10
) -> tuple[pd.DataFrame, pd.DataFrame]:
    pairs = []
    discards = []
    noise_index = noise.groupby(["run_id", "step", "layer"])
    for block_row in block.to_dict("records"):
        key = (block_row["run_id"], block_row["step"], block_row["layer"])
        candidates = noise_index.get_group(key)
        candidates = candidates[~candidates["catastrophic"]]
        eligible = []
        closest = None
        for noise_row in candidates.to_dict("records"):
            ok, balance = calipers(noise_row, block_row, relative)
            score = (
                balance["absolute_kl_gap"] / balance["kl_caliper"]
                + balance["absolute_nll_gap"] / balance["nll_caliper"]
            )
            candidate = (score, noise_row["beta"], noise_row, balance)
            if closest is None or candidate[:2] < closest[:2]:
                closest = candidate
            if ok:
                eligible.append(candidate)
        if not eligible:
            discards.append({
                "run_id": key[0], "step": key[1], "layer": key[2],
                "reason": "no_joint_caliper_match",
                "closest_beta": closest[1] if closest else None,
                "closest_score": closest[0] if closest else None,
                **(closest[3] if closest else {}),
            })
            continue
        _, _, noise_row, balance = min(eligible, key=lambda item: (item[0], item[1]))
        pairs.append({
            "pair_id": f"r{key[0]}_s{key[1]}_l{key[2]}",
            "run_id": key[0], "step": key[1], "layer": key[2],
            "beta": noise_row["beta"],
            "block_ds": block_row["top1_damage"],
            "noise_ds": noise_row["top1_damage"],
            "family_residual": noise_row["top1_damage"] - block_row["top1_damage"],
            "block_kl": block_row["kl"], "noise_kl": noise_row["kl"],
            "block_nll_damage": block_row["nll_damage"],
            "noise_nll_damage": noise_row["nll_damage"],
            "noise_m_rel": noise_row["activation_relative_magnitude"],
            **balance,
        })
    return pd.DataFrame(pairs), pd.DataFrame(discards)


def greedy_magnitude_matched(noise: pd.DataFrame) -> pd.DataFrame:
    pairs = []
    for (run_id, step, beta), group in noise.groupby(["run_id", "step", "beta"]):
        candidates = []
        for left, right in itertools.combinations(group.to_dict("records"), 2):
            gap = abs(left["kl"] - right["kl"])
            if gap < 0.03:
                continue
            high, low = (left, right) if left["kl"] >= right["kl"] else (right, left)
            candidates.append((-gap, high["layer"], low["layer"], high, low))
        candidates.sort(key=lambda item: item[:3])
        used = set()
        for _, _, _, high, low in candidates:
            if high["layer"] in used or low["layer"] in used:
                continue
            used.update([high["layer"], low["layer"]])
            pairs.append({
                "run_id": run_id, "step": step, "beta": beta,
                "high_layer": high["layer"], "low_layer": low["layer"],
                "kl_gap": high["kl"] - low["kl"],
                "nll_gap": high["nll_damage"] - low["nll_damage"],
                "magnitude_ratio": max(
                    high["activation_relative_magnitude"], low["activation_relative_magnitude"]
                ) / min(
                    high["activation_relative_magnitude"], low["activation_relative_magnitude"]
                ),
                "directional_ds_contrast": high["top1_damage"] - low["top1_damage"],
            })
    return pd.DataFrame(pairs)


def greedy_damage_matched(noise: pd.DataFrame) -> pd.DataFrame:
    pairs = []
    for (run_id, step), group in noise.groupby(["run_id", "step"]):
        candidates = []
        for left, right in itertools.combinations(group.to_dict("records"), 2):
            if left["beta"] == right["beta"]:
                continue
            ratio = max(left["activation_relative_magnitude"], right["activation_relative_magnitude"]) / min(
                left["activation_relative_magnitude"], right["activation_relative_magnitude"]
            )
            if ratio < 1.25:
                continue
            ok, balance = calipers(left, right, 0.10)
            if not ok:
                continue
            score = (
                balance["absolute_kl_gap"] / balance["kl_caliper"]
                + balance["absolute_nll_gap"] / balance["nll_caliper"]
            )
            high, low = (
                (left, right)
                if left["activation_relative_magnitude"] >= right["activation_relative_magnitude"]
                else (right, left)
            )
            candidates.append((score, -ratio, high, low, balance))
        candidates.sort(key=lambda item: (item[0], item[1], item[2]["layer"], item[3]["layer"]))
        used = set()
        for _, _, high, low, balance in candidates:
            high_key = (high["layer"], high["beta"])
            low_key = (low["layer"], low["beta"])
            if high_key in used or low_key in used:
                continue
            used.update([high_key, low_key])
            pairs.append({
                "run_id": run_id, "step": step,
                "high_layer": high["layer"], "high_beta": high["beta"],
                "low_layer": low["layer"], "low_beta": low["beta"],
                "magnitude_ratio": max(
                    high["activation_relative_magnitude"], low["activation_relative_magnitude"]
                ) / min(
                    high["activation_relative_magnitude"], low["activation_relative_magnitude"]
                ),
                "directional_ds_contrast": high["top1_damage"] - low["top1_damage"],
                **balance,
            })
    return pd.DataFrame(pairs)


def pair_summary(pairs: pd.DataFrame) -> dict:
    run_stats = pairs.groupby("run_id", as_index=False).agg(
        median_contrast=("directional_ds_contrast", "median"),
        pairs=("directional_ds_contrast", "size"),
    )
    values = run_stats["median_contrast"].to_numpy(float)
    return {
        "pairs": int(len(pairs)),
        "run_statistics": run_stats.to_dict("records"),
        "positive_runs": int((values > 0).sum()),
        "mean_run_median": float(values.mean()),
        "bootstrap_95_ci": bootstrap_mean(values, 0.95),
    }


def sign_test(noise: pd.DataFrame) -> dict:
    checkpoint = noise.groupby(["run_id", "step"], as_index=False)["top1_agreement"].mean()
    pivot = checkpoint.pivot(index="run_id", columns="step", values="top1_agreement")
    deltas = pivot[143000] - pivot[14000]
    values = deltas.to_numpy(float)
    return {
        "run_checkpoint_s": checkpoint.to_dict("records"),
        "run_deltas": [
            {"run_id": int(run_id), "delta_s": float(delta)}
            for run_id, delta in deltas.items()
        ],
        "negative_runs": int((values < 0).sum()),
        "mean_delta_s": float(values.mean()),
        "median_delta_s": float(np.median(values)),
        "bootstrap_95_ci": bootstrap_mean(values, 0.95),
        "pass": bool((values < 0).sum() >= 4 and bootstrap_mean(values, 0.95)[1] < 0),
    }


def confidence_test(confidence: pd.DataFrame) -> dict:
    pivot = confidence.pivot_table(
        index=["run_id", "bin_index", "bin_low", "bin_high"],
        columns="step", values=["agreement", "bin_count"], aggfunc="first"
    )
    rows = []
    for index, row in pivot.iterrows():
        run_id, bin_index, low, high = index
        early_count = row[("bin_count", 14000)]
        late_count = row[("bin_count", 143000)]
        if early_count < 100 or late_count < 100:
            continue
        rows.append({
            "run_id": int(run_id), "bin_index": int(bin_index),
            "low": float(low), "high": float(high),
            "early_count": int(early_count), "late_count": int(late_count),
            "delta_s": float(row[("agreement", 143000)] - row[("agreement", 14000)]),
        })
    frame = pd.DataFrame(rows)
    return {
        "eligible_run_bins": int(len(frame)),
        "negative_run_bins": int((frame["delta_s"] < 0).sum()),
        "mean_delta_by_bin": frame.groupby("bin_index")["delta_s"].mean().to_dict(),
        "rows": rows,
    }


def cross_family_summary(pairs: pd.DataFrame, bound: float) -> dict:
    run_stats = pairs.groupby("run_id", as_index=False).agg(
        median_residual=("family_residual", "median"),
        mean_residual=("family_residual", "mean"),
        pairs=("family_residual", "size"),
    )
    values = run_stats["median_residual"].to_numpy(float)
    ci90 = bootstrap_mean(values, 0.90)
    ci95 = bootstrap_mean(values, 0.95)
    mean = float(values.mean())
    return {
        "pairs": int(len(pairs)),
        "run_statistics": run_stats.to_dict("records"),
        "mean_run_median_residual": mean,
        "median_run_median_residual": float(np.median(values)),
        "bootstrap_90_ci": ci90,
        "bootstrap_95_ci": ci95,
        "equivalence_bound": bound,
        "equivalence_pass": bool(abs(mean) <= bound and ci90[0] >= -bound and ci90[1] <= bound),
        "r_family": abs(mean) / 0.04296875,
        "leave_one_run_out_mean_range": [
            float(min(np.delete(values, i).mean() for i in range(len(values)))),
            float(max(np.delete(values, i).mean() for i in range(len(values)))),
        ],
    }


def standardized_mean_difference(left: pd.Series, right: pd.Series) -> float:
    pooled = math.sqrt((left.var(ddof=1) + right.var(ddof=1)) / 2)
    return float((left.mean() - right.mean()) / pooled) if pooled else 0.0


def matching_quality(
    pairs: pd.DataFrame, discards: pd.DataFrame, noise: pd.DataFrame, block: pd.DataFrame
) -> dict:
    coverage = pairs.groupby("run_id").size().reindex(RUNS, fill_value=0)
    before = {
        "kl_smd_noise_minus_block": standardized_mean_difference(noise["kl"], block["kl"]),
        "nll_smd_noise_minus_block": standardized_mean_difference(
            noise["nll_damage"], block["nll_damage"]
        ),
    }
    after = {
        "mean_signed_kl_gap": float((pairs["noise_kl"] - pairs["block_kl"]).mean()),
        "mean_signed_nll_gap": float(
            (pairs["noise_nll_damage"] - pairs["block_nll_damage"]).mean()
        ),
        "median_relative_kl_gap": float(pairs["relative_kl_gap"].median()),
        "median_relative_nll_gap": float(pairs["relative_nll_gap"].median()),
    }
    match_pass = bool(
        len(pairs) >= 50
        and coverage.min() >= 5
        and len(pairs) / 150 >= 0.30
        and after["median_relative_kl_gap"] <= 0.10
        and after["median_relative_nll_gap"] <= 0.10
    )
    return {
        "eligible_block_cells": 150,
        "candidate_noise_cells": int(len(noise)),
        "matched_pairs": int(len(pairs)),
        "discarded_block_cells": int(len(discards)),
        "coverage_fraction": len(pairs) / 150,
        "matches_by_run": {str(int(k)): int(v) for k, v in coverage.items()},
        "balance_before": before,
        "balance_after": after,
        "match_quality_pass": match_pass,
    }


def interaction_analysis(pairs: pd.DataFrame) -> dict:
    rows = []
    for pair in pairs.to_dict("records"):
        rows.extend([
            {
                "run_id": pair["run_id"], "step": pair["step"], "layer": pair["layer"],
                "family": 0, "kl": pair["block_kl"], "nll_damage": pair["block_nll_damage"],
                "ds": pair["block_ds"],
            },
            {
                "run_id": pair["run_id"], "step": pair["step"], "layer": pair["layer"],
                "family": 1, "kl": pair["noise_kl"], "nll_damage": pair["noise_nll_damage"],
                "ds": pair["noise_ds"],
            },
        ])
    data = pd.DataFrame(rows)
    for column in ["kl", "nll_damage"]:
        data[f"z_{column}"] = (data[column] - data[column].mean()) / data[column].std(ddof=0)
    data["f_damage"] = (data["z_kl"] + data["z_nll_damage"]) / 2
    data["interaction"] = data["f_damage"] * data["family"]

    fixed = pd.get_dummies(
        data[["run_id", "step", "layer"]].astype(str), drop_first=True, dtype=float
    )
    x = np.column_stack([
        np.ones(len(data)), data["f_damage"], data["family"], data["interaction"], fixed
    ])
    coefficients = np.linalg.lstsq(x, data["ds"].to_numpy(float), rcond=None)[0]
    slope_differences = []
    slopes = []
    for run_id, group in data.groupby("run_id"):
        block = group[group["family"] == 0]
        noise = group[group["family"] == 1]
        block_slope = float(np.polyfit(block["f_damage"], block["ds"], 1)[0])
        noise_slope = float(np.polyfit(noise["f_damage"], noise["ds"], 1)[0])
        slopes.append({
            "run_id": int(run_id), "block_slope": block_slope,
            "noise_slope": noise_slope, "difference": noise_slope - block_slope,
        })
        slope_differences.append(noise_slope - block_slope)
    differences = np.asarray(slope_differences)
    ci = bootstrap_mean(differences, 0.95)
    pooled_block = float(np.polyfit(
        data.loc[data["family"] == 0, "f_damage"], data.loc[data["family"] == 0, "ds"], 1
    )[0])
    pooled_noise = float(np.polyfit(
        data.loc[data["family"] == 1, "f_damage"], data.loc[data["family"] == 1, "ds"], 1
    )[0])
    pooled_common = (pooled_block + pooled_noise) / 2
    mean_diff = float(differences.mean())
    strong = bool(
        (ci[0] > 0 or ci[1] < 0)
        and abs(mean_diff) > 0.25 * abs(pooled_common)
    )
    return {
        "pooled_ols_f_damage": float(coefficients[1]),
        "pooled_ols_family": float(coefficients[2]),
        "pooled_ols_interaction": float(coefficients[3]),
        "run_slopes": slopes,
        "mean_slope_difference": mean_diff,
        "slope_difference_bootstrap_95_ci": ci,
        "pooled_block_slope": pooled_block,
        "pooled_noise_slope": pooled_noise,
        "pooled_common_slope": pooled_common,
        "relative_slope_difference": abs(mean_diff) / (abs(pooled_common) + 1e-12),
        "strong_interaction": strong,
    }


def cross_family_regression(pairs: pd.DataFrame) -> dict:
    """Frozen secondary model: D_S ~ z(KL) + z(NLL) + family + fixed effects."""
    rows = []
    for pair in pairs.to_dict("records"):
        rows.extend([
            {
                "run_id": pair["run_id"], "step": pair["step"], "layer": pair["layer"],
                "family": 0.0, "kl": pair["block_kl"],
                "nll_damage": pair["block_nll_damage"], "ds": pair["block_ds"],
            },
            {
                "run_id": pair["run_id"], "step": pair["step"], "layer": pair["layer"],
                "family": 1.0, "kl": pair["noise_kl"],
                "nll_damage": pair["noise_nll_damage"], "ds": pair["noise_ds"],
            },
        ])
    data = pd.DataFrame(rows)
    for column in ["kl", "nll_damage"]:
        data[f"z_{column}"] = (
            (data[column] - data[column].mean()) / data[column].std(ddof=0)
        )
    fixed = pd.get_dummies(
        data[["run_id", "step", "layer"]].astype(str), drop_first=True, dtype=float
    )
    design = np.column_stack([
        np.ones(len(data)), data["z_kl"], data["z_nll_damage"], data["family"], fixed
    ])
    coefficients = np.linalg.lstsq(design, data["ds"].to_numpy(float), rcond=None)[0]

    leave_one_run_out = []
    for omitted in RUNS:
        subset = data[data["run_id"] != omitted].copy()
        subset_fixed = pd.get_dummies(
            subset[["run_id", "step", "layer"]].astype(str), drop_first=True, dtype=float
        )
        subset_design = np.column_stack([
            np.ones(len(subset)), subset["z_kl"], subset["z_nll_damage"],
            subset["family"], subset_fixed
        ])
        subset_coefficients = np.linalg.lstsq(
            subset_design, subset["ds"].to_numpy(float), rcond=None
        )[0]
        leave_one_run_out.append({
            "omitted_run_id": int(omitted),
            "family_coefficient": float(subset_coefficients[3]),
        })
    return {
        "formula": "D_S ~ z(KL) + z(NLL_damage) + family + run + checkpoint + layer",
        "observations": int(len(data)),
        "design_rank": int(np.linalg.matrix_rank(design)),
        "design_columns": int(design.shape[1]),
        "condition_number": float(np.linalg.cond(design)),
        "coefficient_z_kl": float(coefficients[1]),
        "coefficient_z_nll_damage": float(coefficients[2]),
        "coefficient_family_noise": float(coefficients[3]),
        "leave_one_run_out": leave_one_run_out,
    }


def monotonicity(noise: pd.DataFrame) -> dict:
    rows = []
    for key, group in noise.groupby(["run_id", "step", "layer"]):
        ordered = group.sort_values("beta")
        rows.append({
            "run_id": key[0], "step": key[1], "layer": key[2],
            "kl_nondecreasing": bool(np.all(np.diff(ordered["kl"]) >= 0)),
            "nll_nondecreasing": bool(np.all(np.diff(ordered["nll_damage"]) >= 0)),
        })
    frame = pd.DataFrame(rows)
    return {
        "groups": len(frame),
        "kl_nondecreasing_fraction": float(frame["kl_nondecreasing"].mean()),
        "nll_nondecreasing_fraction": float(frame["nll_nondecreasing"].mean()),
        "both_nondecreasing_fraction": float(
            (frame["kl_nondecreasing"] & frame["nll_nondecreasing"]).mean()
        ),
        "rows": rows,
    }


def weakest_evidence(sign: dict, within_a: pd.DataFrame, pairs: pd.DataFrame) -> dict:
    run_delta = max(sign["run_deltas"], key=lambda row: row["delta_s"])
    checkpoint = within_a.groupby("step")["directional_ds_contrast"].mean()
    layer = pairs.groupby("layer")["family_residual"].mean()
    work = pairs.copy()
    work["damage_quartile"] = pd.qcut(work["block_kl"], 4, labels=False, duplicates="drop")
    quartile = work.groupby("damage_quartile")["family_residual"].mean()
    stratum = work.groupby(["run_id", "step"])["family_residual"].mean()
    worst_key = max(stratum.index, key=lambda key: abs(stratum.loc[key]))
    return {
        "weakest_sign_run": run_delta,
        "weakest_within_family_checkpoint": {
            "step": int(checkpoint.idxmin()), "mean_contrast": float(checkpoint.min())
        },
        "largest_mean_layer_residual": {
            "layer": int(max(layer.index, key=lambda key: abs(layer.loc[key]))),
            "mean_residual": float(layer.loc[max(layer.index, key=lambda key: abs(layer.loc[key]))]),
        },
        "largest_mean_damage_quartile_residual": {
            "quartile": int(max(quartile.index, key=lambda key: abs(quartile.loc[key]))),
            "mean_residual": float(quartile.loc[max(quartile.index, key=lambda key: abs(quartile.loc[key]))]),
        },
        "strongest_family_deviation_stratum": {
            "run_id": int(worst_key[0]), "step": int(worst_key[1]),
            "mean_residual": float(stratum.loc[worst_key]),
        },
    }


def add_blossom(fig: plt.Figure) -> None:
    # Small consistent research mark in the locked top-right position.
    center_x, center_y = 0.975, 0.965
    for dx, dy in [(-0.006, 0), (0.006, 0), (0, -0.008), (0, 0.008)]:
        fig.add_artist(plt.Circle((center_x + dx, center_y + dy), 0.004,
                                 transform=fig.transFigure, color=GOLD, alpha=0.8))


def style_axis(ax: plt.Axes) -> None:
    ax.grid(True, color=GRID, linewidth=0.8, alpha=0.7)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)


def create_figures(
    noise: pd.DataFrame, block: pd.DataFrame, pairs: pd.DataFrame,
    cross: dict, weakest: dict
) -> None:
    out = ARC_ROOT / "figures"
    out.mkdir(exist_ok=True)
    plt.rcParams.update({"font.size": 10, "axes.titlesize": 11, "axes.labelsize": 10})

    # Figure 1: two ECDF panels with rugs.
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.3))
    for ax, column, label in zip(axes, ["kl", "nll_damage"], ["KL damage", "NLL damage"]):
        for frame, color, family, linestyle in [
            (block, BLUE, "Block deletion", "-"),
            (noise, ORANGE, "Activation noise", "--"),
        ]:
            values = np.sort(frame[column].to_numpy())
            y = np.arange(1, len(values) + 1) / len(values)
            ax.plot(values, y, color=color, linestyle=linestyle, linewidth=2, label=family)
            ax.plot(values, np.full_like(values, -0.025), "|", color=color, alpha=0.22)
        ax.set_xlabel(label)
        ax.set_ylabel("Empirical cumulative fraction")
        ax.set_ylim(-0.05, 1.02)
        style_axis(ax)
    axes[0].legend(frameon=False, loc="lower right")
    fig.suptitle("Intervention-family functional-damage support", color=INK)
    fig.text(0.5, 0.92, f"Block n={len(block)} cells; activation-noise n={len(noise)} cells",
             ha="center", color="#666666")
    add_blossom(fig)
    fig.tight_layout(rect=(0, 0, 1, 0.90))
    fig.savefig(out / "fig1_family_damage_support.png", dpi=240)
    plt.close(fig)

    # Figure 2: relationship by checkpoint.
    fig, axes = plt.subplots(1, 3, figsize=(12, 4.2), sharex=True, sharey=True)
    for ax, step in zip(axes, STEPS):
        b = block[block["step"] == step]
        n = noise[noise["step"] == step]
        ax.scatter(b["kl"], b["top1_damage"], s=26, color=BLUE, marker="o",
                   alpha=0.55, label="Block deletion")
        ax.scatter(n["kl"], n["top1_damage"], s=28, facecolors="none",
                   edgecolors=ORANGE, marker="^", alpha=0.65, label="Activation noise")
        ax.set_title(f"step {step:,}")
        ax.set_xlabel("KL damage")
        style_axis(ax)
    axes[0].set_ylabel("Top-1 damage $D_S=1-S$")
    axes[0].legend(frameon=False, loc="lower right")
    fig.suptitle("Top-1 damage versus functional damage", color=INK)
    fig.text(0.5, 0.92, "Individual run-layer-strength cells; common axes across checkpoints",
             ha="center", color="#666666")
    add_blossom(fig)
    fig.tight_layout(rect=(0, 0, 1, 0.90))
    fig.savefig(out / "fig2_ds_vs_functional_damage.png", dpi=240)
    plt.close(fig)

    # Figure 3: paired slopes by run.
    fig, axes = plt.subplots(1, 5, figsize=(13, 4), sharey=True)
    for ax, run_id in zip(axes, RUNS):
        subset = pairs[pairs["run_id"] == run_id]
        for row in subset.to_dict("records"):
            ax.plot([0, 1], [row["block_ds"], row["noise_ds"]], color="#BBBBBB", alpha=0.45)
        medians = [subset["block_ds"].median(), subset["noise_ds"].median()]
        ax.plot([0, 1], medians, color=INK, marker="D", linewidth=2.2)
        ax.scatter(np.zeros(len(subset)), subset["block_ds"], color=BLUE, s=18, alpha=0.55)
        ax.scatter(np.ones(len(subset)), subset["noise_ds"], facecolors="none",
                   edgecolors=ORANGE, marker="^", s=22, alpha=0.7)
        ax.set_xticks([0, 1], ["Block", "Noise"])
        ax.set_title(f"seed{run_id}\nn={len(subset)}")
        style_axis(ax)
    axes[0].set_ylabel("Top-1 damage $D_S$")
    fig.suptitle("Cross-family damage-matched pairs", color=INK)
    fig.text(0.5, 0.92, "Thin lines are matched run-checkpoint-layer pairs; diamonds are medians",
             ha="center", color="#666666")
    add_blossom(fig)
    fig.tight_layout(rect=(0, 0, 1, 0.90))
    fig.savefig(out / "fig3_cross_family_matched.png", dpi=240)
    plt.close(fig)

    # Figure 4: run-level residual forest and equivalence band.
    run_stats = pd.DataFrame(cross["run_statistics"])
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    bound = cross["equivalence_bound"]
    ax.axvspan(-bound, bound, color=GOLD, alpha=0.18, label="Frozen equivalence band")
    ax.axvline(0, color=INK, linewidth=1)
    y = np.arange(len(run_stats))
    ax.scatter(run_stats["median_residual"], y, color=BLUE, s=48, zorder=3)
    aggregate_y = len(run_stats) + 0.8
    ax.errorbar(
        cross["mean_run_median_residual"], aggregate_y,
        xerr=[[cross["mean_run_median_residual"] - cross["bootstrap_95_ci"][0]],
              [cross["bootstrap_95_ci"][1] - cross["mean_run_median_residual"]]],
        fmt="D", color=ORANGE, capsize=4, label="Aggregate 95% interval"
    )
    ax.set_yticks(list(y) + [aggregate_y],
                  [f"seed{x}" for x in run_stats["run_id"]] + ["aggregate"])
    ax.set_xlabel("Family residual: $D_S$(noise) - $D_S$(block)")
    ax.set_title("Residual intervention-family effect")
    ax.legend(frameon=False, loc="best")
    style_axis(ax)
    add_blossom(fig)
    fig.tight_layout()
    fig.savefig(out / "fig4_family_residual_forest.png", dpi=240)
    plt.close(fig)

    # Figure 5: prespecified strongest run/checkpoint counterevidence.
    worst = weakest["strongest_family_deviation_stratum"]
    subset = pairs[(pairs["run_id"] == worst["run_id"]) & (pairs["step"] == worst["step"])]
    fig, ax = plt.subplots(figsize=(7.6, 4.6))
    ax.axhspan(-cross["equivalence_bound"], cross["equivalence_bound"], color=GOLD, alpha=0.18)
    ax.axhline(0, color=INK, linewidth=1)
    ax.scatter(subset["layer"], subset["family_residual"], color=ORANGE,
               edgecolor=INK, marker="^", s=58)
    ax.set_xticks(sorted(subset["layer"].unique()))
    ax.set_xlabel("Interior layer")
    ax.set_ylabel("Matched family residual")
    ax.set_title("Strongest cross-family deviation stratum")
    fig.text(0.5, 0.91, f"seed{worst['run_id']}, step {worst['step']:,}; selected by max absolute stratum mean",
             ha="center", color="#666666")
    style_axis(ax)
    add_blossom(fig)
    fig.tight_layout(rect=(0, 0, 1, 0.89))
    fig.savefig(out / "fig5_strongest_counterevidence.png", dpi=240)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["final"], default="final")
    parser.parse_args()
    config = yaml.safe_load((ARC_ROOT / "configs" / "confirmatory.yaml").read_text())
    noise_raw, bin_raw, noise_baselines, payloads = load_noise()
    block_raw, block_baselines = load_block()
    noise = aggregate_noise(noise_raw)
    block = aggregate_block(block_raw)
    confidence = aggregate_confidence(bin_raw)

    # Exact shared-baseline integrity.
    baseline = noise_baselines.merge(
        block_baselines, on=["run_id", "step", "evaluation_seed"], suffixes=("_noise", "_block")
    )
    baseline["abs_nll_diff"] = (
        baseline["baseline_nll_noise"] - baseline["baseline_nll_block"]
    ).abs()

    within_a = greedy_magnitude_matched(noise)
    within_b = greedy_damage_matched(noise)
    cross_pairs, discards = match_cross_family(noise, block, 0.10)
    sensitivity = {}
    for relative in [0.05, 0.15]:
        pairs, discarded = match_cross_family(noise, block, relative)
        sensitivity[str(relative)] = {
            "summary": cross_family_summary(pairs, config["family_equivalence_bound"]),
            "matched_pairs": len(pairs), "discarded": len(discarded),
        }

    sign = sign_test(noise)
    sign_noncatastrophic = sign_test(noise[~noise["catastrophic"]])
    within_a_summary = pair_summary(within_a)
    within_b_summary = pair_summary(within_b)
    cross = cross_family_summary(cross_pairs, config["family_equivalence_bound"])
    quality = matching_quality(cross_pairs, discards, noise, block)
    interaction = interaction_analysis(cross_pairs)
    regression = cross_family_regression(cross_pairs)
    confidence_summary = confidence_test(confidence)
    monotonic = monotonicity(noise)
    weakest = weakest_evidence(sign, within_a, cross_pairs)

    within_a_pass = bool(
        within_a_summary["positive_runs"] >= 4
        and within_a_summary["bootstrap_95_ci"][0] > 0
    )
    within_b_weakened = bool(
        within_b_summary["bootstrap_95_ci"][0] <= 0 <= within_b_summary["bootstrap_95_ci"][1]
        and abs(within_b_summary["mean_run_median"])
        < 0.25 * abs(within_a_summary["mean_run_median"])
    )
    family_go = bool(
        sign["pass"] and within_a_pass and within_b_weakened
        and quality["match_quality_pass"] and cross["equivalence_pass"]
        and not interaction["strong_interaction"]
    )
    sign_values = np.asarray([row["delta_s"] for row in sign["run_deltas"]])
    decisive_sign_fail = bool(
        ((sign_values < 0).sum() <= 1 and sign["bootstrap_95_ci"][1] >= 0)
        or ((sign_values > 0).sum() >= 4 and sign["bootstrap_95_ci"][0] > 0)
    )
    family_kill = bool(
        decisive_sign_fail
        or (
            quality["match_quality_pass"]
            and abs(cross["mean_run_median_residual"]) >= 0.021484375
            and (cross["bootstrap_95_ci"][0] > 0 or cross["bootstrap_95_ci"][1] < 0)
        )
    )
    verdict = "FAMILY-GO" if family_go else ("FAMILY-KILL" if family_kill else "FAMILY-PARTIAL")

    processed = ARC_ROOT / "processed"
    diagnostics = ARC_ROOT / "matching_diagnostics"
    results = ARC_ROOT / "results"
    for directory in [processed, diagnostics, results]:
        directory.mkdir(exist_ok=True)
    noise_raw.to_csv(processed / "noise_raw_metrics.csv", index=False)
    noise.to_csv(processed / "noise_cells.csv", index=False)
    block.to_csv(processed / "block_anchor_cells.csv", index=False)
    confidence.to_csv(processed / "noise_confidence_bins.csv", index=False)
    baseline.to_csv(processed / "baseline_consistency.csv", index=False)
    within_a.to_csv(diagnostics / "within_family_magnitude_matched.csv", index=False)
    within_b.to_csv(diagnostics / "within_family_damage_matched.csv", index=False)
    cross_pairs.to_csv(diagnostics / "cross_family_pairs.csv", index=False)
    discards.to_csv(diagnostics / "cross_family_discards.csv", index=False)

    data_quality = {
        "raw_noise_rows": len(noise_raw),
        "expected_raw_noise_rows": 4050,
        "aggregated_noise_cells": len(noise),
        "expected_aggregated_noise_cells": 450,
        "block_anchor_cells": len(block),
        "expected_block_anchor_cells": 150,
        "raw_composite_key_duplicates": int(noise_raw.duplicated([
            "run_id", "step", "evaluation_seed", "layer", "beta", "direction_id"
        ]).sum()),
        "aggregated_key_duplicates": int(noise.duplicated([
            "run_id", "step", "layer", "beta"
        ]).sum()),
        "nonfinite_noise_metrics": int((~np.isfinite(noise[[
            "top1_agreement", "nll_damage", "kl", "activation_relative_magnitude"
        ]])).sum().sum()),
        "catastrophic_noise_cells": int(noise["catastrophic"].sum()),
        "max_shared_baseline_nll_diff": float(baseline["abs_nll_diff"].max()),
        "all_harness_records_pass": bool(all(
            checkpoint["harness_validation"]["pass"]
            for payload in payloads for checkpoint in payload["checkpoints"]
        )),
    }
    data_quality["pass"] = bool(
        data_quality["raw_noise_rows"] == data_quality["expected_raw_noise_rows"]
        and data_quality["aggregated_noise_cells"] == data_quality["expected_aggregated_noise_cells"]
        and data_quality["block_anchor_cells"] == data_quality["expected_block_anchor_cells"]
        and data_quality["raw_composite_key_duplicates"] == 0
        and data_quality["aggregated_key_duplicates"] == 0
        and data_quality["nonfinite_noise_metrics"] == 0
        and data_quality["max_shared_baseline_nll_diff"] == 0.0
        and data_quality["all_harness_records_pass"]
    )

    total_runtime = float(sum(
        checkpoint["runtime_seconds"] for payload in payloads for checkpoint in payload["checkpoints"]
    ))
    peak_cuda = int(max(
        checkpoint["peak_cuda_bytes"] for payload in payloads for checkpoint in payload["checkpoints"]
    ))
    summary = {
        "arc": "ARC-20260826-5060-005",
        "intervention_family": "norm_controlled_additive_activation_noise",
        "test_a_sign": sign,
        "test_a_sign_excluding_catastrophic_cells": sign_noncatastrophic,
        "test_b_magnitude_matched": within_a_summary,
        "test_b_damage_matched": within_b_summary,
        "test_b_functional_alignment_pass": within_a_pass,
        "test_b_raw_magnitude_weakened": within_b_weakened,
        "test_c_cross_family": cross,
        "matching_quality": quality,
        "matching_sensitivity": sensitivity,
        "interaction": interaction,
        "cross_family_regression": regression,
        "confidence_control": confidence_summary,
        "monotonicity": monotonic,
        "weakest_evidence": weakest,
        "data_quality": data_quality,
        "decisive_sign_fail": decisive_sign_fail,
        "verdict": verdict,
        "resources": {
            "confirmatory_checkpoint_runtime_seconds_sum": total_runtime,
            "peak_cuda_bytes": peak_cuda,
            "api_cost_usd": 0,
            "external_compute_cost_usd": 0,
        },
        "raw_sha256": {
            path.name: sha256(path)
            for path in sorted((ARC_ROOT / "raw" / "confirmatory").glob("*.json"))
        },
    }
    target = results / "family_robustness_summary.json"
    target.write_text(json.dumps(summary, indent=2, default=json_scalar), encoding="utf-8")
    create_figures(noise, block, cross_pairs, cross, weakest)
    print(json.dumps({
        "verdict": verdict,
        "test_a": sign,
        "test_a_excluding_catastrophic": sign_noncatastrophic,
        "within_a": within_a_summary,
        "within_b": within_b_summary,
        "cross_family": cross,
        "matching_quality": quality,
        "interaction": interaction,
        "cross_family_regression": regression,
        "weakest": weakest,
        "data_quality": data_quality,
    }, indent=2, default=json_scalar))


if __name__ == "__main__":
    main()
