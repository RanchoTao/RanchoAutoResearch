"""Run only preregistered missing SmolLM2 WSD-window checkpoints."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path

import yaml
from transformers import AutoTokenizer

os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
os.environ.setdefault("HF_HUB_DOWNLOAD_TIMEOUT", "600")

ROOT = Path(__file__).resolve().parents[1]
PREVIOUS = ROOT.parent / "ARC-20260825-5060-003"


def load_previous_runner():
    path = PREVIOUS / "src/run_cross_family.py"
    spec = importlib.util.spec_from_file_location("arc003_runner", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    args = parser.parse_args()
    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    previous_payload = json.loads(
        (PREVIOUS / "experiments/trajectory/raw_results.json").read_text(encoding="utf-8")
    )
    expected_old_steps = {320000, 800000, 1280000, 1920000, 2560000}
    old_rows = {
        row["step"]: row for row in previous_payload["checkpoints"]
        if row["step"] in expected_old_steps
    }
    if set(old_rows) != expected_old_steps:
        raise ValueError("ARC-003 does not contain every required frozen checkpoint")
    if any(row["dtype"] != "bfloat16" for row in old_rows.values()):
        raise ValueError("Only native BF16 ARC-003 records may be reused")

    runner = load_previous_runner()
    tokenizer = AutoTokenizer.from_pretrained(config["model"], revision="step-2560000")
    text = (ROOT / config["text_file"]).resolve().read_text(encoding="utf-8")
    all_tokens = tokenizer(text, add_special_tokens=False, return_tensors="pt")["input_ids"][0]
    output = ROOT / "experiments/trajectory/raw_results.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        payload = json.loads(output.read_text(encoding="utf-8"))
    else:
        payload = {
            "model": config["model"],
            "architecture": "LlamaForCausalLM",
            "training_framework": "Nanotron",
            "config": config,
            "text_tokens": int(len(all_tokens)),
            "reused_source": str(PREVIOUS / "experiments/trajectory/raw_results.json"),
            "reused_steps": sorted(expected_old_steps),
            "checkpoints": list(old_rows.values()),
        }
        payload["checkpoints"].sort(key=lambda row: row["step"])
        output.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    completed = {row["step"] for row in payload["checkpoints"]}
    for revision, step in zip(config["new_revisions"], config["new_checkpoint_steps"]):
        if step in completed:
            continue
        row = runner.evaluate_checkpoint(
            config["model"], revision, step, tokenizer, all_tokens, config
        )
        payload["checkpoints"].append(row)
        payload["checkpoints"].sort(key=lambda item: item["step"])
        output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(json.dumps({
            "revision": revision,
            "commit_hash": row["commit_hash"],
            "step": step,
            "runtime_seconds": row["runtime_seconds"],
            "output": str(output),
        }), flush=True)


if __name__ == "__main__":
    main()

