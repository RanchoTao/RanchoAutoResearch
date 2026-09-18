"""Low-cost replication of Lad et al.'s layer deletion result.

The paper's TransformerLens hooks zero both attention and MLP residual updates.
For Hugging Face GPT-NeoX, omitting one residual block is functionally equivalent.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import time
import urllib.request
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
import yaml

# The Windows environment's hf-xet middleware intermittently fails on the public
# CDN. Standard HTTP uses the same immutable model files and is easier to resume.
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")

from transformers import AutoModelForCausalLM, AutoTokenizer


ROOT = Path(__file__).resolve().parents[1]


def load_config(path: Path) -> dict:
    config = yaml.safe_load(path.read_text(encoding="utf-8"))
    config["config_path"] = str(path.resolve())
    return config


def acquire_text(url: str) -> str:
    data_dir = ROOT / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    target = data_dir / "wikitext2_train.txt"
    if not target.exists():
        urllib.request.urlretrieve(url, target)
    return target.read_text(encoding="utf-8")


def get_layers(model: torch.nn.Module) -> torch.nn.ModuleList:
    if hasattr(model, "gpt_neox") and hasattr(model.gpt_neox, "layers"):
        return model.gpt_neox.layers
    raise TypeError(f"unsupported architecture: {type(model).__name__}")


def choose_sequences(tokens: torch.Tensor, seed: int, count: int, length: int) -> torch.Tensor:
    rng = random.Random(seed)
    usable = len(tokens) - length - 1
    if usable <= 0:
        raise ValueError("text is shorter than one requested sequence")
    # Stratified bins prevent accidental overlap and turn each seed into an
    # independently jittered text shard.
    bin_width = usable // count
    starts = [i * bin_width + rng.randrange(max(1, bin_width - length)) for i in range(count)]
    return torch.stack([tokens[start:start + length + 1] for start in starts])


@torch.inference_mode()
def evaluate(config: dict) -> dict:
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required by the preregistered harness")
    start = time.perf_counter()
    torch.manual_seed(0)
    torch.cuda.reset_peak_memory_stats()
    tokenizer = AutoTokenizer.from_pretrained(config["model"], revision=config["revision"])
    model = AutoModelForCausalLM.from_pretrained(
        config["model"], revision=config["revision"], dtype=torch.float16,
    ).to("cuda").eval()
    original_layers = get_layers(model)
    n_layers = len(original_layers)
    if n_layers < 8:
        raise AssertionError(f"expected at least 8 layers, got {n_layers}")

    text = acquire_text(config["text_url"])
    all_tokens = tokenizer(text, add_special_tokens=False, return_tensors="pt")["input_ids"][0]
    seed_results = []
    total_scored = 0
    for seed in config["seeds"]:
        sequences = choose_sequences(
            all_tokens, seed, config["sequences_per_seed"], config["sequence_length"]
        )
        accumulator = {
            layer: {"agree": 0.0, "nll": 0.0, "kl": 0.0, "tokens": 0}
            for layer in range(n_layers)
        }
        baseline_nll_sum = 0.0
        baseline_tokens = 0
        for batch_start in range(0, len(sequences), config["batch_size"]):
            batch = sequences[batch_start:batch_start + config["batch_size"]].to("cuda")
            inputs, labels = batch[:, :-1], batch[:, 1:]
            model.gpt_neox.layers = original_layers
            baseline_logits = model(inputs, use_cache=False).logits.float()
            baseline_nll_sum += F.cross_entropy(
                baseline_logits.reshape(-1, baseline_logits.shape[-1]), labels.reshape(-1),
                reduction="sum",
            ).item()
            baseline_tokens += labels.numel()
            baseline_log_probs = baseline_logits.log_softmax(dim=-1)
            baseline_probs = baseline_log_probs.exp()
            baseline_top1 = baseline_logits.argmax(dim=-1)

            for layer in range(n_layers):
                kept = [block for index, block in enumerate(original_layers) if index != layer]
                model.gpt_neox.layers = torch.nn.ModuleList(kept)
                intervened_logits = model(inputs, use_cache=False).logits.float()
                item = accumulator[layer]
                item["agree"] += (intervened_logits.argmax(dim=-1) == baseline_top1).sum().item()
                item["nll"] += F.cross_entropy(
                    intervened_logits.reshape(-1, intervened_logits.shape[-1]), labels.reshape(-1),
                    reduction="sum",
                ).item()
                log_q = intervened_logits.log_softmax(dim=-1)
                item["kl"] += (baseline_probs * (baseline_log_probs - log_q)).sum().item()
                item["tokens"] += labels.numel()
            del baseline_logits, baseline_log_probs, baseline_probs, baseline_top1
        model.gpt_neox.layers = original_layers
        baseline_nll = baseline_nll_sum / baseline_tokens
        total_scored += baseline_tokens
        layer_results = []
        for layer in range(n_layers):
            item = accumulator[layer]
            intervened_nll = item["nll"] / item["tokens"]
            layer_results.append({
                "layer": layer,
                "relative_depth": layer / (n_layers - 1),
                "top1_agreement": item["agree"] / item["tokens"],
                "intervened_nll": intervened_nll,
                "excess_nll": intervened_nll - baseline_nll,
                "kl_baseline_to_intervened": item["kl"] / item["tokens"],
            })
        seed_results.append({
            "seed": seed,
            "baseline_nll": baseline_nll,
            "baseline_perplexity": math.exp(baseline_nll),
            "scored_tokens": baseline_tokens,
            "layers": layer_results,
        })
        print(json.dumps(seed_results[-1]), flush=True)

    model.gpt_neox.layers = original_layers
    result = {
        "config": config,
        "model_type": type(model).__name__,
        "parameters": sum(parameter.numel() for parameter in model.parameters()),
        "n_layers": n_layers,
        "text_tokens": int(len(all_tokens)),
        "total_scored_tokens": total_scored,
        "seed_results": seed_results,
        "runtime_seconds": time.perf_counter() - start,
        "peak_cuda_bytes": torch.cuda.max_memory_allocated(),
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    config = load_config(args.config)
    result = evaluate(config)
    output = ROOT / config["output"]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({
        "output": str(output), "runtime_seconds": result["runtime_seconds"],
        "peak_cuda_bytes": result["peak_cuda_bytes"],
    }), flush=True)


if __name__ == "__main__":
    main()
