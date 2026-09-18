"""Run an open-weight local verifier over paired evidence conditions."""

from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


LABEL_RE = re.compile(r"\b(SUPPORTED|CONTRADICTED|UNVERIFIABLE)\b", re.IGNORECASE)
LABEL_LINE_RE = re.compile(r"^\s*(?:\*\*)?(SUPPORTED|CONTRADICTED|UNVERIFIABLE)(?:\*\*)?\s*$", re.IGNORECASE)


def evidence_for(case: dict, condition: str) -> str:
    parameter = case["parameter"]
    env_key = {
        "scaler": "EXECCONFIG_SCALER",
        "C": "EXECCONFIG_C",
        "metric": "EXECCONFIG_METRIC",
        "seed": "EXECCONFIG_SEED",
    }[parameter]
    static = {
        "target_parameter": parameter,
        "claimed_value": case["claim_value"],
        "repository_default_for_target": case["defaults"][parameter],
        "warning": "A repository default is not proof of the value used by an executed run.",
    }
    if condition == "static":
        evidence = static
    elif condition == "launch":
        evidence = {
            **static,
            "precedence_low_to_high": case["precedence"],
            "json_config_value_for_target": case["config_input"].get(parameter, "ABSENT"),
            "environment_value_for_target": case["environment_input"].get(env_key, "ABSENT"),
            "explicit_cli_value_for_target": case["cli_input"].get(parameter, "ABSENT"),
        }
    elif condition == "receipt":
        evidence = {
            "runtime_receipt_schema": case["receipt"]["schema"],
            "dataset": case["receipt"]["dataset"],
            "target_parameter": parameter,
            "claimed_value": case["claim_value"],
            "resolved_value_used_by_run": case["receipt"]["resolved"][parameter],
            "winning_source_channel": case["receipt"]["winning_source"][parameter],
            "dataset_sha256": case["receipt"]["dataset_sha256"],
            "score_sha256": case["receipt"]["score_sha256"],
        }
    else:
        raise ValueError(condition)
    return json.dumps(evidence, indent=2, sort_keys=True)


def make_prompt(case: dict, condition: str) -> str:
    return f"""You audit a scientific claim about an experiment that may have runtime overrides.

Return exactly one label on the first line: SUPPORTED, CONTRADICTED, or UNVERIFIABLE.
Apply this decision table mechanically:
1. If the effective value used by the executed run is not established, output UNVERIFIABLE.
2. If the effective value is established and is exactly equal to the claimed value, output SUPPORTED.
3. If the effective value is established and differs from the claimed value, output CONTRADICTED.
Equal values are SUPPORTED, never CONTRADICTED.
Then give one short reason on the second line. Do not assume repository defaults were used.
The winning source channel (for example "cli") is the name of a source, not the parameter value.

CLAIM:
{case['claim']}

EVIDENCE CONDITION: {condition}
EVIDENCE:
{evidence_for(case, condition)}
"""


def parse_label(text: str) -> str:
    for line in text.splitlines():
        match = LABEL_LINE_RE.match(line)
        if match:
            return match.group(1).upper()
    match = LABEL_RE.search(text)
    return match.group(1).upper() if match else "PARSE_ERROR"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="Qwen/Qwen2.5-Coder-1.5B-Instruct")
    parser.add_argument("--cases", default="outputs/cases.jsonl")
    parser.add_argument("--output", default="outputs/predictions_qwen_coder_1_5b.jsonl")
    parser.add_argument("--max-cases", type=int)
    parser.add_argument("--batch-size", type=int, default=8)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    cases = [json.loads(line) for line in (root / args.cases).read_text(encoding="utf-8").splitlines() if line]
    if args.max_cases:
        cases = cases[: args.max_cases]
    jobs = [(case, condition) for case in cases for condition in ("static", "launch", "receipt")]

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required for this pilot")
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(
        args.model,
        dtype=torch.float16,
        device_map="cuda",
    )
    model.eval()
    output = root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    started = time.time()
    rows = []
    with torch.inference_mode():
        for offset in range(0, len(jobs), args.batch_size):
            batch = jobs[offset : offset + args.batch_size]
            prompts = []
            for case, condition in batch:
                messages = [{"role": "user", "content": make_prompt(case, condition)}]
                prompts.append(tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True))
            encoded = tokenizer(prompts, return_tensors="pt", padding=True, truncation=True, max_length=4096).to("cuda")
            generated = model.generate(
                **encoded,
                max_new_tokens=64,
                do_sample=False,
                pad_token_id=tokenizer.eos_token_id,
            )
            continuations = generated[:, encoded.input_ids.shape[1] :]
            texts = tokenizer.batch_decode(continuations, skip_special_tokens=True)
            for (case, condition), text in zip(batch, texts):
                rows.append(
                    {
                        "case_id": case["case_id"],
                        "dataset": case["dataset"],
                        "parameter": case["parameter"],
                        "mechanism": case["mechanism"],
                        "actual_label": case["actual_label"],
                        "condition": condition,
                        "model": args.model,
                        "prediction": parse_label(text),
                        "raw_output": text,
                    }
                )
            print(f"completed={min(offset + len(batch), len(jobs))}/{len(jobs)}", flush=True)
    with output.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    print(json.dumps({"predictions": len(rows), "seconds": time.time() - started, "output": str(output)}, indent=2))


if __name__ == "__main__":
    main()
