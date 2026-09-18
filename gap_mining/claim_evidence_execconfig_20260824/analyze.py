"""Analyze the paired pilot and produce tables, tests, and figures."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import binomtest
from sklearn.metrics import balanced_accuracy_score, f1_score


def bootstrap_difference(
    df: pd.DataFrame, left: str, right: str, metric: str, seed: int = 20260824
) -> tuple[float, float, float]:
    pivot = df.pivot(index="case_id", columns="condition", values=metric).dropna()
    diffs = pivot[left].to_numpy(float) - pivot[right].to_numpy(float)
    rng = np.random.default_rng(seed)
    samples = rng.choice(diffs, size=(10000, len(diffs)), replace=True).mean(axis=1)
    return float(diffs.mean()), float(np.quantile(samples, 0.025)), float(np.quantile(samples, 0.975))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--predictions", default="outputs/predictions_qwen_coder_1_5b.jsonl")
    parser.add_argument("--tag", default="pilot")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    records = [json.loads(line) for line in (root / args.predictions).read_text(encoding="utf-8").splitlines() if line]
    df = pd.DataFrame(records)
    df["is_mismatch"] = df.actual_label.eq("CONTRADICTED")
    df["unsafe_support"] = df.is_mismatch & df.prediction.eq("SUPPORTED")
    df["false_rejection"] = (~df.is_mismatch) & (~df.prediction.eq("SUPPORTED"))
    df["abstained"] = df.prediction.eq("UNVERIFIABLE")
    df["correct_actual"] = df.prediction.eq(df.actual_label)

    summaries = []
    for condition, part in df.groupby("condition"):
        binary = part[part.prediction.isin(["SUPPORTED", "CONTRADICTED"])]
        summaries.append(
            {
                "condition": condition,
                "n": len(part),
                "false_support_rate": part.loc[part.is_mismatch, "unsafe_support"].mean(),
                "false_rejection_rate": (~part.loc[~part.is_mismatch, "prediction"].eq("SUPPORTED")).mean(),
                "abstention_rate": part.abstained.mean(),
                "actual_label_accuracy": part.correct_actual.mean(),
                "balanced_accuracy_decided_only": balanced_accuracy_score(binary.actual_label, binary.prediction) if len(binary) else np.nan,
                "macro_f1_all": f1_score(part.actual_label, part.prediction, labels=["SUPPORTED", "CONTRADICTED", "UNVERIFIABLE"], average="macro", zero_division=0),
                "parse_errors": int(part.prediction.eq("PARSE_ERROR").sum()),
            }
        )
    summary = pd.DataFrame(summaries).sort_values("condition")
    summary.to_csv(root / "outputs" / f"summary_by_condition_{args.tag}.csv", index=False)

    mismatch = df[df.is_mismatch]
    diff, low, high = bootstrap_difference(mismatch, "launch", "receipt", "unsafe_support")
    pivot = mismatch.pivot(index="case_id", columns="condition", values="unsafe_support")
    b = int(((pivot.launch == 1) & (pivot.receipt == 0)).sum())
    c = int(((pivot.launch == 0) & (pivot.receipt == 1)).sum())
    mcnemar_p = float(binomtest(b, b + c, 0.5).pvalue) if b + c else 1.0
    aligned = df[~df.is_mismatch]
    fr_diff, fr_low, fr_high = bootstrap_difference(aligned, "launch", "receipt", "false_rejection")
    acc_diff, acc_low, acc_high = bootstrap_difference(df, "receipt", "launch", "correct_actual")
    acc_pivot = df.pivot(index="case_id", columns="condition", values="correct_actual")
    acc_b = int(((acc_pivot.receipt == 1) & (acc_pivot.launch == 0)).sum())
    acc_c = int(((acc_pivot.receipt == 0) & (acc_pivot.launch == 1)).sum())
    acc_p = float(binomtest(acc_b, acc_b + acc_c, 0.5).pvalue) if acc_b + acc_c else 1.0
    test = {
        "primary_difference_launch_minus_receipt": diff,
        "paired_bootstrap_95_ci": [low, high],
        "mcnemar_b_launch_wrong_receipt_correct": b,
        "mcnemar_c_launch_correct_receipt_wrong": c,
        "mcnemar_exact_p": mcnemar_p,
        "exploratory_false_rejection_launch_minus_receipt": fr_diff,
        "exploratory_false_rejection_bootstrap_95_ci": [fr_low, fr_high],
        "exploratory_accuracy_receipt_minus_launch": acc_diff,
        "exploratory_accuracy_bootstrap_95_ci": [acc_low, acc_high],
        "exploratory_accuracy_mcnemar_receipt_only_correct": acc_b,
        "exploratory_accuracy_mcnemar_launch_only_correct": acc_c,
        "exploratory_accuracy_mcnemar_exact_p": acc_p,
    }
    (root / "outputs" / f"primary_test_{args.tag}.json").write_text(json.dumps(test, indent=2), encoding="utf-8")

    strat = (
        mismatch.groupby(["condition", "mechanism", "parameter"], as_index=False)
        .agg(false_support_rate=("unsafe_support", "mean"), n=("case_id", "size"))
    )
    strat.to_csv(root / "outputs" / f"stratified_false_support_{args.tag}.csv", index=False)

    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(7, 4.5))
    order = ["static", "launch", "receipt"]
    plot_data = mismatch.groupby("condition", as_index=False).unsafe_support.mean()
    sns.barplot(data=plot_data, x="condition", y="unsafe_support", order=order, ax=ax, color="#4C78A8")
    ax.set(xlabel="Evidence condition", ylabel="False-support rate", ylim=(0, 1), title="Unsupported runs incorrectly declared supported")
    for container in ax.containers:
        ax.bar_label(container, fmt="%.2f")
    fig.tight_layout()
    fig.savefig(root / "outputs" / f"false_support_by_condition_{args.tag}.png", dpi=180)
    plt.close(fig)

    heat = mismatch.groupby(["mechanism", "condition"]).unsafe_support.mean().unstack().reindex(columns=order)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    sns.heatmap(heat, annot=True, fmt=".2f", vmin=0, vmax=1, cmap="rocket_r", ax=ax)
    ax.set(title="False-support rate by override mechanism", xlabel="Evidence condition", ylabel="Override mechanism")
    fig.tight_layout()
    fig.savefig(root / "outputs" / f"false_support_heatmap_{args.tag}.png", dpi=180)
    plt.close(fig)

    print(summary.to_string(index=False))
    print(json.dumps(test, indent=2))


if __name__ == "__main__":
    main()
