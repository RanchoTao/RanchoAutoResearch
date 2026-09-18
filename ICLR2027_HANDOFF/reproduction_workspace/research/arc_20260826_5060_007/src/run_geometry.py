"""Extract frozen ARC-007 logit geometry for block deletion and activation noise."""

from __future__ import annotations

import argparse
import csv
import gc
import hashlib
import json
import math
import os
import sys
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


ARC_ROOT = Path(__file__).resolve().parents[1]
ARC006_SRC = ARC_ROOT.parent / "arc_20260826_5060_006" / "src"
sys.path.insert(0, str(ARC006_SRC))
from run_targeting import (  # noqa: E402
    NormControlledActivationNoise,
    choose_sequences,
    deterministic_noise_seed,
    replace_one,
    validate_harness,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def new_accumulator() -> dict:
    return {
        "tokens": 0,
        "nll_sum": 0.0,
        "kl_sum": 0.0,
        "flips": 0,
        "top2_flips": 0,
        "other_flips": 0,
        "stratum_total": np.zeros(3, dtype=np.int64),
        "stratum_flips": np.zeros(3, dtype=np.int64),
        "identity_max": 0.0,
        "delta_b": [],
        "delta_margin": [],
        "logit_norm": [],
        "cosine": [],
        "flipped": [],
        "top2_flip": [],
        "stratum": [],
    }


@torch.inference_mode()
def observe(
    accumulator: dict,
    intact_logits: torch.Tensor,
    intact_log_probs: torch.Tensor,
    intact_probs: torch.Tensor,
    intact_top1: torch.Tensor,
    intact_top2: torch.Tensor,
    intact_margin: torch.Tensor,
    changed_logits: torch.Tensor,
    labels: torch.Tensor,
    strata: torch.Tensor,
) -> None:
    changed_log_probs = changed_logits.log_softmax(-1)
    changed_top1 = changed_logits.argmax(-1)
    flipped = changed_top1 != intact_top1
    top2_flip = changed_top1 == intact_top2
    other_flip = flipped & ~top2_flip

    delta_logits = changed_logits - intact_logits
    logit_norm = torch.linalg.vector_norm(delta_logits, dim=-1)
    delta_c1 = delta_logits.gather(-1, intact_top1.unsqueeze(-1)).squeeze(-1)
    delta_c2 = delta_logits.gather(-1, intact_top2.unsqueeze(-1)).squeeze(-1)
    delta_b = delta_c1 - delta_c2
    changed_c1 = changed_logits.gather(-1, intact_top1.unsqueeze(-1)).squeeze(-1)
    changed_c2 = changed_logits.gather(-1, intact_top2.unsqueeze(-1)).squeeze(-1)
    delta_margin = changed_c1 - changed_c2 - intact_margin
    cosine = delta_b / (math.sqrt(2.0) * logit_norm + 1e-12)

    count = int(labels.numel())
    accumulator["tokens"] += count
    accumulator["nll_sum"] += float(F.cross_entropy(
        changed_logits.reshape(-1, changed_logits.shape[-1]),
        labels.reshape(-1), reduction="sum",
    ).item())
    accumulator["kl_sum"] += float(
        (intact_probs * (intact_log_probs - changed_log_probs)).sum().item()
    )
    accumulator["flips"] += int(flipped.sum().item())
    accumulator["top2_flips"] += int(top2_flip.sum().item())
    accumulator["other_flips"] += int(other_flip.sum().item())
    accumulator["identity_max"] = max(
        accumulator["identity_max"],
        float((delta_b - delta_margin).abs().max().item()),
    )
    for index in range(3):
        mask = strata == index
        accumulator["stratum_total"][index] += int(mask.sum().item())
        accumulator["stratum_flips"][index] += int(flipped[mask].sum().item())

    accumulator["delta_b"].append(delta_b.detach().cpu().numpy().astype(np.float32))
    accumulator["delta_margin"].append(delta_margin.detach().cpu().numpy().astype(np.float32))
    accumulator["logit_norm"].append(logit_norm.detach().cpu().numpy().astype(np.float32))
    accumulator["cosine"].append(cosine.detach().cpu().numpy().astype(np.float32))
    accumulator["flipped"].append(flipped.detach().cpu().numpy().astype(np.uint8))
    accumulator["top2_flip"].append(top2_flip.detach().cpu().numpy().astype(np.uint8))
    accumulator["stratum"].append(strata.detach().cpu().numpy().astype(np.uint8))


def concatenate(accumulator: dict, field: str) -> np.ndarray:
    return np.concatenate([np.asarray(value).reshape(-1) for value in accumulator[field]])


def frozen_top1_and_runner_up(logits: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Anchor c1 to the frozen argmax rule, then select c2 after masking c1."""
    c1 = logits.argmax(dim=-1)
    runner_logits = logits.clone()
    runner_logits.scatter_(-1, c1.unsqueeze(-1), -torch.inf)
    c2 = runner_logits.argmax(dim=-1)
    z_c1 = logits.gather(-1, c1.unsqueeze(-1)).squeeze(-1)
    z_c2 = logits.gather(-1, c2.unsqueeze(-1)).squeeze(-1)
    return c1, c2, z_c1 - z_c2


def summarize_accumulators(accumulators: list[dict], baseline_nll: float) -> dict:
    fields = ["delta_b", "delta_margin", "logit_norm", "cosine", "flipped", "top2_flip", "stratum"]
    arrays = {field: np.concatenate([concatenate(item, field) for item in accumulators]) for field in fields}
    tokens = int(sum(item["tokens"] for item in accumulators))
    nll = float(sum(item["nll_sum"] for item in accumulators) / tokens)
    strata = []
    for index in range(3):
        total = int(sum(item["stratum_total"][index] for item in accumulators))
        flips = int(sum(item["stratum_flips"][index] for item in accumulators))
        strata.append({"stratum": index, "count": total, "flip_rate": flips / total})
    flipped = arrays["flipped"].astype(bool)
    return {
        "tokens": tokens,
        "intervened_nll": nll,
        "nll_damage": nll - baseline_nll,
        "kl": float(sum(item["kl_sum"] for item in accumulators) / tokens),
        "top1_flip_rate": float(arrays["flipped"].mean()),
        "top1_retained_rate": float(1.0 - arrays["flipped"].mean()),
        "top1_to_intact_top2_rate": float(arrays["top2_flip"].mean()),
        "other_flip_rate": float((arrays["flipped"] - arrays["top2_flip"]).mean()),
        "top1_to_top2_share_of_flips": float(arrays["top2_flip"][flipped].mean()) if flipped.any() else None,
        "delta_b_mean": float(arrays["delta_b"].mean()),
        "delta_b_median": float(np.median(arrays["delta_b"])),
        "delta_b_q10": float(np.quantile(arrays["delta_b"], 0.10)),
        "delta_b_q25": float(np.quantile(arrays["delta_b"], 0.25)),
        "delta_b_q75": float(np.quantile(arrays["delta_b"], 0.75)),
        "delta_b_q90": float(np.quantile(arrays["delta_b"], 0.90)),
        "delta_margin_mean": float(arrays["delta_margin"].mean()),
        "delta_margin_identity_max_abs": float(max(item["identity_max"] for item in accumulators)),
        "logit_delta_norm_mean": float(arrays["logit_norm"].mean()),
        "logit_delta_norm_median": float(np.median(arrays["logit_norm"])),
        "cosine_alignment_mean": float(arrays["cosine"].mean()),
        "abs_cosine_alignment_mean": float(np.abs(arrays["cosine"]).mean()),
        "boundary_strata": strata,
    }


@torch.inference_mode()
def intact_margin_thresholds(model, original, sequences: torch.Tensor, batch_size: int) -> tuple[float, float]:
    values = []
    for start in range(0, len(sequences), batch_size):
        batch = sequences[start : start + batch_size].to("cuda")
        model.gpt_neox.layers = original
        logits = model(batch[:, :-1], use_cache=False).logits.float()
        _, _, margin = frozen_top1_and_runner_up(logits)
        values.append(margin.cpu().numpy().reshape(-1))
    merged = np.concatenate(values)
    return tuple(float(value) for value in np.quantile(merged, [1 / 3, 2 / 3]))


@torch.inference_mode()
def evaluate_checkpoint(
    model_name: str,
    revision: str,
    step: int,
    all_tokens: torch.Tensor,
    targets: list[dict],
    config: dict,
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
        raise RuntimeError(f"geometry harness failed: {harness}")

    accumulators: dict[tuple[str, str, int], dict] = {}
    for target in targets:
        accumulators[(target["target_id"], "block", 0)] = new_accumulator()
        for direction in config["noise_direction_ids"]:
            accumulators[(target["target_id"], "noise", int(direction))] = new_accumulator()
    intact_margins = []
    intact_seed_ids = []
    baseline_nll_sum = 0.0
    baseline_tokens = 0

    for evaluation_seed in config["evaluation_seeds"]:
        sequences = choose_sequences(
            all_tokens, int(evaluation_seed), int(config["sequences_per_seed"]),
            int(config["sequence_length"]),
        )
        low, high = intact_margin_thresholds(
            model, original, sequences, int(config["batch_size"])
        )
        for batch_start in range(0, len(sequences), int(config["batch_size"])):
            batch = sequences[batch_start : batch_start + int(config["batch_size"])].to("cuda")
            inputs, labels = batch[:, :-1], batch[:, 1:]
            model.gpt_neox.layers = original
            logits = model(inputs, use_cache=False).logits.float()
            log_probs = logits.log_softmax(-1)
            probs = log_probs.exp()
            c1, c2, margin = frozen_top1_and_runner_up(logits)
            strata = torch.bucketize(
                margin.contiguous(),
                torch.tensor([low, high], device=margin.device, dtype=margin.dtype),
            )
            baseline_nll_sum += float(F.cross_entropy(
                logits.reshape(-1, logits.shape[-1]), labels.reshape(-1), reduction="sum"
            ).item())
            baseline_tokens += int(labels.numel())
            intact_margins.append(margin.cpu().numpy().astype(np.float32))
            intact_seed_ids.append(np.full(margin.numel(), int(evaluation_seed), dtype=np.int16))

            for target in targets:
                layer = int(target["layer"])
                model.gpt_neox.layers = torch.nn.ModuleList(
                    [block for index, block in enumerate(original) if index != layer]
                )
                block_logits = model(inputs, use_cache=False).logits.float()
                observe(
                    accumulators[(target["target_id"], "block", 0)],
                    logits, log_probs, probs, c1, c2, margin,
                    block_logits, labels, strata,
                )
                del block_logits

                beta = float(target["selected_beta"])
                for direction in config["noise_direction_ids"]:
                    direction = int(direction)
                    seed = deterministic_noise_seed(
                        direction, int(evaluation_seed), layer, batch_start
                    )
                    wrapper = NormControlledActivationNoise(original[layer], beta, seed)
                    model.gpt_neox.layers = replace_one(original, layer, wrapper)
                    noise_logits = model(inputs, use_cache=False).logits.float()
                    observe(
                        accumulators[(target["target_id"], "noise", direction)],
                        logits, log_probs, probs, c1, c2, margin,
                        noise_logits, labels, strata,
                    )
                    del wrapper, noise_logits
            del batch, inputs, labels, logits, log_probs, probs, c1, c2, margin, strata

    baseline_nll = baseline_nll_sum / baseline_tokens
    geometry_rows = []
    arrays: dict[str, np.ndarray] = {
        "intact_margin": np.concatenate([value.reshape(-1) for value in intact_margins]),
        "evaluation_seed": np.concatenate(intact_seed_ids),
    }
    for target in sorted(targets, key=lambda row: int(row["layer"])):
        target_id = target["target_id"]
        for family in ["block", "noise"]:
            directions = [0] if family == "block" else [int(x) for x in config["noise_direction_ids"]]
            selected = [accumulators[(target_id, family, direction)] for direction in directions]
            row = summarize_accumulators(selected, baseline_nll)
            row.update({
                "target_id": target_id,
                "run_id": int(target["run_id"]),
                "step": int(target["step"]),
                "layer": int(target["layer"]),
                "match_class": target["match_class"],
                "selected_beta": float(target["selected_beta"]),
                "family": family,
                "intact_margin_mean": float(arrays["intact_margin"].mean()),
                "intact_margin_median": float(np.median(arrays["intact_margin"])),
                "intact_margin_q10": float(np.quantile(arrays["intact_margin"], 0.10)),
                "intact_margin_q25": float(np.quantile(arrays["intact_margin"], 0.25)),
                "intact_margin_q75": float(np.quantile(arrays["intact_margin"], 0.75)),
                "intact_margin_q90": float(np.quantile(arrays["intact_margin"], 0.90)),
                "baseline_nll": float(baseline_nll),
            })
            geometry_rows.append(row)
            for direction in directions:
                item = accumulators[(target_id, family, direction)]
                prefix = f"l{target['layer']}_{family}_d{direction}"
                for field in ["delta_b", "delta_margin", "logit_norm", "cosine", "flipped", "top2_flip", "stratum"]:
                    arrays[f"{prefix}_{field}"] = concatenate(item, field)

    array_path = ARC_ROOT / config["raw_array_dir"] / f"seed{targets[0]['run_id']}_step{step}.npz"
    array_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(array_path, **arrays)
    result = {
        "revision": revision,
        "commit_hash": getattr(model.config, "_commit_hash", None),
        "step": int(step),
        "harness_validation": harness,
        "baseline_tokens": int(baseline_tokens),
        "baseline_nll": float(baseline_nll),
        "geometry_rows": geometry_rows,
        "array_file": str(array_path),
        "array_sha256": sha256(array_path),
        "runtime_seconds": float(time.perf_counter() - started),
        "peak_cuda_bytes": int(torch.cuda.max_memory_allocated()),
    }
    model.gpt_neox.layers = original
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
        raise ValueError("run is outside the frozen ARC-007 set")
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required by the frozen geometry extractor")

    manifest_path = (ARC_ROOT / config["cell_manifest"]).resolve()
    with manifest_path.open(newline="", encoding="utf-8") as handle:
        manifest = list(csv.DictReader(handle))
    for row in manifest:
        for field in ["run_id", "step", "layer"]:
            row[field] = int(row[field])
        row["selected_beta"] = float(row["selected_beta"])
    manifest = [row for row in manifest if row["run_id"] == run_id]
    if len(manifest) != 30:
        raise RuntimeError(f"expected 30 frozen cells for run {run_id}, found {len(manifest)}")

    model_name = f"EleutherAI/pythia-{config['model_scale']}m-seed{run_id}"
    tokenizer = AutoTokenizer.from_pretrained(model_name, revision="main", local_files_only=True)
    text_path = (ARC_ROOT / config["text_file"]).resolve()
    all_tokens = tokenizer(
        text_path.read_text(encoding="utf-8"), add_special_tokens=False,
        return_tensors="pt",
    )["input_ids"][0]
    output = ARC_ROOT / config["raw_output_dir"] / f"pythia-160m-seed{run_id}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "arc": config["arc"],
        "model": model_name,
        "run_id": run_id,
        "cell_manifest_sha256": sha256(manifest_path),
        "config": config,
        "checkpoints": [],
    }
    for revision, step in zip(config["revisions"], config["checkpoint_steps"]):
        targets = [row for row in manifest if row["step"] == int(step)]
        result = evaluate_checkpoint(
            model_name, revision, int(step), all_tokens, targets, config
        )
        payload["checkpoints"].append(result)
        output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(json.dumps({
            "stage": "geometry", "run_id": run_id, "step": int(step),
            "cell_count": len(targets), "family_rows": len(result["geometry_rows"]),
            "runtime_seconds": result["runtime_seconds"],
            "peak_cuda_bytes": result["peak_cuda_bytes"],
            "harness_pass": result["harness_validation"]["pass"],
        }), flush=True)


if __name__ == "__main__":
    main()
