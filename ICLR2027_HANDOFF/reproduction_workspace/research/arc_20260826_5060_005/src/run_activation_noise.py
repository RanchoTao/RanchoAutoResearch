"""ARC-005 norm-controlled additive activation-noise evaluator.

The runner is checkpoint-resumable. It never prints agreement/effect outcomes;
calibration support and formal analysis are handled by separate frozen scripts.
"""

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
import torch.nn as nn
import torch.nn.functional as F
import yaml

os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
from transformers import AutoModelForCausalLM, AutoTokenizer


ARC_ROOT = Path(__file__).resolve().parents[1]


def choose_sequences(tokens: torch.Tensor, seed: int, count: int, length: int) -> torch.Tensor:
    rng = random.Random(seed)
    usable = len(tokens) - length - 1
    if usable <= 0:
        raise ValueError("evaluation text is too short")
    width = usable // count
    starts = [i * width + rng.randrange(max(1, width - length)) for i in range(count)]
    return torch.stack([tokens[start : start + length + 1] for start in starts])


def deterministic_noise_seed(
    direction_id: int, evaluation_seed: int, layer: int, batch_start: int
) -> int:
    # Excludes model run, checkpoint, and beta so matched conditions reuse the
    # same hidden-space direction while the activation scale remains local.
    return int(direction_id * 1_000_003 + evaluation_seed * 10_007 + layer * 101 + batch_start)


class NormControlledActivationNoise(nn.Module):
    """Run the original block, then add token-wise normalized Gaussian noise."""

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
            actual_difference = torch.zeros_like(intact_output, dtype=torch.float32)
        else:
            generator = torch.Generator(device=intact_output.device)
            generator.manual_seed(self.direction_seed)
            direction = torch.randn(
                intact_output.shape,
                generator=generator,
                device=intact_output.device,
                dtype=torch.float32,
            )
            direction_norm = torch.linalg.vector_norm(direction, dim=-1, keepdim=True)
            output_f = intact_output.float()
            output_norm = torch.linalg.vector_norm(output_f, dim=-1, keepdim=True)
            intended = self.beta * output_norm * direction / (direction_norm + 1e-12)
            changed = (output_f + intended).to(intact_output.dtype)
            actual_difference = changed.float() - output_f

        with torch.no_grad():
            diff_norm = torch.linalg.vector_norm(actual_difference, dim=-1)
            out_norm = torch.linalg.vector_norm(intact_output.float(), dim=-1)
            hidden_size = intact_output.shape[-1]
            self.relative_sum += (diff_norm / (out_norm + 1e-12)).sum().item()
            self.absolute_rms_sum += (diff_norm / math.sqrt(hidden_size)).sum().item()
            self.token_count += diff_norm.numel()
        return (changed,) + outputs[1:]

    def summary(self) -> dict[str, float | int]:
        if not self.token_count:
            raise RuntimeError("noise wrapper recorded no tokens")
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

    different = NormControlledActivationNoise(
        original[layer], 0.2, deterministic_noise_seed(202, 11, layer, 0)
    )
    model.gpt_neox.layers = replace_one(original, layer, different)
    different_logits = model(sample_inputs, use_cache=False).logits.float()

    repeat = NormControlledActivationNoise(original[layer], 0.2, seed)
    model.gpt_neox.layers = replace_one(original, layer, repeat)
    repeat_logits = model(sample_inputs, use_cache=False).logits.float()
    model.gpt_neox.layers = original

    zero_stats = zero.summary()
    result = {
        "tested_layer": layer,
        "zero_max_abs_logit_diff": (zero_logits - intact).abs().max().item(),
        "zero_top1_equal": bool(torch.equal(zero_logits.argmax(-1), intact.argmax(-1))),
        "zero_measured_relative_magnitude": zero_stats["activation_relative_magnitude"],
        "repeat_max_abs_logit_diff": (first_logits - repeat_logits).abs().max().item(),
        "repeat_top1_equal": bool(
            torch.equal(first_logits.argmax(-1), repeat_logits.argmax(-1))
        ),
        "different_direction_max_abs_logit_diff": (
            first_logits - different_logits
        ).abs().max().item(),
        "atol": atol,
    }
    result["pass"] = bool(
        result["zero_max_abs_logit_diff"] <= atol
        and result["zero_top1_equal"]
        and result["zero_measured_relative_magnitude"] == 0.0
        and result["repeat_max_abs_logit_diff"] <= atol
        and result["repeat_top1_equal"]
        and result["different_direction_max_abs_logit_diff"] > atol
    )
    return result


@torch.inference_mode()
def evaluate_checkpoint(
    model_name: str,
    revision: str,
    step: int,
    tokenizer,
    all_tokens: torch.Tensor,
    config: dict,
) -> dict:
    started = time.perf_counter()
    torch.cuda.reset_peak_memory_stats()
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        revision=revision,
        dtype=torch.float16,
        local_files_only=True,
    ).to("cuda").eval()
    original = model.gpt_neox.layers
    layers = [int(layer) for layer in config["layers"]]
    if not layers or min(layers) < 1 or max(layers) >= len(original) - 1:
        raise ValueError(f"invalid interior layers {layers} for {len(original)} blocks")
    betas = [float(value) for value in config["beta_grid"]]
    direction_ids = [int(value) for value in config["noise_direction_ids"]]
    bins = np.asarray(config["confidence_bins"], dtype=float)

    validation_sequences = choose_sequences(
        all_tokens, config["evaluation_seeds"][0], 1, min(32, config["sequence_length"])
    )
    harness = validate_harness(
        model,
        validation_sequences[:, :-1].to("cuda"),
        float(config["zero_logit_atol"]),
    )
    if not harness["pass"]:
        raise RuntimeError(f"activation-noise harness validation failed: {harness}")

    evaluation_results = []
    for evaluation_seed in config["evaluation_seeds"]:
        sequences = choose_sequences(
            all_tokens,
            evaluation_seed,
            config["sequences_per_seed"],
            config["sequence_length"],
        )
        baseline = {"nll": 0.0, "entropy": 0.0, "confidence": 0.0, "margin": 0.0}
        tokens_seen = 0
        keys = [
            (layer, beta, direction_id)
            for layer in layers for beta in betas for direction_id in direction_ids
        ]
        fixed_rng = random.Random(20260826 + evaluation_seed)
        fixed_rng.shuffle(keys)
        accumulators = {
            key: {
                "agree": 0,
                "nll": 0.0,
                "kl": 0.0,
                "m_rel_sum": 0.0,
                "m_abs_sum": 0.0,
                "m_tokens": 0,
                "bin_total": np.zeros(len(bins) - 1, dtype=np.int64),
                "bin_agree": np.zeros(len(bins) - 1, dtype=np.int64),
            }
            for key in keys
        }

        for batch_start in range(0, len(sequences), config["batch_size"]):
            batch = sequences[batch_start : batch_start + config["batch_size"]].to("cuda")
            inputs, labels = batch[:, :-1], batch[:, 1:]
            model.gpt_neox.layers = original
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

            for layer, beta, direction_id in keys:
                seed = deterministic_noise_seed(
                    direction_id, evaluation_seed, layer, batch_start
                )
                wrapper = NormControlledActivationNoise(original[layer], beta, seed)
                model.gpt_neox.layers = replace_one(original, layer, wrapper)
                changed = model(inputs, use_cache=False).logits.float()
                changed_log_probs = changed.log_softmax(-1)
                agree = changed.argmax(-1) == top1
                item = accumulators[(layer, beta, direction_id)]
                item["agree"] += agree.sum().item()
                item["nll"] += F.cross_entropy(
                    changed.reshape(-1, changed.shape[-1]),
                    labels.reshape(-1),
                    reduction="sum",
                ).item()
                item["kl"] += (probs * (log_probs - changed_log_probs)).sum().item()
                activation = wrapper.summary()
                stat_tokens = int(activation["activation_stat_tokens"])
                item["m_rel_sum"] += activation["activation_relative_magnitude"] * stat_tokens
                item["m_abs_sum"] += activation["activation_absolute_rms"] * stat_tokens
                item["m_tokens"] += stat_tokens
                agree_np = agree.cpu().numpy()
                for bin_index in range(len(bins) - 1):
                    mask = bin_ids == bin_index
                    item["bin_total"][bin_index] += int(mask.sum())
                    item["bin_agree"][bin_index] += int(agree_np[mask].sum())
                del changed, changed_log_probs, agree, wrapper

            del logits, log_probs, probs, top_values, top_indices, top1, confidence, margin, entropy

        baseline_nll = baseline["nll"] / tokens_seen
        rows = []
        for layer in layers:
            for beta in betas:
                for direction_id in direction_ids:
                    item = accumulators[(layer, beta, direction_id)]
                    changed_nll = item["nll"] / tokens_seen
                    bin_rows = []
                    for index in range(len(bins) - 1):
                        bin_count = int(item["bin_total"][index])
                        bin_rows.append({
                            "low": float(bins[index]),
                            "high": float(bins[index + 1]),
                            "count": bin_count,
                            "agreement": (
                                float(item["bin_agree"][index] / bin_count)
                                if bin_count else None
                            ),
                        })
                    rows.append({
                        "layer": layer,
                        "relative_depth": layer / (len(original) - 1),
                        "beta": beta,
                        "noise_direction_id": direction_id,
                        "top1_agreement": item["agree"] / tokens_seen,
                        "top1_damage": 1.0 - item["agree"] / tokens_seen,
                        "intervened_nll": changed_nll,
                        "nll_damage": changed_nll - baseline_nll,
                        "kl": item["kl"] / tokens_seen,
                        "activation_relative_magnitude": item["m_rel_sum"] / item["m_tokens"],
                        "activation_absolute_rms": item["m_abs_sum"] / item["m_tokens"],
                        "confidence_bins": bin_rows,
                    })
        evaluation_results.append({
            "evaluation_seed": evaluation_seed,
            "tokens": tokens_seen,
            "baseline_nll": baseline_nll,
            "baseline_perplexity": math.exp(baseline_nll),
            "baseline_entropy": baseline["entropy"] / tokens_seen,
            "baseline_top1_confidence": baseline["confidence"] / tokens_seen,
            "baseline_top1_margin": baseline["margin"] / tokens_seen,
            "interventions": rows,
        })

    model.gpt_neox.layers = original
    result = {
        "revision": revision,
        "commit_hash": getattr(model.config, "_commit_hash", None),
        "step": step,
        "normalized_progress": step / config["final_step"],
        "n_layers": len(original),
        "candidate_layers": layers,
        "parameters": sum(parameter.numel() for parameter in model.parameters()),
        "harness_validation": harness,
        "evaluation_results": evaluation_results,
        "runtime_seconds": time.perf_counter() - started,
        "peak_cuda_bytes": torch.cuda.max_memory_allocated(),
    }
    del model
    gc.collect()
    torch.cuda.empty_cache()
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--run-id", required=True, type=int)
    parser.add_argument("--only-steps", nargs="*", type=int)
    args = parser.parse_args()
    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    if args.run_id not in config["run_ids"]:
        raise ValueError(f"run {args.run_id} is not frozen for {config['stage']}")
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required by the frozen ARC-005 harness")

    model_name = f"EleutherAI/pythia-{config['model_scale']}m-seed{args.run_id}"
    tokenizer = AutoTokenizer.from_pretrained(
        model_name, revision="main", local_files_only=True
    )
    text_path = (ARC_ROOT / config["text_file"]).resolve()
    all_tokens = tokenizer(
        text_path.read_text(encoding="utf-8"),
        add_special_tokens=False,
        return_tensors="pt",
    )["input_ids"][0]
    output = ARC_ROOT / config["output_dir"] / f"pythia-160m-seed{args.run_id}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        payload = json.loads(output.read_text(encoding="utf-8"))
        if payload["stage"] != config["stage"]:
            raise RuntimeError("existing raw stage does not match config")
    else:
        payload = {
            "arc": "ARC-20260826-5060-005",
            "stage": config["stage"],
            "intervention_family": "norm_controlled_additive_activation_noise",
            "model": model_name,
            "scale_m": config["model_scale"],
            "training_run_id": args.run_id,
            "training_seed_kind": "combined initialization and data-order seed",
            "config": config,
            "text_path": str(text_path),
            "text_tokens": int(len(all_tokens)),
            "checkpoints": [],
        }
    finished = {row["step"] for row in payload["checkpoints"]}
    selected = set(args.only_steps) if args.only_steps else set(config["checkpoint_steps"])
    for revision, step in zip(config["revisions"], config["checkpoint_steps"]):
        if step not in selected or step in finished:
            continue
        row = evaluate_checkpoint(model_name, revision, step, tokenizer, all_tokens, config)
        payload["checkpoints"].append(row)
        payload["checkpoints"].sort(key=lambda item: item["step"])
        output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(json.dumps({
            "stage": config["stage"],
            "run_id": args.run_id,
            "step": step,
            "runtime_seconds": row["runtime_seconds"],
            "peak_cuda_bytes": row["peak_cuda_bytes"],
            "harness_pass": row["harness_validation"]["pass"],
            "output": str(output),
        }), flush=True)


if __name__ == "__main__":
    main()

