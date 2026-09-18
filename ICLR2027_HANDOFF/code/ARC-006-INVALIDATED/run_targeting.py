"""Outcome-blinded inverse KL/NLL targeting for ARC-006.

This executable intentionally contains no top-1 outcome computation. A
separate, sealed executable handles the later reveal.
"""

from __future__ import annotations

import argparse
import csv
import gc
import json
import math
import os
import random
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import yaml

os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
from transformers import AutoModelForCausalLM, AutoTokenizer


ARC_ROOT = Path(__file__).resolve().parents[1]
GOLDEN_RATIO = (math.sqrt(5.0) - 1.0) / 2.0


def choose_sequences(tokens: torch.Tensor, seed: int, count: int, length: int) -> torch.Tensor:
    rng = random.Random(seed)
    usable = len(tokens) - length - 1
    width = usable // count
    if usable <= 0 or width <= length:
        raise ValueError("evaluation text cannot supply frozen sequences")
    starts = [i * width + rng.randrange(width - length) for i in range(count)]
    return torch.stack([tokens[start : start + length + 1] for start in starts])


def deterministic_noise_seed(
    direction_id: int, evaluation_seed: int, layer: int, batch_start: int
) -> int:
    return int(direction_id * 1_000_003 + evaluation_seed * 10_007 + layer * 101 + batch_start)


class NormControlledActivationNoise(nn.Module):
    def __init__(self, block: nn.Module, beta: float, direction_seed: int):
        super().__init__()
        self.block = block
        self.beta = float(beta)
        self.direction_seed = int(direction_seed)
        self.relative_sum = 0.0
        self.absolute_rms_sum = 0.0
        self.token_count = 0

    def forward(self, hidden_states: torch.Tensor, *args, **kwargs):
        outputs = self.block(hidden_states, *args, **kwargs)
        intact_output = outputs[0]
        if self.beta == 0.0:
            changed = intact_output
            difference = torch.zeros_like(intact_output, dtype=torch.float32)
        else:
            generator = torch.Generator(device=intact_output.device)
            generator.manual_seed(self.direction_seed)
            direction = torch.randn(
                intact_output.shape, generator=generator,
                device=intact_output.device, dtype=torch.float32,
            )
            direction /= torch.linalg.vector_norm(direction, dim=-1, keepdim=True) + 1e-12
            output_f = intact_output.float()
            intended = self.beta * torch.linalg.vector_norm(
                output_f, dim=-1, keepdim=True
            ) * direction
            changed = (output_f + intended).to(intact_output.dtype)
            difference = changed.float() - output_f
        with torch.no_grad():
            diff_norm = torch.linalg.vector_norm(difference, dim=-1)
            out_norm = torch.linalg.vector_norm(intact_output.float(), dim=-1)
            self.relative_sum += (diff_norm / (out_norm + 1e-12)).sum().item()
            self.absolute_rms_sum += (
                diff_norm / math.sqrt(intact_output.shape[-1])
            ).sum().item()
            self.token_count += diff_norm.numel()
        return (changed,) + outputs[1:]

    def summary(self) -> dict:
        return {
            "activation_relative_magnitude": self.relative_sum / self.token_count,
            "activation_absolute_rms": self.absolute_rms_sum / self.token_count,
            "activation_stat_tokens": self.token_count,
        }


def replace_one(layers: nn.ModuleList, index: int, replacement: nn.Module) -> nn.ModuleList:
    return nn.ModuleList([replacement if i == index else block for i, block in enumerate(layers)])


@torch.inference_mode()
def validate_harness(model: nn.Module, sample_inputs: torch.Tensor, atol: float) -> dict:
    original = model.gpt_neox.layers
    layer = 1
    seed = deterministic_noise_seed(101, 11, layer, 0)
    model.gpt_neox.layers = original
    intact = model(sample_inputs, use_cache=False).logits.float()
    zero = NormControlledActivationNoise(original[layer], 0.0, seed)
    model.gpt_neox.layers = replace_one(original, layer, zero)
    zero_logits = model(sample_inputs, use_cache=False).logits.float()
    first = NormControlledActivationNoise(original[layer], 0.2, seed)
    model.gpt_neox.layers = replace_one(original, layer, first)
    first_logits = model(sample_inputs, use_cache=False).logits.float()
    repeat = NormControlledActivationNoise(original[layer], 0.2, seed)
    model.gpt_neox.layers = replace_one(original, layer, repeat)
    repeat_logits = model(sample_inputs, use_cache=False).logits.float()
    different = NormControlledActivationNoise(
        original[layer], 0.2, deterministic_noise_seed(202, 11, layer, 0)
    )
    model.gpt_neox.layers = replace_one(original, layer, different)
    different_logits = model(sample_inputs, use_cache=False).logits.float()
    model.gpt_neox.layers = original
    zero_stats = zero.summary()
    result = {
        "tested_layer": layer,
        "zero_max_abs_logit_diff": float((zero_logits - intact).abs().max().item()),
        "zero_measured_relative_magnitude": float(
            zero_stats["activation_relative_magnitude"]
        ),
        "repeat_max_abs_logit_diff": float(
            (first_logits - repeat_logits).abs().max().item()
        ),
        "different_direction_max_abs_logit_diff": float(
            (first_logits - different_logits).abs().max().item()
        ),
        "atol": float(atol),
    }
    result["pass"] = bool(
        result["zero_max_abs_logit_diff"] <= atol
        and result["zero_measured_relative_magnitude"] == 0.0
        and result["repeat_max_abs_logit_diff"] <= atol
        and result["different_direction_max_abs_logit_diff"] > atol
    )
    return result


def objective(metrics: dict, target_kl: float, target_nll: float) -> float:
    kl_scale = max(0.01, 0.10 * abs(target_kl))
    nll_scale = max(0.015, 0.10 * abs(target_nll))
    return float(
        ((metrics["kl"] - target_kl) / kl_scale) ** 2
        + ((metrics["nll_damage"] - target_nll) / nll_scale) ** 2
    )


def classify(metrics: dict, target_kl: float, target_nll: float) -> tuple[str, dict]:
    kl_error = abs(metrics["kl"] - target_kl)
    nll_error = abs(metrics["nll_damage"] - target_nll)
    a_kl = max(0.005, 0.05 * abs(target_kl))
    a_nll = max(0.0075, 0.05 * abs(target_nll))
    b_kl = max(0.01, 0.10 * abs(target_kl))
    b_nll = max(0.015, 0.10 * abs(target_nll))
    if kl_error <= a_kl and nll_error <= a_nll:
        match_class = "A"
    elif kl_error <= b_kl and nll_error <= b_nll:
        match_class = "B"
    else:
        match_class = "C"
    return match_class, {
        "absolute_kl_error": kl_error,
        "relative_kl_error": kl_error / (abs(target_kl) + 1e-12),
        "absolute_nll_error": nll_error,
        "relative_nll_error": nll_error / (abs(target_nll) + 1e-12),
        "class_a_kl_tolerance": a_kl,
        "class_a_nll_tolerance": a_nll,
        "class_b_kl_tolerance": b_kl,
        "class_b_nll_tolerance": b_nll,
    }


@torch.inference_mode()
def evaluate_beta(
    model: nn.Module,
    original: nn.ModuleList,
    layer: int,
    beta: float,
    all_tokens: torch.Tensor,
    config: dict,
) -> dict:
    changed_nll_sum = 0.0
    baseline_nll_sum = 0.0
    kl_sum = 0.0
    relative_sum = 0.0
    absolute_sum = 0.0
    activation_tokens = 0
    tokens_seen = 0
    directions = [int(value) for value in config["noise_direction_ids"]]
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
            token_count = labels.numel()
            baseline_nll_sum += F.cross_entropy(
                logits.reshape(-1, logits.shape[-1]), labels.reshape(-1), reduction="sum"
            ).item()
            tokens_seen += token_count
            for direction_id in directions:
                seed = deterministic_noise_seed(
                    direction_id, int(evaluation_seed), layer, batch_start
                )
                wrapper = NormControlledActivationNoise(original[layer], beta, seed)
                model.gpt_neox.layers = replace_one(original, layer, wrapper)
                changed = model(inputs, use_cache=False).logits.float()
                changed_log_probs = changed.log_softmax(-1)
                changed_nll_sum += F.cross_entropy(
                    changed.reshape(-1, changed.shape[-1]),
                    labels.reshape(-1), reduction="sum",
                ).item()
                kl_sum += (probs * (log_probs - changed_log_probs)).sum().item()
                activation = wrapper.summary()
                count = int(activation["activation_stat_tokens"])
                relative_sum += activation["activation_relative_magnitude"] * count
                absolute_sum += activation["activation_absolute_rms"] * count
                activation_tokens += count
                del wrapper, changed, changed_log_probs
            del batch, inputs, labels, logits, log_probs, probs
    model.gpt_neox.layers = original
    direction_count = len(directions)
    baseline_nll = baseline_nll_sum / tokens_seen
    intervened_nll = changed_nll_sum / (tokens_seen * direction_count)
    return {
        "beta": float(beta),
        "baseline_nll": float(baseline_nll),
        "intervened_nll": float(intervened_nll),
        "nll_damage": float(intervened_nll - baseline_nll),
        "kl": float(kl_sum / (tokens_seen * direction_count)),
        "activation_relative_magnitude": float(relative_sum / activation_tokens),
        "activation_absolute_rms": float(absolute_sum / activation_tokens),
        "tokens_per_direction": int(tokens_seen),
        "direction_count": int(direction_count),
    }


def solve_target(
    model: nn.Module, original: nn.ModuleList, target: dict,
    all_tokens: torch.Tensor, config: dict,
) -> dict:
    target_kl = float(target["target_kl"])
    target_nll = float(target["target_nll_damage"])
    cache: dict[float, dict] = {}

    def evaluate(beta: float) -> dict:
        key = round(float(beta), 12)
        if key not in cache:
            row = evaluate_beta(
                model, original, int(target["layer"]), key, all_tokens, config
            )
            row["objective"] = objective(row, target_kl, target_nll)
            cache[key] = row
        return cache[key]

    grid = [float(value) for value in config["fixed_beta_grid"]]
    for beta in grid:
        evaluate(beta)
    best_grid_index = min(
        range(len(grid)), key=lambda index: (evaluate(grid[index])["objective"], grid[index])
    )
    lower = grid[max(0, best_grid_index - 1)]
    upper = grid[min(len(grid) - 1, best_grid_index + 1)]
    if lower == upper:
        lower, upper = grid[0], grid[-1]
    c = upper - GOLDEN_RATIO * (upper - lower)
    d = lower + GOLDEN_RATIO * (upper - lower)
    for _ in range(int(config["golden_refinements"])):
        if upper - lower <= float(config["minimum_bracket_width"]):
            break
        c_row, d_row = evaluate(c), evaluate(d)
        if (c_row["objective"], c) <= (d_row["objective"], d):
            upper, d = d, c
            c = upper - GOLDEN_RATIO * (upper - lower)
        else:
            lower, c = c, d
            d = lower + GOLDEN_RATIO * (upper - lower)
    best = min(cache.values(), key=lambda row: (row["objective"], row["beta"]))
    # Independent final forward evaluation at the already fixed beta.
    verification = evaluate_beta(
        model, original, int(target["layer"]), float(best["beta"]), all_tokens, config
    )
    verification["objective"] = objective(verification, target_kl, target_nll)
    match_class, errors = classify(verification, target_kl, target_nll)
    return {
        **target,
        "selected_beta": float(best["beta"]),
        "selected_from_trial_index": int(
            sorted(cache).index(round(float(best["beta"]), 12))
        ),
        "match_class": match_class,
        **errors,
        "achieved_kl": verification["kl"],
        "achieved_nll_damage": verification["nll_damage"],
        "achieved_intervened_nll": verification["intervened_nll"],
        "activation_relative_magnitude": verification["activation_relative_magnitude"],
        "activation_absolute_rms": verification["activation_absolute_rms"],
        "objective": verification["objective"],
        "verification_kl_difference": verification["kl"] - best["kl"],
        "verification_nll_difference": verification["nll_damage"] - best["nll_damage"],
        "boundary_selected": bool(
            abs(best["beta"] - grid[0]) < 1e-12
            or abs(best["beta"] - grid[-1]) < 1e-12
        ),
        "trial_count": len(cache),
        "trials": [cache[key] for key in sorted(cache)],
    }


def evaluate_checkpoint(
    model_name: str, revision: str, step: int, tokenizer,
    all_tokens: torch.Tensor, targets: list[dict], config: dict,
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
        raise RuntimeError(f"targeting harness failed: {harness}")
    results = []
    for target in sorted(targets, key=lambda row: int(row["layer"])):
        layer = int(target["layer"])
        if layer < 1 or layer >= len(original) - 1:
            raise ValueError(f"invalid target layer {layer}")
        results.append(solve_target(model, original, target, all_tokens, config))
    result = {
        "revision": revision,
        "commit_hash": getattr(model.config, "_commit_hash", None),
        "step": int(step),
        "parameters": int(sum(parameter.numel() for parameter in model.parameters())),
        "harness_validation": harness,
        "targets": results,
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
        raise ValueError(f"run {run_id} is outside the frozen {config['stage']} set")
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required")
    target_path = (ARC_ROOT / config["target_file"]).resolve()
    with target_path.open(newline="", encoding="utf-8") as handle:
        targets = list(csv.DictReader(handle))
    expected_columns = {
        "target_id", "run_id", "step", "progress", "layer",
        "target_kl", "target_nll_damage",
    }
    if not targets or set(targets[0]) != expected_columns:
        raise RuntimeError(f"unexpected blinded target schema: {list(targets[0]) if targets else []}")
    numeric_fields = ["run_id", "step", "layer"]
    float_fields = ["progress", "target_kl", "target_nll_damage"]
    for row in targets:
        for field in numeric_fields:
            row[field] = int(row[field])
        for field in float_fields:
            row[field] = float(row[field])
    targets = [row for row in targets if row["run_id"] == run_id]
    target_ids = [row["target_id"] for row in targets]
    if not targets or len(target_ids) != len(set(target_ids)):
        raise RuntimeError(f"invalid target set for run {run_id}")
    model_name = f"EleutherAI/pythia-{config['model_scale']}m-seed{run_id}"
    tokenizer = AutoTokenizer.from_pretrained(model_name, revision="main", local_files_only=True)
    text_path = (ARC_ROOT / config["text_file"]).resolve()
    all_tokens = tokenizer(
        text_path.read_text(encoding="utf-8"), add_special_tokens=False,
        return_tensors="pt",
    )["input_ids"][0]
    output = (ARC_ROOT / config["output_dir"] / f"pythia-160m-seed{run_id}.json").resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        payload = json.loads(output.read_text(encoding="utf-8"))
        if payload["stage"] != config["stage"]:
            raise RuntimeError("existing target file has a different stage")
    else:
        payload = {
            "arc": "ARC-20260826-5060-006",
            "stage": config["stage"],
            "blinded_metrics": ["kl", "nll_damage"],
            "model": model_name,
            "run_id": run_id,
            "config": config,
            "target_file": str(target_path),
            "text_path": str(text_path),
            "checkpoints": [],
        }
    finished = {int(row["step"]) for row in payload["checkpoints"]}
    for revision, step in zip(config["revisions"], config["checkpoint_steps"]):
        step = int(step)
        if step in finished:
            continue
        step_targets = [row for row in targets if row["step"] == step]
        row = evaluate_checkpoint(
            model_name, revision, step, tokenizer, all_tokens, step_targets, config
        )
        payload["checkpoints"].append(row)
        payload["checkpoints"].sort(key=lambda item: item["step"])
        output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        counts = {name: 0 for name in ["A", "B", "C"]}
        for target in row["targets"]:
            counts[target["match_class"]] += 1
        print(json.dumps({
            "stage": config["stage"], "run_id": run_id, "step": step,
            "target_count": len(row["targets"]), "match_classes": counts,
            "runtime_seconds": row["runtime_seconds"],
            "peak_cuda_bytes": row["peak_cuda_bytes"],
            "harness_pass": row["harness_validation"]["pass"],
        }), flush=True)


if __name__ == "__main__":
    main()
