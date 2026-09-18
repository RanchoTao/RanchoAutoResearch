#!/usr/bin/env python3
"""Analyze ARC-011 with frozen ARC-003/004 statistics and matching."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
CONFIG = yaml.safe_load((ROOT / "configs" / "cross_corpus.yaml").read_text(encoding="utf-8"))
RUN_IDS = CONFIG["all_runs"]
EARLY, MIDDLE, LATE = CONFIG["checkpoint_steps"]
BOOTSTRAP_SEED = CONFIG["bootstrap_seed"]
BOOTSTRAP_SAMPLES = CONFIG["bootstrap_samples"]


def load_arc004_analysis():
    path = ROOT.parent / "arc_20260826_5060_004" / "src" / "analyze_mechanism.py"
    spec = importlib.util.spec_from_file_location("arc004_frozen_analysis", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import frozen analysis: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ARC_ROOT = ROOT
    return module


BASE = load_arc004_analysis()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def bootstrap_mean(values: list[float], seed: int = BOOTSTRAP_SEED) -> list[float]:
    array = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    draws = rng.choice(array, size=(BOOTSTRAP_SAMPLES, len(array)), replace=True).mean(axis=1)
    return [float(x) for x in np.quantile(draws, [0.025, 0.975])]


def checkpoint_core(checkpoint: dict) -> dict:
    eval_rows = []
    for evaluation in checkpoint["evaluation_results"]:
        cells = [row for row in evaluation["interventions"] if float(row["alpha"]) == 1.0]
        eval_rows.append({
            "evaluation_seed": int(evaluation["evaluation_seed"]),
            "baseline_nll": float(evaluation["baseline_nll"]),
            "baseline_confidence": float(evaluation["baseline_top1_confidence"]),
            "baseline_entropy": float(evaluation["baseline_entropy"]),
            "agreement": float(np.mean([row["top1_agreement"] for row in cells])),
            "nll_damage": float(np.mean([row["nll_damage"] for row in cells])),
            "kl": float(np.mean([row["kl"] for row in cells])),
        })
    return {
        "step": int(checkpoint["step"]),
        "baseline_nll": float(np.mean([row["baseline_nll"] for row in eval_rows])),
        "baseline_confidence": float(np.mean([row["baseline_confidence"] for row in eval_rows])),
        "baseline_entropy": float(np.mean([row["baseline_entropy"] for row in eval_rows])),
        "agreement": float(np.mean([row["agreement"] for row in eval_rows])),
        "nll_damage": float(np.mean([row["nll_damage"] for row in eval_rows])),
        "kl": float(np.mean([row["kl"] for row in eval_rows])),
        "eval_rows": eval_rows,
    }


def build_core(payloads: list[dict]) -> tuple[list[dict], list[dict]]:
    included = []
    excluded = []
    for payload in sorted(payloads, key=lambda row: row["training_run_id"]):
        run_id = int(payload["training_run_id"])
        checkpoints = {int(row["step"]): checkpoint_core(row) for row in payload["checkpoints"]}
        missing = sorted({EARLY, LATE} - set(checkpoints))
        if missing:
            excluded.append({"run_id": run_id, "reason": f"missing endpoints {missing}"})
            continue
        early, late = checkpoints[EARLY], checkpoints[LATE]
        if max(early["baseline_nll"], late["baseline_nll"]) > CONFIG["competence_max_nll"]:
            excluded.append({
                "run_id": run_id,
                "reason": "competence gate",
                "early_nll": early["baseline_nll"],
                "late_nll": late["baseline_nll"],
            })
            continue
        early_eval = {row["evaluation_seed"]: row for row in early["eval_rows"]}
        late_eval = {row["evaluation_seed"]: row for row in late["eval_rows"]}
        eval_deltas = [
            late_eval[seed]["agreement"] - early_eval[seed]["agreement"]
            for seed in CONFIG["evaluation_seeds"]
        ]
        included.append({
            "run_id": run_id,
            "stage": payload["stage"],
            "early_s": early["agreement"],
            "late_s": late["agreement"],
            "delta_s": late["agreement"] - early["agreement"],
            "early_intact_nll": early["baseline_nll"],
            "late_intact_nll": late["baseline_nll"],
            "early_confidence": early["baseline_confidence"],
            "late_confidence": late["baseline_confidence"],
            "delta_nll_damage": late["nll_damage"] - early["nll_damage"],
            "delta_kl": late["kl"] - early["kl"],
            "eval_deltas": eval_deltas,
            "negative_eval_resamples": int(sum(value < 0 for value in eval_deltas)),
        })
    return included, excluded


def core_confidence(payloads: list[dict]) -> pd.DataFrame:
    rows = []
    for payload in payloads:
        run_id = int(payload["training_run_id"])
        by_step: dict[int, list[dict]] = {}
        for checkpoint in payload["checkpoints"]:
            step = int(checkpoint["step"])
            if step not in (EARLY, LATE):
                continue
            pooled = [
                {"count": 0, "agree": 0.0}
                for _ in range(len(CONFIG["confidence_bins"]) - 1)
            ]
            for evaluation in checkpoint["evaluation_results"]:
                for cell in evaluation["interventions"]:
                    if float(cell["alpha"]) != 1.0:
                        continue
                    for bin_index, item in enumerate(cell["confidence_bins"]):
                        if item["agreement"] is None:
                            continue
                        pooled[bin_index]["count"] += int(item["count"])
                        pooled[bin_index]["agree"] += float(item["agreement"]) * int(item["count"])
            by_step[step] = pooled
        if EARLY not in by_step or LATE not in by_step:
            continue
        for index in range(len(CONFIG["confidence_bins"]) - 1):
            early = by_step[EARLY][index]
            late = by_step[LATE][index]
            if min(early["count"], late["count"]) < 100:
                continue
            early_agreement = early["agree"] / early["count"]
            late_agreement = late["agree"] / late["count"]
            rows.append({
                "run_id": run_id,
                "bin_index": index,
                "bin_low": CONFIG["confidence_bins"][index],
                "bin_high": CONFIG["confidence_bins"][index + 1],
                "early_count": early["count"],
                "late_count": late["count"],
                "early_agreement": early_agreement,
                "late_agreement": late_agreement,
                "delta_s": late_agreement - early_agreement,
            })
    return pd.DataFrame(rows)


def summarize_core(core: list[dict], excluded: list[dict]) -> dict:
    values = [row["delta_s"] for row in core]
    loo = [
        float(np.mean([value for j, value in enumerate(values) if j != i]))
        for i in range(len(values))
    ]
    criteria = {
        "at_least_five_eligible_runs": len(core) >= 5,
        "at_least_five_of_six_negative": sum(value < 0 for value in values) >= 5,
        "run_bootstrap_ci_below_zero": bootstrap_mean(values)[1] < 0 if values else False,
        "leave_one_run_out_means_negative": bool(loo) and max(loo) < 0,
        "resampling_stability": sum(row["negative_eval_resamples"] >= 2 for row in core) >= 5,
    }
    return {
        "eligible_runs": len(core),
        "excluded": excluded,
        "negative_runs": int(sum(value < 0 for value in values)),
        "mean_delta_s": float(np.mean(values)) if values else None,
        "median_delta_s": float(np.median(values)) if values else None,
        "std_delta_s": float(np.std(values, ddof=1)) if len(values) > 1 else None,
        "run_bootstrap_95_ci_mean": bootstrap_mean(values) if values else None,
        "leave_one_run_out_mean_range": [min(loo), max(loo)] if loo else None,
        "individual_runs": core,
        "criteria": criteria,
        "pass": all(criteria.values()),
    }


def summarize_confidence(df: pd.DataFrame) -> dict:
    if df.empty:
        return {"pass": False, "eligible_comparisons": 0, "eligible_bins": 0}
    run_means = df.groupby("run_id")["delta_s"].mean()
    ci = bootstrap_mean(run_means.tolist(), seed=BOOTSTRAP_SEED + 1)
    criteria = {
        "at_least_three_bins": int(df["bin_index"].nunique()) >= 3,
        "negative_fraction_at_least_075": float((df["delta_s"] < 0).mean()) >= 0.75,
        "mean_negative": float(df["delta_s"].mean()) < 0,
        "run_bootstrap_ci_below_zero": ci[1] < 0,
    }
    return {
        "eligible_comparisons": int(len(df)),
        "eligible_bins": int(df["bin_index"].nunique()),
        "negative_comparisons": int((df["delta_s"] < 0).sum()),
        "negative_fraction": float((df["delta_s"] < 0).mean()),
        "mean_delta_s": float(df["delta_s"].mean()),
        "median_delta_s": float(df["delta_s"].median()),
        "run_mean_bootstrap_95_ci": ci,
        "per_run_mean_delta_s": [
            {"run_id": int(run_id), "mean_delta_s": float(value)}
            for run_id, value in run_means.items()
        ],
        "criteria": criteria,
        "pass": all(criteria.values()),
    }


def effect_ratio(new_values: list[float], wiki_values: list[float]) -> dict:
    point = abs(float(np.mean(new_values))) / abs(float(np.mean(wiki_values)))
    rng = np.random.default_rng(BOOTSTRAP_SEED + 2)
    new = np.asarray(new_values)
    wiki = np.asarray(wiki_values)
    new_draw = rng.choice(new, size=(BOOTSTRAP_SAMPLES, len(new)), replace=True).mean(axis=1)
    wiki_draw = rng.choice(wiki, size=(BOOTSTRAP_SAMPLES, len(wiki)), replace=True).mean(axis=1)
    ratios = np.abs(new_draw) / np.maximum(np.abs(wiki_draw), 1e-12)
    return {
        "absolute_mean_ratio": point,
        "independent_run_bootstrap_95_ci": [float(x) for x in np.quantile(ratios, [0.025, 0.975])],
        "interpretation": "descriptive; not an equality or universality test",
    }


def create_figures(
    core_df: pd.DataFrame,
    wiki_core: pd.DataFrame,
    a_pairs: pd.DataFrame,
    wiki_a: dict,
    confidence: pd.DataFrame,
    wiki_confidence: pd.DataFrame,
    summary: dict,
) -> None:
    out = ROOT / "figures"
    out.mkdir(exist_ok=True)
    plt.style.use("seaborn-v0_8-whitegrid")
    blue, orange, ink = "#4477AA", "#EE7733", "#222222"

    def add_right_labels(ax, x: float, ys: list[float], labels: list[str], min_gap: float) -> None:
        order = np.argsort(ys)
        placed = np.asarray(ys, dtype=float).copy()
        for previous, current in zip(order[:-1], order[1:]):
            if placed[current] - placed[previous] < min_gap:
                placed[current] = placed[previous] + min_gap
        shift = max(0.0, placed.max() - max(ys) - min_gap)
        placed -= shift
        for y, label, label_y in zip(ys, labels, placed):
            ax.annotate(
                label,
                xy=(x, y),
                xytext=(x + 0.055, label_y),
                fontsize=8,
                va="center",
                arrowprops={"arrowstyle": "-", "color": "#777777", "lw": 0.7},
            )

    merged = wiki_core.merge(core_df[["run_id", "delta_s"]], on="run_id", suffixes=("_wiki", "_new"))
    fig, ax = plt.subplots(figsize=(7.6, 5.0))
    for _, row in merged.iterrows():
        ax.plot([0, 1], [row["delta_s_wiki"], row["delta_s_new"]], color="#999999", lw=1)
        ax.scatter(0, row["delta_s_wiki"], color=blue, marker="o", s=48)
        ax.scatter(1, row["delta_s_new"], color=orange, marker="D", s=44)
    add_right_labels(
        ax,
        1.0,
        merged["delta_s_new"].tolist(),
        [f"seed{int(value)}" for value in merged["run_id"]],
        0.0035,
    )
    ax.axhline(0, color=ink, lw=1)
    ax.set_xlim(-0.05, 1.18)
    ax.set_xticks([0, 1])
    ax.set_xticklabels([])
    ax.text(0, -0.035, "WikiText-2", transform=ax.get_xaxis_transform(), ha="center", va="top")
    ax.text(1, -0.035, "HellaSwag", transform=ax.get_xaxis_transform(), ha="center", va="top")
    ax.set_ylabel("Late − early substitutability (ΔS)")
    ax.set_title("Per-run ΔS by evaluation corpus", pad=28)
    ax.text(0, 1.015, "Six matched Pythia-160M pretraining runs; lower values indicate less late-stage substitutability", transform=ax.transAxes, fontsize=9)
    fig.tight_layout(rect=(0, 0, 1, 0.98))
    fig.savefig(out / "fig1_per_run_delta_s.png", dpi=220)
    plt.close(fig)

    new_a_runs = a_pairs.groupby("run_id")["directional_ds_contrast"].median().rename("new")
    wiki_a_runs = pd.DataFrame(wiki_a["run_statistics"]).set_index("run_id")["median_contrast"].rename("wiki")
    pairs = pd.concat([wiki_a_runs, new_a_runs], axis=1).dropna().sort_index()
    fig, ax = plt.subplots(figsize=(7.6, 5.0))
    for run_id, row in pairs.iterrows():
        ax.plot([0, 1], [row["wiki"], row["new"]], color="#999999", lw=1)
        ax.scatter(0, row["wiki"], color=blue, marker="o", s=48)
        ax.scatter(1, row["new"], color=orange, marker="D", s=44)
    add_right_labels(
        ax,
        1.0,
        pairs["new"].tolist(),
        [f"seed{int(value)}" for value in pairs.index],
        0.0018,
    )
    ax.axhline(0, color=ink, lw=1)
    ax.set_xlim(-0.05, 1.18)
    ax.set_xticks([0, 1])
    ax.set_xticklabels([])
    ax.text(0, -0.035, "WikiText-2", transform=ax.get_xaxis_transform(), ha="center", va="top")
    ax.text(1, -0.035, "HellaSwag", transform=ax.get_xaxis_transform(), ha="center", va="top")
    ax.set_ylabel("Run-median magnitude-matched damage contrast")
    ax.set_title("Magnitude-matched functional-damage contrast", pad=28)
    ax.text(0, 1.015, "Same frozen calipers; positive values support functional-damage alignment", transform=ax.transAxes, fontsize=9)
    fig.tight_layout(rect=(0, 0, 1, 0.98))
    fig.savefig(out / "fig2_magnitude_matched_contrast.png", dpi=220)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.2, 5.1))
    rng = np.random.default_rng(11)
    for corpus, frame, color, marker, offset in [
        ("WikiText-2", wiki_confidence, blue, "o", -0.12),
        ("HellaSwag", confidence, orange, "D", 0.12),
    ]:
        for bin_index, group in frame.groupby("bin_index"):
            x = np.full(len(group), bin_index + offset) + rng.uniform(-0.035, 0.035, len(group))
            ax.scatter(x, group["delta_s"], color=color, marker=marker, alpha=0.62, s=28, label=corpus if bin_index == frame["bin_index"].min() else None)
            ax.plot(bin_index + offset, group["delta_s"].mean(), marker="_", color=ink, markersize=14)
    ax.axhline(0, color=ink, lw=1)
    labels = [f"{CONFIG['confidence_bins'][i]:.2g}–{CONFIG['confidence_bins'][i+1]:.2g}" for i in range(5)]
    ax.set_xticks(range(5), labels)
    ax.set_xlabel("Frozen intact-confidence bin")
    ax.set_ylabel("Late − early agreement within bin")
    ax.set_title("Fixed-bin confidence control by corpus", pad=28)
    ax.text(0, 1.015, "Points are run-bin comparisons; short black marks are corpus-bin means", transform=ax.transAxes, fontsize=9)
    ax.legend(frameon=False)
    fig.tight_layout(rect=(0, 0, 1, 0.98))
    fig.savefig(out / "fig3_confidence_control.png", dpi=220)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(9.4, 4.5))
    panels = [
        (axes[0], "Core ΔS", [
            ("WikiText-2", summary["reference"]["wiki_mean_delta_s"], summary["reference"]["wiki_ci_delta_s"], blue, "o", 9),
            ("HellaSwag", summary["core_replication"]["mean_delta_s"], summary["core_replication"]["run_bootstrap_95_ci_mean"], orange, "D", len(core_df)),
        ]),
        (axes[1], "Magnitude-matched contrast", [
            ("WikiText-2", wiki_a["mean_run_median_contrast"], wiki_a["run_bootstrap_95_ci_mean"], blue, "o", 6),
            ("HellaSwag", summary["damage_alignment"]["magnitude_matched"]["mean_run_median_contrast"], summary["damage_alignment"]["magnitude_matched"]["run_bootstrap_95_ci_mean"], orange, "D", 6),
        ]),
    ]
    for ax, title, items in panels:
        for y, (label, point, ci, color, marker, n) in enumerate(items):
            ax.errorbar(point, y, xerr=[[point-ci[0]], [ci[1]-point]], fmt=marker, color=color, capsize=4, label=f"{label} (N={n})")
        ax.axvline(0, color=ink, lw=1)
        ax.set_yticks([0, 1], [items[0][0], items[1][0]])
        ax.set_title(title)
        ax.set_xlabel("Run-level mean with bootstrap 95% CI")
    fig.suptitle("Cross-corpus effect-size summary", y=1.02)
    fig.tight_layout()
    fig.savefig(out / "fig4_effect_size_summary.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    for directory in ["processed", "matching_diagnostics", "results", "figures"]:
        (ROOT / directory).mkdir(exist_ok=True)

    scalar, raw_bins, payloads = BASE.load_rows(RUN_IDS)
    interventions = BASE.aggregate_interventions(scalar)
    bins = BASE.aggregate_bins(raw_bins)
    a_pairs = BASE.all_matches(interventions, "A")
    b_pairs = BASE.all_matches(interventions, "B")
    a_summary = BASE.summarize_pairs(a_pairs)
    b_summary = BASE.summarize_pairs(b_pairs)
    feasibility = BASE.feasibility_summary(
        a_pairs[a_pairs["run_id"].isin(CONFIG["pilot_runs"])],
        b_pairs[b_pairs["run_id"].isin(CONFIG["pilot_runs"])],
    )

    core, excluded = build_core(payloads)
    core_summary = summarize_core(core, excluded)
    confidence = core_confidence(payloads)
    confidence_summary = summarize_confidence(confidence)

    arc003 = json.loads((REPO / "meta_arc05/ARC-20260826-5060-003/results/independent_run_summary.json").read_text(encoding="utf-8"))
    wiki_individual = arc003["primary"]["individual_runs"]
    wiki_values = [float(row["delta_agreement"]) for row in wiki_individual]
    wiki_core = pd.DataFrame([
        {"run_id": int(row["run_id"]), "delta_s": float(row["delta_agreement"])}
        for row in wiki_individual if int(row["run_id"]) in RUN_IDS
    ])
    arc004 = json.loads((ROOT.parent / "arc_20260826_5060_004/results/mechanism_summary.json").read_text(encoding="utf-8"))
    wiki_a = arc004["experiment_a_magnitude_matched"]
    wiki_confidence = pd.DataFrame([
        {
            "run_id": int(row["run_id"]),
            "bin_index": int(row["bin_index"]),
            "delta_s": float(row["delta"]),
        }
        for row in arc003["primary"]["confidence_bin_comparisons"]
        if int(row["run_id"]) in RUN_IDS
    ])

    damage_pass = bool(
        a_summary["positive_runs"] >= 5
        and a_summary["run_bootstrap_95_ci_mean"][0] > 0
        and (
            b_summary["run_bootstrap_95_ci_mean"][0] <= 0 <= b_summary["run_bootstrap_95_ci_mean"][1]
            or abs(b_summary["mean_run_median_contrast"]) < 0.5 * abs(a_summary["mean_run_median_contrast"])
        )
    )
    comparable = bool(
        core_summary["eligible_runs"] >= 5
        and confidence_summary.get("eligible_bins", 0) >= 3
        and all(row["harness_validation"]["pass"] for payload in payloads for row in payload["checkpoints"])
    )
    if not comparable:
        verdict = "CORPUS-NONCOMPARABLE"
    elif core_summary["pass"] and damage_pass and confidence_summary["pass"]:
        verdict = "CORPUS-GO"
    elif core_summary["pass"]:
        verdict = "CORPUS-PARTIAL"
    else:
        verdict = "CORPUS-NO"

    new_values = [row["delta_s"] for row in core]
    profile = json.loads((ROOT / "corpus_profile.json").read_text(encoding="utf-8"))
    comparability = {
        "evaluation_tokens_per_checkpoint_both": profile["evaluation_tokens_per_checkpoint"],
        "sequence_length_both": CONFIG["sequence_length"],
        "full_corpus_profiles": {
            "wikitext2": profile["reference_wikitext2"],
            "hellaswag": profile["selected"],
        },
        "hellaswag_endpoint_intact_nll_mean": {
            "early": float(np.mean([row["early_intact_nll"] for row in core])),
            "late": float(np.mean([row["late_intact_nll"] for row in core])),
        },
        "hellaswag_endpoint_confidence_mean": {
            "early": float(np.mean([row["early_confidence"] for row in core])),
            "late": float(np.mean([row["late_confidence"] for row in core])),
        },
        "hellaswag_intervention_ranges": {
            "kl": [float(interventions["kl"].min()), float(interventions["kl"].max())],
            "nll_damage": [float(interventions["nll_damage"].min()), float(interventions["nll_damage"].max())],
            "top1_damage": [float(interventions["top1_damage"].min()), float(interventions["top1_damage"].max())],
            "activation_relative_magnitude": [float(interventions["activation_relative_magnitude"].min()), float(interventions["activation_relative_magnitude"].max())],
        },
    }

    summary = {
        "arc": CONFIG["arc"],
        "selected_corpus": profile["selected_corpus"],
        "verdict": verdict,
        "core_replication": core_summary,
        "effect_size_ratio": effect_ratio(new_values, wiki_values),
        "damage_alignment": {
            "feasibility": feasibility,
            "magnitude_matched": a_summary,
            "damage_matched": b_summary,
            "pass": damage_pass,
        },
        "confidence_control": confidence_summary,
        "comparability": comparability,
        "reference": {
            "wiki_mean_delta_s": float(np.mean(wiki_values)),
            "wiki_median_delta_s": float(np.median(wiki_values)),
            "wiki_ci_delta_s": arc003["primary"]["bootstrap_95_ci_mean_delta"],
            "wiki_negative_runs": arc003["primary"]["negative_runs"],
            "wiki_runs": arc003["primary"]["eligible_runs"],
            "wiki_magnitude_matched": wiki_a,
        },
        "assay_integrity": {
            "all_checkpoint_harnesses_pass": all(row["harness_validation"]["pass"] for payload in payloads for row in payload["checkpoints"]),
            "all_top1_rules_canonical": all(payload["top1_rule"] == CONFIG["top1_rule"] for payload in payloads),
            "all_corpus_hashes_match": len({payload["corpus"]["text_sha256"] for payload in payloads}) == 1,
            "all_manifest_hashes_match": len({payload["corpus"]["manifest"]["sha256"] for payload in payloads}) == 1,
            "statistical_unit": "independent pretraining run",
            "pass": comparable,
        },
        "resources": {
            "checkpoint_runtime_seconds_sum": float(sum(row["runtime_seconds"] for payload in payloads for row in payload["checkpoints"])),
            "peak_cuda_bytes": int(max(row["peak_cuda_bytes"] for payload in payloads for row in payload["checkpoints"])),
            "api_cost_usd": 0,
            "external_compute_cost_usd": 0,
            "downloads_bytes": 0,
            "network_bytes": 0,
        },
        "raw_sha256": {
            path.name: sha256(path) for path in sorted((ROOT / "raw").glob("*.json"))
        },
    }

    interventions.to_csv(ROOT / "processed" / "intervention_metrics.csv", index=False)
    bins.to_csv(ROOT / "processed" / "confidence_bin_metrics.csv", index=False)
    pd.DataFrame(core).drop(columns=["eval_deltas"]).to_csv(ROOT / "processed" / "core_run_results.csv", index=False)
    confidence.to_csv(ROOT / "processed" / "core_confidence_comparisons.csv", index=False)
    a_pairs.to_csv(ROOT / "matching_diagnostics" / "magnitude_matched_pairs.csv", index=False)
    b_pairs.to_csv(ROOT / "matching_diagnostics" / "damage_matched_pairs.csv", index=False)
    (ROOT / "results" / "cross_corpus_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (ROOT / "results" / "corpus_comparability.json").write_text(json.dumps(comparability, indent=2) + "\n", encoding="utf-8")

    with (ROOT / "run_manifest.csv").open("w", encoding="utf-8", newline="") as handle:
        fieldnames = ["run_id", "stage", "model", "checkpoints", "status", "runtime_seconds", "peak_cuda_bytes", "raw_path", "raw_sha256"]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for payload in sorted(payloads, key=lambda row: row["training_run_id"]):
            path = ROOT / "raw" / f"pythia-160m-seed{payload['training_run_id']}.json"
            writer.writerow({
                "run_id": payload["training_run_id"],
                "stage": payload["stage"],
                "model": payload["model"],
                "checkpoints": ";".join(str(row["step"]) for row in payload["checkpoints"]),
                "status": "complete",
                "runtime_seconds": sum(row["runtime_seconds"] for row in payload["checkpoints"]),
                "peak_cuda_bytes": max(row["peak_cuda_bytes"] for row in payload["checkpoints"]),
                "raw_path": str(path.relative_to(ROOT)),
                "raw_sha256": sha256(path),
            })

    create_figures(
        pd.DataFrame(core), wiki_core, a_pairs, wiki_a, confidence, wiki_confidence, summary
    )
    print(json.dumps({
        "verdict": verdict,
        "core": core_summary,
        "effect_size_ratio": summary["effect_size_ratio"],
        "damage_alignment_pass": damage_pass,
        "confidence_control": confidence_summary,
        "resources": summary["resources"],
        "output": str(ROOT / "results" / "cross_corpus_summary.json"),
    }, indent=2))


if __name__ == "__main__":
    main()
