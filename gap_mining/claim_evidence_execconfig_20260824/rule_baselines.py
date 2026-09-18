"""Deterministic controls showing what is and is not identifiable from the artifacts."""

from __future__ import annotations

import json
from pathlib import Path


ENV_KEYS = {
    "scaler": "EXECCONFIG_SCALER",
    "C": "EXECCONFIG_C",
    "metric": "EXECCONFIG_METRIC",
    "seed": "EXECCONFIG_SEED",
}


def coerce(parameter: str, value: object) -> object:
    if parameter == "C":
        return float(value)
    if parameter == "seed":
        return int(value)
    return str(value)


def verdict(value: object, claim: object) -> str:
    return "SUPPORTED" if value == claim else "CONTRADICTED"


def main() -> None:
    root = Path(__file__).resolve().parent
    cases = [json.loads(line) for line in (root / "outputs" / "cases.jsonl").read_text(encoding="utf-8").splitlines()]
    rows = []
    for case in cases:
        parameter = case["parameter"]
        claim = case["claim_value"]
        default_guess = case["defaults"][parameter]
        cli_guess = case["cli_input"].get(parameter, default_guess)
        resolved_guess = default_guess
        if parameter in case["config_input"]:
            resolved_guess = coerce(parameter, case["config_input"][parameter])
        env_key = ENV_KEYS[parameter]
        if env_key in case["environment_input"]:
            resolved_guess = coerce(parameter, case["environment_input"][env_key])
        if parameter in case["cli_input"]:
            resolved_guess = coerce(parameter, case["cli_input"][parameter])
        receipt_guess = case["receipt"]["resolved"][parameter]
        predictions = {
            "repository_default": verdict(default_guess, claim),
            "cli_only": verdict(cli_guess, claim),
            "precedence_resolver": verdict(resolved_guess, claim),
            "receipt_typed_diff": verdict(receipt_guess, claim),
        }
        for baseline, prediction in predictions.items():
            rows.append({**{key: case[key] for key in ("case_id", "dataset", "parameter", "mechanism", "actual_label")}, "baseline": baseline, "prediction": prediction})
    output = root / "outputs" / "rule_baselines.jsonl"
    output.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")

    for baseline in sorted({row["baseline"] for row in rows}):
        part = [row for row in rows if row["baseline"] == baseline]
        mismatches = [row for row in part if row["actual_label"] == "CONTRADICTED"]
        aligned = [row for row in part if row["actual_label"] == "SUPPORTED"]
        fsr = sum(row["prediction"] == "SUPPORTED" for row in mismatches) / len(mismatches)
        frr = sum(row["prediction"] != "SUPPORTED" for row in aligned) / len(aligned)
        accuracy = sum(row["prediction"] == row["actual_label"] for row in part) / len(part)
        print(f"{baseline}\tfalse_support={fsr:.3f}\tfalse_rejection={frr:.3f}\taccuracy={accuracy:.3f}")


if __name__ == "__main__":
    main()

