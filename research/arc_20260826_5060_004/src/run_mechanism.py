"""Frozen ARC-004 continuous block-bypass mechanism assay.

The alpha=1 endpoint is required to reproduce the original module-list deletion.
Raw JSON is checkpoint-resumable and written after every completed checkpoint.
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


def middle_layers(n_layers: int) -> list[int]:
    if n_layers < 3:
        raise ValueError(f"need at least three layers, found {n_layers}")
    return list(range(1, n_layers - 1))


class ResidualAttenuator(nn.Module):
    """Attenuate one block's complete residual update while retaining its API."""

    def __init__(self, block: nn.Module, alpha: float):
        super().__init__()
        self.block = block
        self.alpha = float(alpha)
        self.reset_stats()

    def reset_stats(self) -> None:
        self.relative_sum = 0.0
        self.absolute_rms_sum = 0.0
        self.update_rms_sum = 0.0
        self.token_count = 0

    def forward(self, hidden_states: torch.Tensor, *args, **kwargs):
        outputs = self.block(hidden_states, *args, **kwargs)
        intact_output = outputs[0]
        update = intact_output - hidden_states
        difference = self.alpha * update
        # Preserve exact frozen endpoints. Reconstructing x as b(x)-(b(x)-x)
        # in FP16 is algebraically correct but not bitwise equivalent to the
        # original module-list bypass, which directly forwards x.
        if self.alpha == 0.0:
            changed = intact_output
        elif self.alpha == 1.0:
            changed = hidden_states
        else:
            changed = intact_output - difference
        with torch.no_grad():
            diff_f = difference.float()
            out_f = intact_output.float()
            update_f = update.float()
            diff_norm = torch.linalg.vector_norm(diff_f, dim=-1)
            out_norm = torch.linalg.vector_norm(out_f, dim=-1)
            hidden_size = diff_f.shape[-1]
            self.relative_sum += (diff_norm / (out_norm + 1e-12)).sum().item()
            self.absolute_rms_sum += (diff_norm / math.sqrt(hidden_size)).sum().item()
            self.update_rms_sum += (
                torch.linalg.vector_norm(update_f, dim=-1) / math.sqrt(hidden_size)
            ).sum().item()
            self.token_count += diff_norm.numel()
        return (changed,) + outputs[1:]

    def summary(self) -> dict[str, float | int]:
        if self.token_count == 0:
            raise RuntimeError("attenuator recorded no activation statistics")
        return {
            "activation_relative_magnitude": self.relative_sum / self.token_count,
            "activation_absolute_rms": self.absolute_rms_sum / self.token_count,
            "intact_update_rms": self.update_rms_sum / self.token_count,
            "activation_stat_tokens": self.token_count,
        }


def replace_one(layers: nn.ModuleList, index: int, replacement: nn.Module) -> nn.ModuleList:
    return nn.ModuleList([replacement if i == index else block for i, block in enumerate(layers)])


def parameter_norm(module: nn.Module) -> float:
    square_sum = 0.0
    for parameter in module.parameters():
        square_sum += parameter.detach().float().square().sum().item()
    return math.sqrt(square_sum)


@torch.inference_mode()
def validate_wrapper(model: nn.Module, sample_inputs: torch.Tensor, atol: float) -> dict:
    original = model.gpt_neox.layers
    layer = middle_layers(len(original))[0]

    model.gpt_neox.layers = original
    intact = model(sample_inputs, use_cache=False).logits.float()

    zero = ResidualAttenuator(original[layer], 0.0)
    model.gpt_neox.layers = replace_one(original, layer, zero)
    zero_logits = model(sample_inputs, use_cache=False).logits.float()

    full = ResidualAttenuator(original[layer], 1.0)
    model.gpt_neox.layers = replace_one(original, layer, full)
    full_logits = model(sample_inputs, use_cache=False).logits.float()

    model.gpt_neox.layers = nn.ModuleList(
        [block for index, block in enumerate(original) if index != layer]
    )
    deleted = model(sample_inputs, use_cache=False).logits.float()

    # Fixed order-reversal/state-leakage check.
    first = ResidualAttenuator(original[layer], 0.5)
    model.gpt_neox.layers = replace_one(original, layer, first)
    first_logits = model(sample_inputs, use_cache=False).logits.float()
    other_layer = middle_layers(len(original))[-1]
    other = ResidualAttenuator(original[other_layer], 0.75)
    model.gpt_neox.layers = replace_one(original, other_layer, other)
    _ = model(sample_inputs, use_cache=False).logits
    repeat = ResidualAttenuator(original[layer], 0.5)
    model.gpt_neox.layers = replace_one(original, layer, repeat)
    repeat_logits = model(sample_inputs, use_cache=False).logits.float()
    model.gpt_neox.layers = original

    result = {
        "tested_layer": layer,
        "alpha0_max_abs_logit_diff": (zero_logits - intact).abs().max().item(),
        "alpha0_top1_equal": bool(torch.equal(zero_logits.argmax(-1), intact.argmax(-1))),
        "alpha1_deletion_max_abs_logit_diff": (full_logits - deleted).abs().max().item(),
        "alpha1_deletion_top1_equal": bool(
            torch.equal(full_logits.argmax(-1), deleted.argmax(-1))
        ),
        "order_repeat_max_abs_logit_diff": (first_logits - repeat_logits).abs().max().item(),
        "order_repeat_top1_equal": bool(
            torch.equal(first_logits.argmax(-1), repeat_logits.argmax(-1))
        ),
        "atol": atol,
    }
    result["pass"] = bool(
        result["alpha0_max_abs_logit_diff"] <= atol
        and result["alpha0_top1_equal"]
        and result["alpha1_deletion_max_abs_logit_diff"] <= atol
        and result["alpha1_deletion_top1_equal"]
        and result["order_repeat_max_abs_logit_diff"] <= atol
        and result["order_repeat_top1_equal"]
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
    candidates = middle_layers(len(original))
    bins = np.asarray(config["confidence_bins"], dtype=float)
    strengths = [float(value) for value in config["intervention_strengths"]]
    layer_norms = {layer: parameter_norm(original[layer]) for layer in candidates}
    model_norm = parameter_norm(model)

    validation_sequences = choose_sequences(
        all_tokens, config["evaluation_seeds"][0], 1, min(32, config["sequence_length"])
    )
    harness = validate_wrapper(
        model,
        validation_sequences[:, :-1].to("cuda"),
        float(config["equivalence_logit_atol"]),
    )
    if not harness["pass"]:
        raise RuntimeError(f"new intervention harness failed equivalence: {harness}")

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
        keys = [(layer, alpha) for layer in candidates for alpha in strengths]
        fixed_rng = random.Random(20260826 + evaluation_seed + step)
        fixed_rng.shuffle(keys)
        accumulators = {
            key: {
                "agree": 0,
                "nll": 0.0,
                "kl": 0.0,
                "m_rel_sum": 0.0,
                "m_abs_sum": 0.0,
                "update_rms_sum": 0.0,
                "m_tokens": 0,
                "bin_total": np.zeros(len(bins) - 1, dtype=np.int64),
                "bin_agree": np.zeros(len(bins) - 1, dtype=np.int64),
            }
            for key in keys
        }

        for start in range(0, len(sequences), config["batch_size"]):
            batch = sequences[start : start + config["batch_size"]].to("cuda")
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
                confidence,
                torch.tensor(bins[1:-1], device="cuda", dtype=confidence.dtype),
            ).cpu().numpy()

            for layer, alpha in keys:
                wrapper = ResidualAttenuator(original[layer], alpha)
                model.gpt_neox.layers = replace_one(original, layer, wrapper)
                changed = model(inputs, use_cache=False).logits.float()
                changed_log_probs = changed.log_softmax(-1)
                agree = changed.argmax(-1) == top1
                item = accumulators[(layer, alpha)]
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
                item["update_rms_sum"] += activation["intact_update_rms"] * stat_tokens
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
        for layer in candidates:
            for alpha in strengths:
                item = accumulators[(layer, alpha)]
                changed_nll = item["nll"] / tokens_seen
                bin_rows = []
                for index in range(len(bins) - 1):
                    bin_count = int(item["bin_total"][index])
                    bin_rows.append({
                        "low": float(bins[index]),
                        "high": float(bins[index + 1]),
                        "count": bin_count,
                        "agreement": (
                            float(item["bin_agree"][index] / bin_count) if bin_count else None
                        ),
                    })
                rows.append({
                    "layer": layer,
                    "relative_depth": layer / (len(original) - 1),
                    "alpha": alpha,
                    "top1_agreement": item["agree"] / tokens_seen,
                    "top1_damage": 1.0 - item["agree"] / tokens_seen,
                    "intervened_nll": changed_nll,
                    "nll_damage": changed_nll - baseline_nll,
                    "kl": item["kl"] / tokens_seen,
                    "activation_relative_magnitude": item["m_rel_sum"] / item["m_tokens"],
                    "activation_absolute_rms": item["m_abs_sum"] / item["m_tokens"],
                    "intact_update_rms": item["update_rms_sum"] / item["m_tokens"],
                    "layer_parameter_l2": layer_norms[layer],
                    "alpha_layer_parameter_l2_proxy": alpha * layer_norms[layer],
                    "alpha_layer_parameter_l2_relative_model": (
                        alpha * layer_norms[layer] / model_norm
                    ),
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
        "candidate_layers": candidates,
        "parameters": sum(parameter.numel() for parameter in model.parameters()),
        "model_parameter_l2": model_norm,
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
    parser.add_argument("--stage", choices=["pilot", "confirmatory"], required=True)
    parser.add_argument("--only-steps", nargs="*", type=int)
    args = parser.parse_args()
    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    allowed = config["pilot_runs"] if args.stage == "pilot" else config["confirmatory_runs"]
    if args.run_id not in allowed:
        raise ValueError(f"run {args.run_id} is not frozen for stage {args.stage}")
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required by the frozen mechanism harness")

    model_name = f"EleutherAI/pythia-{config['model_scale']}m-seed{args.run_id}"
    tokenizer = AutoTokenizer.from_pretrained(
        model_name, revision="main", local_files_only=True
    )
    text_path = (ARC_ROOT / config["text_file"]).resolve()
    text = text_path.read_text(encoding="utf-8")
    all_tokens = tokenizer(text, add_special_tokens=False, return_tensors="pt")["input_ids"][0]
    output = ARC_ROOT / config["output_dir"] / f"pythia-160m-seed{args.run_id}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        payload = json.loads(output.read_text(encoding="utf-8"))
        if payload["stage"] != args.stage:
            raise RuntimeError("existing raw stage does not match requested stage")
    else:
        payload = {
            "arc": "ARC-20260826-5060-004",
            "stage": args.stage,
            "model": model_name,
            "scale_m": config["model_scale"],
            "training_run_id": args.run_id,
            "training_seed_kind": "combined initialization and data-order seed",
            "checkpoint_source": "Hugging Face EleutherAI PolyPythias",
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
            "stage": args.stage,
            "run_id": args.run_id,
            "step": step,
            "runtime_seconds": row["runtime_seconds"],
            "peak_cuda_bytes": row["peak_cuda_bytes"],
            "harness_pass": row["harness_validation"]["pass"],
            "output": str(output),
        }), flush=True)


if __name__ == "__main__":
    main()
