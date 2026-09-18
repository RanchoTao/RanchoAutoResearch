"""Evaluate unchanged ARC-003 HellaSwag competence on new WSD checkpoints."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PREVIOUS = ROOT.parent / "ARC-20260825-5060-003"


def load_previous_evaluator():
    path = PREVIOUS / "src/evaluate_hellaswag.py"
    spec = importlib.util.spec_from_file_location("arc003_hellaswag", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    module.ROOT = PREVIOUS
    return module


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--revision", required=True)
    args = parser.parse_args()
    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    if args.revision not in config["new_revisions"]:
        raise ValueError("Only preregistered new revisions may be evaluated")
    evaluator = load_previous_evaluator()
    result = evaluator.evaluate(config, args.revision)
    output = ROOT / "experiments/competence" / f"hellaswag-{args.revision}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({
        "revision": args.revision,
        "commit_hash": result["commit_hash"],
        "raw_accuracy": result["raw_accuracy"],
        "normalized_accuracy": result["normalized_accuracy"],
        "normalized_ci": result["normalized_bootstrap_95_ci"],
        "runtime_seconds": result["runtime_seconds"],
        "output": str(output),
    }), flush=True)


if __name__ == "__main__":
    main()

