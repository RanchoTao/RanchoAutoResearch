"""Pretraining-checkpoint sweep for layer-deletion robustness."""

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
from transformers import AutoModelForCausalLM, AutoTokenizer


ROOT = Path(__file__).resolve().parents[1]


def choose_sequences(tokens: torch.Tensor, seed: int, count: int, length: int) -> torch.Tensor:
    rng = random.Random(seed)
    usable = len(tokens) - length - 1
    width = usable // count
    starts = [i * width + rng.randrange(max(1, width - length)) for i in range(count)]
    return torch.stack([tokens[start:start + length + 1] for start in starts])


def layers_of(model: torch.nn.Module) -> torch.nn.ModuleList:
    return model.gpt_neox.layers


@torch.inference_mode()
def evaluate_checkpoint(model_name: str, revision: str, step: int, tokenizer,
                        all_tokens: torch.Tensor, config: dict) -> dict:
    started = time.perf_counter()
    model = AutoModelForCausalLM.from_pretrained(
        model_name, revision=revision, dtype=torch.float16,
    ).to("cuda").eval()
    original_layers = layers_of(model)
    n_layers = len(original_layers)
    bins = np.asarray(config["confidence_bins"], dtype=float)
    seed_results = []
    for seed in config["seeds"]:
        sequences = choose_sequences(all_tokens, seed, config["sequences_per_seed"], config["sequence_length"])
        base_nll = 0.0
        base_entropy = 0.0
        base_confidence = 0.0
        base_margin = 0.0
        tokens_seen = 0
        per_layer = {
            layer: {
                "agree": 0, "nll": 0.0, "kl": 0.0,
                "bin_total": np.zeros(len(bins) - 1, dtype=np.int64),
                "bin_agree": np.zeros(len(bins) - 1, dtype=np.int64),
            }
            for layer in range(n_layers)
        }
        for start in range(0, len(sequences), config["batch_size"]):
            batch = sequences[start:start + config["batch_size"]].to("cuda")
            inputs, labels = batch[:, :-1], batch[:, 1:]
            model.gpt_neox.layers = original_layers
            logits = model(inputs, use_cache=False).logits.float()
            log_probs = logits.log_softmax(-1)
            probs = log_probs.exp()
            top_values, top_indices = probs.topk(2, dim=-1)
            top1 = top_indices[..., 0]
            confidence = top_values[..., 0]
            margin = top_values[..., 0] - top_values[..., 1]
            entropy = -(probs * log_probs).sum(-1)
            n = labels.numel()
            base_nll += F.cross_entropy(logits.reshape(-1, logits.shape[-1]), labels.reshape(-1), reduction="sum").item()
            base_entropy += entropy.sum().item()
            base_confidence += confidence.sum().item()
            base_margin += margin.sum().item()
            tokens_seen += n
            bin_ids = torch.bucketize(
                confidence,
                torch.tensor(bins[1:-1], device="cuda", dtype=confidence.dtype),
            ).cpu().numpy()

            for layer in range(n_layers):
                model.gpt_neox.layers = torch.nn.ModuleList([
                    block for index, block in enumerate(original_layers) if index != layer
                ])
                changed = model(inputs, use_cache=False).logits.float()
                agree = changed.argmax(-1) == top1
                item = per_layer[layer]
                item["agree"] += agree.sum().item()
                item["nll"] += F.cross_entropy(
                    changed.reshape(-1, changed.shape[-1]), labels.reshape(-1), reduction="sum"
                ).item()
                item["kl"] += (probs * (log_probs - changed.log_softmax(-1))).sum().item()
                agree_np = agree.cpu().numpy()
                for bin_index in range(len(bins) - 1):
                    mask = bin_ids == bin_index
                    item["bin_total"][bin_index] += mask.sum()
                    item["bin_agree"][bin_index] += agree_np[mask].sum()
        baseline_nll = base_nll / tokens_seen
        layer_rows = []
        for layer in range(n_layers):
            item = per_layer[layer]
            changed_nll = item["nll"] / tokens_seen
            bin_rows = []
            for index in range(len(bins) - 1):
                count = int(item["bin_total"][index])
                bin_rows.append({
                    "low": float(bins[index]), "high": float(bins[index + 1]), "count": count,
                    "agreement": float(item["bin_agree"][index] / count) if count else None,
                })
            layer_rows.append({
                "layer": layer, "relative_depth": layer / (n_layers - 1),
                "top1_agreement": item["agree"] / tokens_seen,
                "excess_nll": changed_nll - baseline_nll,
                "kl": item["kl"] / tokens_seen, "confidence_bins": bin_rows,
            })
        seed_results.append({
            "seed": seed, "tokens": tokens_seen,
            "baseline_nll": baseline_nll, "baseline_perplexity": math.exp(baseline_nll),
            "baseline_entropy": base_entropy / tokens_seen,
            "baseline_top1_confidence": base_confidence / tokens_seen,
            "baseline_top1_margin": base_margin / tokens_seen,
            "layers": layer_rows,
        })
    model.gpt_neox.layers = original_layers
    result = {
        "revision": revision, "step": step, "n_layers": n_layers,
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
    args = parser.parse_args()
    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    torch.cuda.reset_peak_memory_stats()
    tokenizer = AutoTokenizer.from_pretrained(config["model"], revision="main")
    text = (ROOT / config["text_file"]).read_text(encoding="utf-8")
    all_tokens = tokenizer(text, add_special_tokens=False, return_tensors="pt")["input_ids"][0]
    results = []
    for revision, step in zip(config["revisions"], config["checkpoint_steps"]):
        result = evaluate_checkpoint(config["model"], revision, step, tokenizer, all_tokens, config)
        results.append(result)
        means = {
            "nll": float(np.mean([row["baseline_nll"] for row in result["seed_results"]])),
            "confidence": float(np.mean([row["baseline_top1_confidence"] for row in result["seed_results"]])),
        }
        print(json.dumps({"revision": revision, "step": step, **means,
                          "runtime_seconds": result["runtime_seconds"]}), flush=True)
    output = ROOT / config["output"]
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {"config": config, "checkpoints": results, "text_tokens": int(len(all_tokens))}
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(output)}), flush=True)


if __name__ == "__main__":
    main()
