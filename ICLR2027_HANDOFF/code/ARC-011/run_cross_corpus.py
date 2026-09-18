#!/usr/bin/env python3
"""Run the preregistered ARC-011 corpus-only intervention assay."""

from __future__ import annotations

import argparse
import csv
import gc
import hashlib
import importlib.util
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
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("HF_DATASETS_OFFLINE", "1")
os.environ.setdefault("WANDB_MODE", "offline")
from transformers import AutoModelForCausalLM, AutoTokenizer


ROOT = Path(__file__).resolve().parents[1]
BASE_PATH = ROOT.parent / "arc_20260826_5060_004" / "src" / "run_mechanism.py"


def load_base():
    spec = importlib.util.spec_from_file_location("arc004_frozen_runner", BASE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import frozen intervention code: {BASE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = load_base()
ResidualAttenuator = BASE.ResidualAttenuator
middle_layers = BASE.middle_layers
parameter_norm = BASE.parameter_norm
replace_one = BASE.replace_one


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def canonical_top1(logits: torch.Tensor) -> torch.Tensor:
    """Lowest token index among exact maxima, identical for both families."""
    return torch.argmax(logits, dim=-1)


def choose_sequences(tokens: torch.Tensor, seed: int, count: int, length: int) -> torch.Tensor:
    rng = random.Random(seed)
    usable = len(tokens) - length - 1
    if usable <= 0:
        raise ValueError("evaluation text is too short")
    width = usable // count
    starts = [i * width + rng.randrange(max(1, width - length)) for i in range(count)]
    return torch.stack([tokens[start : start + length + 1] for start in starts])


def verify_manifest(tokens: torch.Tensor, config: dict) -> dict:
    manifest_path = (ROOT / config["corpus_manifest_file"]).resolve()
    with manifest_path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    expected = len(config["evaluation_seeds"]) * config["sequences_per_seed"]
    if len(rows) != expected:
        raise RuntimeError(f"manifest has {len(rows)} rows; expected {expected}")
    for row in rows:
        start = int(row["token_start"])
        end = int(row["token_end_exclusive"])
        token_slice = tokens[start:end].tolist()
        digest = hashlib.sha256(
            json.dumps(token_slice, separators=(",", ":")).encode("ascii")
        ).hexdigest().upper()
        if digest != row["token_ids_sha256"]:
            raise RuntimeError(
                f"manifest token mismatch seed={row['evaluation_seed']} seq={row['sequence_index']}"
            )
    return {"path": str(manifest_path), "sha256": sha256(manifest_path), "rows": len(rows)}


@torch.inference_mode()
def validate_harness(model: torch.nn.Module, sample_inputs: torch.Tensor, atol: float) -> dict:
    result = BASE.validate_wrapper(model, sample_inputs, atol)
    tie = torch.tensor([[[0.0, 1.0, 1.0, -1.0]]], device=sample_inputs.device)
    tie_index = int(canonical_top1(tie).item())
    result.update({
        "canonical_tie_test_index": tie_index,
        "canonical_tie_test_expected": 1,
        "top1_rule": "lowest_token_index_among_exact_logit_maxima",
    })
    result["pass"] = bool(result["pass"] and tie_index == 1)
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
    harness = validate_harness(
        model,
        validation_sequences[:, :-1].to("cuda"),
        float(config["equivalence_logit_atol"]),
    )
    if not harness["pass"]:
        raise RuntimeError(f"frozen intervention harness failed: {harness}")

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
            top_values, _ = probs.topk(2, dim=-1)
            top1 = canonical_top1(logits)
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
                agree = canonical_top1(changed) == top1
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

            del logits, log_probs, probs, top_values, top1, confidence, margin, entropy

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
                            float(item["bin_agree"][index] / bin_count)
                            if bin_count else None
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
        raise RuntimeError("CUDA is required by the frozen harness")

    model_name = f"EleutherAI/pythia-{config['model_scale']}m-seed{args.run_id}"
    tokenizer = AutoTokenizer.from_pretrained(
        model_name, revision="main", local_files_only=True
    )
    text_path = (ROOT / config["derived_text_file"]).resolve()
    text = text_path.read_text(encoding="utf-8")
    all_tokens = tokenizer(
        text, add_special_tokens=False, return_tensors="pt"
    )["input_ids"][0]
    manifest = verify_manifest(all_tokens, config)

    output = ROOT / config["output_dir"] / f"pythia-160m-seed{args.run_id}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        payload = json.loads(output.read_text(encoding="utf-8"))
        if payload["stage"] != args.stage:
            raise RuntimeError("existing raw stage does not match requested stage")
    else:
        payload = {
            "arc": config["arc"],
            "stage": args.stage,
            "model": model_name,
            "scale_m": config["model_scale"],
            "training_run_id": args.run_id,
            "training_seed_kind": "combined initialization and data-order seed",
            "checkpoint_source": "local Hugging Face cache: EleutherAI PolyPythias",
            "config": config,
            "corpus": {
                "name": "HellaSwag validation correct continuations",
                "text_path": str(text_path),
                "text_sha256": sha256(text_path),
                "text_tokens": int(len(all_tokens)),
                "manifest": manifest,
            },
            "top1_rule": config["top1_rule"],
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
        output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
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

