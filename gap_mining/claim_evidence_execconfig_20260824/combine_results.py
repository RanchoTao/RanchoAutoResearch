"""Combine both open-model runs into final tables and figures."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


ROOT = Path(__file__).resolve().parent
FILES = {
    "Qwen2.5-Coder-1.5B": "predictions_qwen_coder_1_5b_reparsed.jsonl",
    "Qwen2.5-3B": "predictions_qwen_3b.jsonl",
}


def load() -> pd.DataFrame:
    frames = []
    for model, filename in FILES.items():
        rows = [json.loads(line) for line in (ROOT / "outputs" / filename).read_text(encoding="utf-8").splitlines() if line]
        frame = pd.DataFrame(rows)
        frame["model_short"] = model
        frames.append(frame)
    df = pd.concat(frames, ignore_index=True)
    df["is_mismatch"] = df.actual_label.eq("CONTRADICTED")
    df["correct"] = df.prediction.eq(df.actual_label)
    df["unsafe_support"] = df.is_mismatch & df.prediction.eq("SUPPORTED")
    df["false_rejection"] = (~df.is_mismatch) & (~df.prediction.eq("SUPPORTED"))
    df["abstained"] = df.prediction.eq("UNVERIFIABLE")
    return df


def main() -> None:
    df = load()
    rows = []
    for (model, condition), part in df.groupby(["model_short", "condition"]):
        rows.append(
            {
                "model": model,
                "condition": condition,
                "n": len(part),
                "accuracy": part.correct.mean(),
                "false_support_rate": part.loc[part.is_mismatch, "unsafe_support"].mean(),
                "false_rejection_rate": part.loc[~part.is_mismatch, "false_rejection"].mean(),
                "abstention_rate": part.abstained.mean(),
            }
        )
    summary = pd.DataFrame(rows)
    summary.to_csv(ROOT / "outputs" / "combined_summary.csv", index=False)

    gains = []
    for model, part in df.groupby("model_short"):
        pivot = part.pivot(index="case_id", columns="condition", values="correct")
        for axis in ("mechanism", "parameter", "dataset"):
            metadata = part.drop_duplicates("case_id").set_index("case_id")[axis]
            local = pivot.join(metadata)
            for level, group in local.groupby(axis):
                gains.append(
                    {
                        "model": model,
                        "axis": axis,
                        "level": level,
                        "n": len(group),
                        "accuracy_gain_receipt_minus_launch": (group.receipt.astype(int) - group.launch.astype(int)).mean(),
                    }
                )
    gain_df = pd.DataFrame(gains)
    gain_df.to_csv(ROOT / "outputs" / "accuracy_gain_stratified.csv", index=False)

    sns.set_theme(style="whitegrid")
    order = ["static", "launch", "receipt"]
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.2), sharex=True)
    metrics = [
        ("accuracy", "Actual-label accuracy"),
        ("false_support_rate", "False-support rate"),
        ("false_rejection_rate", "False-rejection rate"),
    ]
    for ax, (metric, title) in zip(axes, metrics):
        sns.barplot(data=summary, x="condition", y=metric, hue="model", order=order, ax=ax)
        ax.set(title=title, xlabel="Evidence condition", ylabel="Rate", ylim=(0, 1))
        if ax is not axes[0]:
            ax.get_legend().remove()
    axes[0].legend(title="Open model", loc="upper left", fontsize=8)
    fig.suptitle("Resolved execution receipts change verifier behavior", y=1.02)
    fig.tight_layout()
    fig.savefig(ROOT / "outputs" / "combined_verifier_metrics.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    mechanism = gain_df[gain_df.axis == "mechanism"]
    fig, ax = plt.subplots(figsize=(8, 4.6))
    sns.barplot(data=mechanism, x="level", y="accuracy_gain_receipt_minus_launch", hue="model", ax=ax)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set(title="Receipt accuracy gain by override mechanism", xlabel="Override mechanism", ylabel="Receipt − launch accuracy")
    fig.tight_layout()
    fig.savefig(ROOT / "outputs" / "receipt_gain_by_mechanism.png", dpi=200)
    plt.close(fig)

    print(summary.to_string(index=False))
    print("\nAccuracy gain by mechanism:\n" + mechanism.to_string(index=False))


if __name__ == "__main__":
    main()

