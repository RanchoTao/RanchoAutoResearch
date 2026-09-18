"""Faithful Llama-family adaptation of the ARC-002 block-bypass sweep."""

from __future__ import annotations

import argparse
import gc
import json
import math
import os
import random
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
import yaml

os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
os.environ.setdefault("HF_HUB_DOWNLOAD_TIMEOUT", "600")
from transformers import AutoModelForCausalLM, AutoTokenizer


ROOT = Path(__file__).resolve().parents[1]


def choose_sequences(tokens: torch.Tensor, seed: int, count: int, length: int) -> torch.Tensor:
    rng = random.Random(seed)
    usable = len(tokens) - length - 1
    width = usable // count
    starts = [i * width + rng.randrange(max(1, width - length)) for i in range(count)]
    return torch.stack([tokens[start : start + length + 1] for start in starts])


def layers_of(model: torch.nn.Module) -> torch.nn.ModuleList:
    return model.model.layers


@torch.inference_mode()
def evaluate_checkpoint(model_name: str, revision: str, step: int, tokenizer,
                        all_tokens: torch.Tensor, config: dict) -> dict:
    started = time.perf_counter()
    torch.cuda.reset_peak_memory_stats()
    dtype = {"float16": torch.float16, "bfloat16": torch.bfloat16}[config["dtype"]]
    model = AutoModelForCausalLM.from_pretrained(
        model_name, revision=revision, dtype=dtype,
    ).to("cuda").eval()
    original_layers = layers_of(model)
    candidates = list(range(1, len(original_layers) - 1))
    bins = np.asarray(config["confidence_bins"], dtype=float)
    seed_results = []

    for evaluation_seed in config["evaluation_seeds"]:
        sequences = choose_sequences(
            all_tokens, evaluation_seed, config["sequences_per_seed"], config["sequence_length"]
        )
        baseline = {"nll": 0.0, "entropy": 0.0, "confidence": 0.0, "margin": 0.0}
        tokens_seen = 0
        per_layer = {
            layer: {
                "agree": 0, "nll": 0.0, "kl": 0.0,
                "bin_total": np.zeros(len(bins) - 1, dtype=np.int64),
                "bin_agree": np.zeros(len(bins) - 1, dtype=np.int64),
            } for layer in candidates
        }
        for start in range(0, len(sequences), config["batch_size"]):
            batch = sequences[start : start + config["batch_size"]].to("cuda")
            inputs, labels = batch[:, :-1], batch[:, 1:]
            model.model.layers = original_layers
            logits = model(inputs, use_cache=False).logits.float()
            log_probs = logits.log_softmax(-1)
            probs = log_probs.exp()
            top_values, top_indices = probs.topk(2, dim=-1)
            top1 = top_indices[..., 0]
            confidence = top_values[..., 0]
            margin = top_values[..., 0] - top_values[..., 1]
            entropy = -(probs * log_probs).sum(-1)
            count = labels.numel()
            baseline["nll"] += F.cross_entropy(
                logits.reshape(-1, logits.shape[-1]), labels.reshape(-1), reduction="sum"
            ).item()
            baseline["entropy"] += entropy.sum().item()
            baseline["confidence"] += confidence.sum().item()
            baseline["margin"] += margin.sum().item()
            tokens_seen += count
            bin_ids = torch.bucketize(
                confidence.contiguous(),
                torch.tensor(bins[1:-1], device="cuda", dtype=confidence.dtype),
            ).cpu().numpy()

            for layer in candidates:
                model.model.layers = torch.nn.ModuleList(
                    [block for index, block in enumerate(original_layers) if index != layer]
                )
                changed = model(inputs, use_cache=False).logits.float()
                changed_log_probs = changed.log_softmax(-1)
                agree = changed.argmax(-1) == top1
                item = per_layer[layer]
                item["agree"] += agree.sum().item()
                item["nll"] += F.cross_entropy(
                    changed.reshape(-1, changed.shape[-1]), labels.reshape(-1), reduction="sum"
                ).item()
                item["kl"] += (probs * (log_probs - changed_log_probs)).sum().item()
                agree_np = agree.cpu().numpy()
                for bin_index in range(len(bins) - 1):
                    mask = bin_ids == bin_index
                    item["bin_total"][bin_index] += int(mask.sum())
                    item["bin_agree"][bin_index] += int(agree_np[mask].sum())

        baseline_nll = baseline["nll"] / tokens_seen
        layer_rows = []
        for layer in candidates:
            item = per_layer[layer]
            deleted_nll = item["nll"] / tokens_seen
            bin_rows = []
            for index in range(len(bins) - 1):
                count = int(item["bin_total"][index])
                bin_rows.append({
                    "low": float(bins[index]), "high": float(bins[index + 1]), "count": count,
                    "agreement": float(item["bin_agree"][index] / count) if count else None,
                })
            layer_rows.append({
                "layer": layer, "relative_depth": layer / (len(original_layers) - 1),
                "top1_agreement": item["agree"] / tokens_seen,
                "deleted_nll": deleted_nll, "nll_damage": deleted_nll - baseline_nll,
                "kl": item["kl"] / tokens_seen, "confidence_bins": bin_rows,
            })
        seed_results.append({
            "evaluation_seed": evaluation_seed, "tokens": tokens_seen,
            "baseline_nll": baseline_nll, "baseline_perplexity": math.exp(baseline_nll),
            "baseline_entropy": baseline["entropy"] / tokens_seen,
            "baseline_top1_confidence": baseline["confidence"] / tokens_seen,
            "baseline_top1_margin": baseline["margin"] / tokens_seen,
            "layers": layer_rows,
        })

    model.model.layers = original_layers
    result = {
        "revision": revision, "commit_hash": getattr(model.config, "_commit_hash", None),
        "dtype": config["dtype"],
        "step": step, "training_tokens": step * config["tokens_per_step"],
        "normalized_progress": step / config["final_step"],
        "n_layers": len(original_layers), "candidate_layers": candidates,
        "parameters": sum(parameter.numel() for parameter in model.parameters()),
        "seed_results": seed_results, "runtime_seconds": time.perf_counter() - started,
        "peak_cuda_bytes": torch.cuda.max_memory_allocated(),
    }
    del model
    gc.collect()
    torch.cuda.empty_cache()
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--only-steps", nargs="*", type=int)
    args = parser.parse_args()
    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    tokenizer = AutoTokenizer.from_pretrained(config["model"], revision=config["revisions"][-1])
    text = (ROOT / config["text_file"]).resolve().read_text(encoding="utf-8")
    all_tokens = tokenizer(text, add_special_tokens=False, return_tensors="pt")["input_ids"][0]
    output = ROOT / config["output_dir"] / "trajectory/raw_results.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        payload = json.loads(output.read_text(encoding="utf-8"))
    else:
        payload = {
            "model": config["model"], "architecture": "LlamaForCausalLM",
            "training_framework": "Nanotron", "config": config,
            "text_tokens": int(len(all_tokens)), "checkpoints": [],
        }
    completed = {row["step"] for row in payload["checkpoints"]}
    selected = set(args.only_steps) if args.only_steps else set(config["checkpoint_steps"])
    for revision, step in zip(config["revisions"], config["checkpoint_steps"]):
        if step not in selected or step in completed:
            continue
        row = evaluate_checkpoint(config["model"], revision, step, tokenizer, all_tokens, config)
        payload["checkpoints"].append(row)
        payload["checkpoints"].sort(key=lambda item: item["step"])
        output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(json.dumps({
            "revision": revision, "step": step,
            "mean_nll": float(np.mean([item["baseline_nll"] for item in row["seed_results"]])),
            "mean_agreement": float(np.mean([
                layer["top1_agreement"] for seed in row["seed_results"] for layer in seed["layers"]
            ])),
            "runtime_seconds": row["runtime_seconds"], "output": str(output),
        }), flush=True)


if __name__ == "__main__":
    main()
