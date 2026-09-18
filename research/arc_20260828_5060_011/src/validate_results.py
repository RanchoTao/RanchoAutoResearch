#!/usr/bin/env python3
"""Independent integrity and calculation checks for ARC-011."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SUMMARY_PATH = ROOT / "results" / "cross_corpus_summary.json"
SUMMARY = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def core_delta(payload: dict) -> float:
    values = {}
    for checkpoint in payload["checkpoints"]:
        if checkpoint["step"] not in (14000, 143000):
            continue
        cell_values = []
        for evaluation in checkpoint["evaluation_results"]:
            cell_values.extend(
                float(row["top1_agreement"])
                for row in evaluation["interventions"]
                if float(row["alpha"]) == 1.0
            )
        values[checkpoint["step"]] = float(np.mean(cell_values))
    return values[143000] - values[14000]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def validate_matches(rows: list[dict[str, str]], kind: str) -> tuple[bool, list[str]]:
    failures = []
    used: dict[tuple[int, int], set[tuple[int, float]]] = {}
    for index, row in enumerate(rows):
        run_id, step = int(row["run_id"]), int(row["step"])
        key = (run_id, step)
        high = (int(row["high_layer"]), float(row["high_alpha"]))
        low = (int(row["low_layer"]), float(row["low_alpha"]))
        if high in used.setdefault(key, set()) or low in used[key]:
            failures.append(f"{kind} row {index}: cell reused within run/checkpoint")
        used[key].update([high, low])
        ratio = float(row["magnitude_ratio"])
        kl_gap = float(row["absolute_kl_gap"])
        nll_gap = float(row["absolute_nll_gap"])
        if kind == "A":
            if ratio > 1.10 + 1e-12 or kl_gap < 0.03 - 1e-12:
                failures.append(f"A row {index}: frozen caliper failure")
        else:
            mean_kl = (abs(float(row["high_kl"])) + abs(float(row["low_kl"]))) / 2
            mean_nll = (abs(float(row["high_nll_damage"])) + abs(float(row["low_nll_damage"]))) / 2
            kl_caliper = max(0.01, 0.10 * mean_kl)
            nll_caliper = max(0.015, 0.10 * mean_nll)
            separated = abs(high[0] - low[0]) >= 3 or ratio >= 1.25
            if kl_gap > kl_caliper + 1e-12 or nll_gap > nll_caliper + 1e-12 or not separated:
                failures.append(f"B row {index}: frozen caliper/separation failure")
    return not failures, failures


def main() -> None:
    raw_paths = sorted((ROOT / "raw").glob("pythia-160m-seed*.json"))
    payloads = [json.loads(path.read_text(encoding="utf-8")) for path in raw_paths]
    raw_deltas = {int(payload["training_run_id"]): core_delta(payload) for payload in payloads}
    reported = {
        int(row["run_id"]): float(row["delta_s"])
        for row in SUMMARY["core_replication"]["individual_runs"]
    }
    raw_values = [raw_deltas[key] for key in sorted(raw_deltas)]
    rng = np.random.default_rng(20260828)
    draws = rng.choice(np.asarray(raw_values), size=(100000, len(raw_values)), replace=True).mean(axis=1)
    ci = [float(x) for x in np.quantile(draws, [0.025, 0.975])]

    a_rows = read_csv(ROOT / "matching_diagnostics" / "magnitude_matched_pairs.csv")
    b_rows = read_csv(ROOT / "matching_diagnostics" / "damage_matched_pairs.csv")
    a_valid, a_failures = validate_matches(a_rows, "A")
    b_valid, b_failures = validate_matches(b_rows, "B")
    conf = read_csv(ROOT / "processed" / "core_confidence_comparisons.csv")

    figure_checks = {}
    for path in sorted((ROOT / "figures").glob("*.png")):
        with Image.open(path) as image:
            extrema = image.convert("L").getextrema()
            figure_checks[path.name] = {
                "width": image.width,
                "height": image.height,
                "nonblank": extrema[0] < extrema[1],
            }

    checks = {
        "six_raw_runs": len(payloads) == 6,
        "three_checkpoints_each": all(len(payload["checkpoints"]) == 3 for payload in payloads),
        "all_harnesses_pass": all(cp["harness_validation"]["pass"] for payload in payloads for cp in payload["checkpoints"]),
        "canonical_top1_everywhere": all(payload["top1_rule"] == "lowest_token_index_among_exact_logit_maxima" for payload in payloads),
        "raw_hashes_match_summary": all(SUMMARY["raw_sha256"][path.name] == sha256(path) for path in raw_paths),
        "per_run_delta_recomputed": all(abs(raw_deltas[key] - reported[key]) < 1e-12 for key in raw_deltas),
        "mean_delta_recomputed": abs(float(np.mean(raw_values)) - SUMMARY["core_replication"]["mean_delta_s"]) < 1e-12,
        "median_delta_recomputed": abs(float(np.median(raw_values)) - SUMMARY["core_replication"]["median_delta_s"]) < 1e-12,
        "bootstrap_ci_recomputed": np.allclose(ci, SUMMARY["core_replication"]["run_bootstrap_95_ci_mean"], atol=1e-12),
        "all_six_negative": sum(value < 0 for value in raw_values) == 6,
        "magnitude_matches_obey_frozen_calipers": a_valid,
        "damage_matches_obey_frozen_calipers": b_valid,
        "matching_pair_counts": len(a_rows) == 161 and len(b_rows) == 194,
        "confidence_rows_and_signs": len(conf) == 30 and all(float(row["delta_s"]) < 0 for row in conf),
        "exactly_four_nonblank_figures": len(figure_checks) == 4 and all(row["nonblank"] for row in figure_checks.values()),
        "verdict_matches_preregistered_logic": SUMMARY["verdict"] == "CORPUS-GO",
    }
    result = {
        "arc": "ARC-20260828-5060-011",
        "checks": checks,
        "recomputed": {
            "per_run_delta_s": raw_deltas,
            "mean_delta_s": float(np.mean(raw_values)),
            "median_delta_s": float(np.median(raw_values)),
            "bootstrap_95_ci": ci,
        },
        "match_failures": {"A": a_failures, "B": b_failures},
        "figure_checks": figure_checks,
        "passed": all(checks.values()),
    }
    (ROOT / "results" / "independent_validation.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    lines = [
        "# Independent validation",
        "",
        f"Overall: **{'PASS' if result['passed'] else 'FAIL'}**",
        "",
        "| Check | Result |",
        "|---|---|",
    ]
    lines.extend(f"| `{name}` | {'PASS' if value else 'FAIL'} |" for name, value in checks.items())
    (ROOT / "independent_validation.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
