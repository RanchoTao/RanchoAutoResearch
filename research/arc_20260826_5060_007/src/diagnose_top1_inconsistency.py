"""Quantify the ARC-006 mixed top-1 tie-breaking inconsistency."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ARC_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ARC_ROOT.parents[1]
ARC006 = ARC_ROOT.parent / "arc_20260826_5060_006"
RUNS = [2, 3, 5, 6, 8]
TOPK_SEAL_COMMIT = "1a6892b"
BOUND = 0.0107421875
BOOT_SEED = 20260826

BLUE = "#4477AA"
ORANGE = "#EE7733"
GOLD = "#CCAA44"
INK = "#2B2B2B"
GRID = "#D9D9D9"


def load_commit_geometry(commit: str) -> pd.DataFrame:
    rows = []
    for run_id in RUNS:
        rel = (
            "research/arc_20260826_5060_007/raw/geometry/"
            f"pythia-160m-seed{run_id}.json"
        )
        text = subprocess.check_output(
            ["git", "show", f"{commit}:{rel}"], cwd=REPO_ROOT, text=True
        )
        payload = json.loads(text)
        for checkpoint in payload["checkpoints"]:
            rows.extend(checkpoint["geometry_rows"])
    return pd.DataFrame(rows)


def load_current_geometry() -> pd.DataFrame:
    rows = []
    for run_id in RUNS:
        payload = json.loads((
            ARC_ROOT / "raw" / "geometry" / f"pythia-160m-seed{run_id}.json"
        ).read_text(encoding="utf-8"))
        for checkpoint in payload["checkpoints"]:
            rows.extend(checkpoint["geometry_rows"])
    return pd.DataFrame(rows)


def residual_frame(frame: pd.DataFrame, name: str) -> pd.DataFrame:
    primary = frame[frame["match_class"] == "A"]
    wide = primary.pivot(
        index=["target_id", "run_id", "step", "layer"],
        columns="family", values="top1_flip_rate",
    ).reset_index()
    wide[name] = wide["noise"] - wide["block"]
    return wide[["target_id", "run_id", "step", "layer", name]]


def summarize(frame: pd.DataFrame, column: str) -> dict:
    run_values = frame.groupby("run_id")[column].median().reindex(RUNS)
    values = run_values.to_numpy(float)
    rng = np.random.default_rng(BOOT_SEED)
    draws = rng.choice(values, size=(100_000, len(values)), replace=True).mean(axis=1)
    return {
        "estimate": float(values.mean()),
        "run_medians": {str(int(index)): float(value) for index, value in run_values.items()},
        "bootstrap_90_ci": [float(x) for x in np.quantile(draws, [.05, .95])],
        "bootstrap_95_ci": [float(x) for x in np.quantile(draws, [.025, .975])],
        "same_sign_runs": int((values < 0).sum()),
    }


def style_axis(ax):
    ax.grid(True, color=GRID, linewidth=.8, alpha=.7)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)


def add_blossom(fig):
    x, y = .975, .965
    for dx, dy in [(-.006, 0), (.006, 0), (0, -.008), (0, .008)]:
        fig.add_artist(plt.Circle((x + dx, y + dy), .004,
                                 transform=fig.transFigure, color=GOLD, alpha=.8))


def main() -> None:
    source = pd.read_csv(ARC006 / "processed" / "all_target_results.csv")
    source_a = source[source["match_class"] == "A"][
        ["target_id", "run_id", "step", "layer", "family_residual", "block_ds", "noise_ds"]
    ].copy()
    topk = load_commit_geometry(TOPK_SEAL_COMMIT)
    argmax = load_current_geometry()
    topk_pairs = residual_frame(topk, "corrected_topk_residual")
    argmax_pairs = residual_frame(argmax, "corrected_argmax_residual")
    diagnostic = source_a.merge(topk_pairs, on=["target_id", "run_id", "step", "layer"], validate="one_to_one")
    diagnostic = diagnostic.merge(argmax_pairs, on=["target_id", "run_id", "step", "layer"], validate="one_to_one")
    diagnostic["topk_correction"] = diagnostic["corrected_topk_residual"] - diagnostic["family_residual"]
    diagnostic["argmax_correction"] = diagnostic["corrected_argmax_residual"] - diagnostic["family_residual"]

    topk_all = topk.merge(
        source[["target_id", "block_ds", "noise_ds"]], on="target_id", validate="many_to_one"
    )
    argmax_all = argmax.merge(
        source[["target_id", "block_ds", "noise_ds"]], on="target_id", validate="many_to_one"
    )
    topk_all["source_ds"] = np.where(topk_all["family"] == "block", topk_all["block_ds"], topk_all["noise_ds"])
    argmax_all["source_ds"] = np.where(argmax_all["family"] == "block", argmax_all["block_ds"], argmax_all["noise_ds"])
    topk_all["difference"] = topk_all["top1_flip_rate"] - topk_all["source_ds"]
    argmax_all["difference"] = argmax_all["top1_flip_rate"] - argmax_all["source_ds"]

    summaries = {
        "arc006_mixed": summarize(diagnostic, "family_residual"),
        "consistent_topk": summarize(diagnostic, "corrected_topk_residual"),
        "consistent_argmax": summarize(diagnostic, "corrected_argmax_residual"),
    }
    for result in summaries.values():
        ci90 = result["bootstrap_90_ci"]
        result["equivalence_pass"] = bool(
            abs(result["estimate"]) <= BOUND and ci90[0] >= -BOUND and ci90[1] <= BOUND
        )
    summary = {
        "verdict": "PRIOR ASSAY INVALIDATION",
        "root_cause": "ARC-006 compared block D_S anchored by topk with noise D_S anchored by argmax under tied FP16 logits",
        "summaries": summaries,
        "topk_path_max_abs_difference_by_family": {
            family: float(group["difference"].abs().max())
            for family, group in topk_all.groupby("family")
        },
        "argmax_path_max_abs_difference_by_family": {
            family: float(group["difference"].abs().max())
            for family, group in argmax_all.groupby("family")
        },
        "consistent_topk_shrinkage_vs_frozen": float(
            1.0 - abs(summaries["consistent_topk"]["estimate"])
            / abs(summaries["arc006_mixed"]["estimate"])
        ),
        "largest_cellwise_residual_correction": float(diagnostic["topk_correction"].abs().max()),
        "conclusion": "ARC-006 exact residual and high-confidence frozen-assay claim are invalid; a corrected rerun is required before ARC-007 geometry inference",
    }

    processed = ARC_ROOT / "processed"
    results = ARC_ROOT / "results"
    figures = ARC_ROOT / "figures"
    processed.mkdir(exist_ok=True); results.mkdir(exist_ok=True); figures.mkdir(exist_ok=True)
    diagnostic.to_csv(processed / "top1_consistency_diagnostic.csv", index=False)
    (results / "prior_assay_invalidation.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )

    labels = ["ARC-006 mixed", "Consistent topk", "Consistent argmax"]
    keys = ["arc006_mixed", "consistent_topk", "consistent_argmax"]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
    ax = axes[0]
    ax.axvspan(-BOUND, BOUND, color=GOLD, alpha=.18)
    ax.axvline(0, color=INK, linewidth=1)
    for index, (label, key) in enumerate(zip(labels, keys)):
        row = summaries[key]; ci = row["bootstrap_95_ci"]; value = row["estimate"]
        ax.errorbar(value, index, xerr=[[value-ci[0]], [ci[1]-value]],
                    fmt="D" if index else "o", color=ORANGE if index else BLUE, capsize=4)
    ax.set_yticks(range(3), labels)
    ax.set_xlabel("Family residual with run-bootstrap 95% CI")
    ax.set_title("Residual under top-1 tie-breaking rules")
    style_axis(ax)

    ax = axes[1]
    by_step = diagnostic.groupby("step")[["family_residual", "corrected_topk_residual"]].median()
    x = np.arange(len(by_step))
    ax.bar(x-.18, by_step["family_residual"], width=.36, color=BLUE, label="ARC-006 mixed")
    ax.bar(x+.18, by_step["corrected_topk_residual"], width=.36,
           facecolor="none", edgecolor=ORANGE, linewidth=1.8, label="Consistent topk")
    ax.axhline(0, color=INK, linewidth=1)
    ax.set_xticks(x, [f"step {int(step):,}" for step in by_step.index])
    ax.set_ylabel("Median Class A cell residual")
    ax.set_title("Tie-breaking correction by checkpoint")
    ax.legend(frameon=False)
    style_axis(ax)
    fig.suptitle("ARC-006 top-1 anchor inconsistency")
    fig.text(.5, .92, "Same 103 Class A cells; correction changes only the intact top-1 tie rule", ha="center", color="#666666")
    add_blossom(fig); fig.tight_layout(rect=(0, 0, 1, .90))
    fig.savefig(figures / "fig_prior_assay_invalidation.png", dpi=240)
    plt.close(fig)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
