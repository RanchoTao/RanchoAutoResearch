"""Sealed ARC-006 top-1 reveal evaluator.

Do not execute before the target manifest and this source are committed.
"""

from __future__ import annotations

import argparse
import csv
import gc
import json
import os
import random
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
import yaml

os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
from transformers import AutoModelForCausalLM, AutoTokenizer

from run_targeting import (
    NormControlledActivationNoise,
    choose_sequences,
    deterministic_noise_seed,
    replace_one,
    validate_harness,
)


ARC_ROOT = Path(__file__).resolve().parents[1]


@torch.inference_mode()
def evaluate_checkpoint(
    model_name: str, revision: str, step: int, all_tokens: torch.Tensor,
    targets: list[dict], config: dict,
) -> dict:
    started = time.perf_counter()
    torch.cuda.reset_peak_memory_stats()
    model = AutoModelForCausalLM.from_pretrained(
        model_name, revision=revision, dtype=torch.float16, local_files_only=True
    ).to("cuda").eval()
    original = model.gpt_neox.layers
    validation = choose_sequences(
        all_tokens, int(config["evaluation_seeds"][0]), 1,
        min(32, int(config["sequence_length"])),
    )
    harness = validate_harness(
        model, validation[:, :-1].to("cuda"), float(config["zero_logit_atol"])
    )
    if not harness["pass"]:
        raise RuntimeError(f"reveal harness failed: {harness}")
    bins = np.asarray(config["confidence_bins"], dtype=float)
    directions = [int(value) for value in config["noise_direction_ids"]]
    accumulators = {}
    for target in targets:
        accumulators[target["target_id"]] = {
            "agree": 0, "changed_nll": 0.0, "baseline_nll": 0.0,
            "kl": 0.0, "tokens": 0,
            "bin_total": np.zeros(len(bins) - 1, dtype=np.int64),
            "bin_agree": np.zeros(len(bins) - 1, dtype=np.int64),
        }
    for evaluation_seed in config["evaluation_seeds"]:
        sequences = choose_sequences(
            all_tokens, int(evaluation_seed), int(config["sequences_per_seed"]),
            int(config["sequence_length"]),
        )
        for batch_start in range(0, len(sequences), int(config["batch_size"])):
            batch = sequences[batch_start : batch_start + int(config["batch_size"])].to("cuda")
            inputs, labels = batch[:, :-1], batch[:, 1:]
            model.gpt_neox.layers = original
            logits = model(inputs, use_cache=False).logits.float()
            log_probs = logits.log_softmax(-1)
            probs = log_probs.exp()
            intact_top1 = logits.argmax(-1)
            confidence = probs.max(-1).values
            bin_ids = torch.bucketize(
                confidence.contiguous(),
                torch.tensor(bins[1:-1], device="cuda", dtype=confidence.dtype),
            ).cpu().numpy()
            baseline_nll = F.cross_entropy(
                logits.reshape(-1, logits.shape[-1]), labels.reshape(-1), reduction="sum"
            ).item()
            token_count = labels.numel()
            for target in targets:
                item = accumulators[target["target_id"]]
                layer = int(target["layer"])
                beta = float(target["selected_beta"])
                item["baseline_nll"] += baseline_nll * len(directions)
                item["tokens"] += token_count * len(directions)
                for direction_id in directions:
                    seed = deterministic_noise_seed(
                        direction_id, int(evaluation_seed), layer, batch_start
                    )
                    wrapper = NormControlledActivationNoise(original[layer], beta, seed)
                    model.gpt_neox.layers = replace_one(original, layer, wrapper)
                    changed = model(inputs, use_cache=False).logits.float()
                    changed_log_probs = changed.log_softmax(-1)
                    agree = changed.argmax(-1) == intact_top1
                    item["agree"] += int(agree.sum().item())
                    item["changed_nll"] += F.cross_entropy(
                        changed.reshape(-1, changed.shape[-1]), labels.reshape(-1),
                        reduction="sum",
                    ).item()
                    item["kl"] += float(
                        (probs * (log_probs - changed_log_probs)).sum().item()
                    )
                    agree_np = agree.cpu().numpy()
                    for index in range(len(bins) - 1):
                        mask = bin_ids == index
                        item["bin_total"][index] += int(mask.sum())
                        item["bin_agree"][index] += int(agree_np[mask].sum())
                    del wrapper, changed, changed_log_probs, agree
            del batch, inputs, labels, logits, log_probs, probs, intact_top1, confidence
    model.gpt_neox.layers = original
    rows = []
    for target in sorted(targets, key=lambda row: int(row["layer"])):
        item = accumulators[target["target_id"]]
        agreement = item["agree"] / item["tokens"]
        baseline_nll = item["baseline_nll"] / item["tokens"]
        changed_nll = item["changed_nll"] / item["tokens"]
        confidence_bins = []
        for index in range(len(bins) - 1):
            count = int(item["bin_total"][index])
            confidence_bins.append({
                "low": float(bins[index]), "high": float(bins[index + 1]),
                "count": count,
                "agreement": float(item["bin_agree"][index] / count) if count else None,
            })
        rows.append({
            "target_id": target["target_id"], "run_id": int(target["run_id"]),
            "step": int(target["step"]), "layer": int(target["layer"]),
            "selected_beta": float(target["selected_beta"]),
            "match_class": target["match_class"],
            "top1_agreement": float(agreement),
            "top1_damage": float(1.0 - agreement),
            "baseline_nll": float(baseline_nll),
            "intervened_nll": float(changed_nll),
            "nll_damage": float(changed_nll - baseline_nll),
            "kl": float(item["kl"] / item["tokens"]),
            "tokens_across_directions": int(item["tokens"]),
            "confidence_bins": confidence_bins,
        })
    result = {
        "revision": revision,
        "commit_hash": getattr(model.config, "_commit_hash", None),
        "step": int(step), "harness_validation": harness,
        "target_results": rows,
        "runtime_seconds": float(time.perf_counter() - started),
        "peak_cuda_bytes": int(torch.cuda.max_memory_allocated()),
    }
    del model
    gc.collect()
    torch.cuda.empty_cache()
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--run-id", required=True, type=int)
    args = parser.parse_args()
    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    run_id = int(args.run_id)
    if run_id not in config["run_ids"]:
        raise ValueError("run is outside the sealed reveal set")
    manifest_path = (ARC_ROOT / config["target_manifest"]).resolve()
    with manifest_path.open(newline="", encoding="utf-8") as handle:
        manifest = list(csv.DictReader(handle))
    numeric = ["run_id", "step", "layer"]
    floats = ["selected_beta"]
    for row in manifest:
        for field in numeric:
            row[field] = int(row[field])
        for field in floats:
            row[field] = float(row[field])
    manifest = [row for row in manifest if row["run_id"] == run_id]
    if len(manifest) != 30:
        raise RuntimeError(f"sealed manifest has {len(manifest)} rows for run {run_id}")
    model_name = f"EleutherAI/pythia-{config['model_scale']}m-seed{run_id}"
    tokenizer = AutoTokenizer.from_pretrained(model_name, revision="main", local_files_only=True)
    text_path = (ARC_ROOT / config["text_file"]).resolve()
    all_tokens = tokenizer(
        text_path.read_text(encoding="utf-8"), add_special_tokens=False,
        return_tensors="pt",
    )["input_ids"][0]
    output = (ARC_ROOT / config["output_dir"] / f"pythia-160m-seed{run_id}.json").resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "arc": "ARC-20260826-5060-006", "stage": "reveal",
        "model": model_name, "run_id": run_id,
        "target_manifest": str(manifest_path), "config": config,
        "checkpoints": [],
    }
    for revision, step in zip(config["revisions"], config["checkpoint_steps"]):
        step = int(step)
        targets = [row for row in manifest if row["step"] == step]
        result = evaluate_checkpoint(
            model_name, revision, step, all_tokens, targets, config
        )
        payload["checkpoints"].append(result)
        output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(json.dumps({
            "stage": "reveal", "run_id": run_id, "step": step,
            "target_count": len(result["target_results"]),
            "runtime_seconds": result["runtime_seconds"],
            "peak_cuda_bytes": result["peak_cuda_bytes"],
            "harness_pass": result["harness_validation"]["pass"],
        }), flush=True)


if __name__ == "__main__":
    main()
