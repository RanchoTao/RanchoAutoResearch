"""Generate paired claim/config cases by executing the experiment runner."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from runner import DEFAULTS, ENV_KEYS


DATASETS = ["iris", "wine", "breast_cancer", "digits"]
PARAMETERS = {
    "scaler": ("standard", "none"),
    "C": (0.1, 10.0),
    "metric": ("balanced_accuracy", "accuracy"),
    "seed": (17, 43),
}
MECHANISMS = ["cli", "environment", "config", "precedence"]


def render_value(value: object) -> str:
    return json.dumps(value)


def claim_text(dataset: str, parameter: str, value: object) -> str:
    descriptions = {
        "scaler": "preprocessing scaler",
        "C": "logistic-regression regularization parameter C",
        "metric": "reported evaluation metric",
        "seed": "train/test split random seed",
    }
    return (
        f"The reported {dataset} experiment used {descriptions[parameter]} "
        f"equal to {render_value(value)}."
    )


def build_inputs(parameter: str, claim: object, opposite: object, mechanism: str, aligned: bool) -> tuple[dict, dict, dict]:
    config: dict[str, object] = {}
    env: dict[str, str] = {}
    cli: dict[str, object] = {}
    target = claim if aligned else opposite
    if mechanism == "cli":
        cli[parameter] = target
    elif mechanism == "environment":
        env[ENV_KEYS[parameter]] = str(target)
    elif mechanism == "config":
        config[parameter] = target
    else:
        if aligned:
            config[parameter] = opposite
            env[ENV_KEYS[parameter]] = str(opposite)
            cli[parameter] = claim
        else:
            config[parameter] = claim
            env[ENV_KEYS[parameter]] = str(claim)
            cli[parameter] = opposite
    return config, env, cli


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="outputs/cases.jsonl")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    output = root / args.output
    receipts = root / "outputs" / "receipts"
    configs = root / "outputs" / "configs"
    receipts.mkdir(parents=True, exist_ok=True)
    configs.mkdir(parents=True, exist_ok=True)
    records = []

    for dataset in DATASETS:
        for parameter, (claim, opposite) in PARAMETERS.items():
            for mechanism in MECHANISMS:
                for aligned in (True, False):
                    status = "aligned" if aligned else "mismatched"
                    case_id = f"{dataset}__{parameter}__{mechanism}__{status}"
                    config, env_inputs, cli = build_inputs(parameter, claim, opposite, mechanism, aligned)
                    config_path = configs / f"{case_id}.json"
                    config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")
                    receipt_path = receipts / f"{case_id}.json"
                    command = [
                        sys.executable,
                        str(root / "runner.py"),
                        "--dataset",
                        dataset,
                        "--config",
                        str(config_path),
                        "--receipt",
                        str(receipt_path),
                    ]
                    flag = {"scaler": "--scaler", "C": "--C", "metric": "--metric", "seed": "--seed"}
                    for key, value in cli.items():
                        command.extend([flag[key], str(value)])
                    run_env = os.environ.copy()
                    for env_key in ENV_KEYS.values():
                        run_env.pop(env_key, None)
                    run_env.update(env_inputs)
                    completed = subprocess.run(command, env=run_env, check=True, capture_output=True, text=True)
                    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
                    resolved = receipt["resolved"][parameter]
                    actual_label = "SUPPORTED" if resolved == claim else "CONTRADICTED"
                    assert (actual_label == "SUPPORTED") == aligned, (case_id, receipt)
                    records.append(
                        {
                            "case_id": case_id,
                            "dataset": dataset,
                            "parameter": parameter,
                            "mechanism": mechanism,
                            "actual_label": actual_label,
                            "epistemic_static_label": "UNVERIFIABLE",
                            "claim_value": claim,
                            "opposite_value": opposite,
                            "claim": claim_text(dataset, parameter, claim),
                            "defaults": DEFAULTS,
                            "config_input": config,
                            "environment_input": env_inputs,
                            "cli_input": cli,
                            "command": subprocess.list2cmdline(command),
                            "precedence": "defaults < JSON config < environment < explicit CLI",
                            "receipt": receipt,
                            "stderr": completed.stderr,
                        }
                    )

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
    print(json.dumps({"cases": len(records), "output": str(output)}, indent=2))


if __name__ == "__main__":
    main()

