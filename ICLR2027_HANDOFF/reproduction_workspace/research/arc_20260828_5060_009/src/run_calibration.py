"""Outcome-blind continuous-alpha calibration for ARC-009."""

from __future__ import annotations

import argparse
import csv
import ctypes
import gc
import json
import math
import os
import random
import time
from pathlib import Path

import torch
import torch.nn as nn
import torch.nn.functional as F
import yaml
from transformers import AutoModelForCausalLM, AutoTokenizer


ROOT = Path(__file__).resolve().parents[1]
ALLOWED_TARGETS = [
    "target_id", "run_id", "step", "layer", "match_class",
    "selected_beta", "target_kl", "target_nll_damage",
]


def choose(tokens: torch.Tensor, seed: int, count: int, length: int) -> torch.Tensor:
    rng = random.Random(seed)
    usable = len(tokens) - length - 1
    width = usable // count
    rows = []
    for index in range(count):
        start = index * width + rng.randrange(max(1, width - length))
        rows.append(tokens[start:start + length + 1])
    return torch.stack(rows)


def noise_seed(direction: int, eval_seed: int, layer: int, batch_start: int) -> int:
    return int(direction * 1_000_003 + eval_seed * 10_007 + layer * 101 + batch_start)


class Inject(nn.Module):
    def __init__(self, block: nn.Module, kind: str, alpha: float, seed: int):
        super().__init__()
        self.block = block
        self.kind = kind
        self.alpha = float(alpha)
        self.seed = int(seed)
        self.rel_sum = 0.0
        self.count = 0

    def forward(self, hidden, *args, **kwargs):
        output = self.block(hidden, *args, **kwargs)
        base = output[0]
        base_float = base.float()
        if self.kind == "block":
            raw = hidden.float() - base_float
        else:
            generator = torch.Generator(device=base.device)
            generator.manual_seed(self.seed)
            raw = torch.randn(
                base.shape, generator=generator, device=base.device, dtype=torch.float32
            )
        raw_norm = torch.linalg.vector_norm(raw, dim=-1, keepdim=True)
        base_norm = torch.linalg.vector_norm(base_float, dim=-1, keepdim=True)
        delta = self.alpha * base_norm * raw / (raw_norm + 1e-12)
        changed = (base_float + delta).to(base.dtype)
        actual = changed.float() - base_float
        self.rel_sum += (
            torch.linalg.vector_norm(actual, dim=-1) / (base_norm.squeeze(-1) + 1e-12)
        ).sum().item()
        self.count += actual.shape[0] * actual.shape[1]
        return (changed,) + output[1:]

    def relative(self) -> float:
        return self.rel_sum / self.count


def replace(layers: nn.ModuleList, index: int, wrapper: nn.Module) -> nn.ModuleList:
    return nn.ModuleList([wrapper if position == index else block for position, block in enumerate(layers)])


def peak_working_set() -> int | None:
    if os.name != "nt":
        return None
    class Counters(ctypes.Structure):
        _fields_ = [
            ("cb", ctypes.c_ulong), ("PageFaultCount", ctypes.c_ulong),
            ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
            ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
            ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t),
        ]
    counters = Counters()
    counters.cb = ctypes.sizeof(counters)
    ok = ctypes.windll.psapi.GetProcessMemoryInfo(
        ctypes.windll.kernel32.GetCurrentProcess(), ctypes.byref(counters), counters.cb
    )
    return int(counters.PeakWorkingSetSize) if ok else None


class Evaluator:
    def __init__(self, model, original, batch, eval_seed, direction_ids):
        self.model = model
        self.original = original
        self.eval_seed = int(eval_seed)
        self.direction_ids = [int(value) for value in direction_ids]
        self.inputs = batch[:, :-1].to("cuda")
        self.labels = batch[:, 1:].to("cuda")
        self.model.gpt_neox.layers = self.original
        with torch.inference_mode():
            self.intact = self.model(self.inputs, use_cache=False).logits.float()
        self.log_probs = self.intact.log_softmax(-1)
        self.probs = self.log_probs.exp()
        self.first = self.intact.argmax(-1)
        runner = self.intact.clone()
        runner.scatter_(-1, self.first.unsqueeze(-1), -torch.inf)
        self.second = runner.argmax(-1)
        self.baseline_nll = F.cross_entropy(
            self.intact.reshape(-1, self.intact.shape[-1]),
            self.labels.reshape(-1), reduction="mean",
        ).item()
        self.cache: dict[tuple[int, str, str], dict[str, float]] = {}

    @torch.inference_mode()
    def evaluate(self, layer: int, family: str, alpha: float) -> dict[str, float]:
        key = (int(layer), family, f"{float(alpha):.15g}")
        if key in self.cache:
            return self.cache[key]
        acc = {"tokens": 0, "nll": 0.0, "kl": 0.0, "lognorm": 0.0,
               "abscos": 0.0, "hidden": 0.0, "hidden_count": 0}
        identifiers = [0] if family == "block" else self.direction_ids
        for direction in identifiers:
            seed = noise_seed(direction, self.eval_seed, layer, 0) if family == "noise" else 0
            wrapper = Inject(self.original[layer], family, alpha, seed)
            self.model.gpt_neox.layers = replace(self.original, layer, wrapper)
            changed = self.model(self.inputs, use_cache=False).logits.float()
            changed_log_probs = changed.log_softmax(-1)
            delta = changed - self.intact
            logit_norm = torch.linalg.vector_norm(delta, dim=-1)
            boundary = (
                delta.gather(-1, self.first.unsqueeze(-1)).squeeze(-1)
                - delta.gather(-1, self.second.unsqueeze(-1)).squeeze(-1)
            )
            count = self.labels.numel()
            acc["tokens"] += count
            acc["nll"] += F.cross_entropy(
                changed.reshape(-1, changed.shape[-1]), self.labels.reshape(-1), reduction="sum"
            ).item()
            acc["kl"] += (self.probs * (self.log_probs - changed_log_probs)).sum().item()
            acc["lognorm"] += logit_norm.sum().item()
            acc["abscos"] += (boundary / (math.sqrt(2) * logit_norm + 1e-12)).abs().sum().item()
            acc["hidden"] += wrapper.relative() * wrapper.count
            acc["hidden_count"] += wrapper.count
        self.model.gpt_neox.layers = self.original
        result = {
            "kl": acc["kl"] / acc["tokens"],
            "nll_damage": acc["nll"] / acc["tokens"] - self.baseline_nll,
            "output_logit_norm": acc["lognorm"] / acc["tokens"],
            "output_abs_cosine": acc["abscos"] / acc["tokens"],
            "hidden_relative_norm": acc["hidden"] / acc["hidden_count"],
        }
        self.cache[key] = result
        return result


def safe_log_ratio(value: float, target: float) -> float:
    epsilon = 1e-12
    return abs(math.log(max(value, epsilon) / max(target, epsilon)))


def pair_objective(block: dict[str, float], noise: dict[str, float], target: dict) -> float:
    objective = sum(
        safe_log_ratio(value, target_value)
        for value, target_value in (
            (block["kl"], target["target_kl"]),
            (noise["kl"], target["target_kl"]),
            (block["nll_damage"], target["target_nll_damage"]),
            (noise["nll_damage"], target["target_nll_damage"]),
        )
    )
    objective += safe_log_ratio(noise["kl"], block["kl"])
    objective += safe_log_ratio(noise["nll_damage"], block["nll_damage"])
    objective += 0.5 * safe_log_ratio(noise["hidden_relative_norm"], block["hidden_relative_norm"])
    objective += 0.5 * safe_log_ratio(noise["output_logit_norm"], block["output_logit_norm"])
    objective += 5.0 * abs(noise["output_abs_cosine"] - block["output_abs_cosine"])
    return objective


def logspace(low: float, high: float, count: int) -> list[float]:
    left, right = math.log(low), math.log(high)
    return [math.exp(left + (right - left) * index / (count - 1)) for index in range(count)]


def solve_cell(evaluator: Evaluator, target: dict, cfg: dict):
    beta = target["selected_beta"]
    low = beta * float(cfg["alpha_multiplier_min"])
    high = beta * float(cfg["alpha_multiplier_max"])
    pools: dict[str, set[float]] = {"block": {low, beta, high}, "noise": {low, beta, high}}
    roots = []
    no_bracket = False
    numerical = False
    manifest = []

    for family in ("block", "noise"):
        for metric, target_key in (("kl", "target_kl"), ("nll_damage", "target_nll_damage")):
            target_value = target[target_key]
            left, right = low, high
            left_result = evaluator.evaluate(target["layer"], family, left)
            right_result = evaluator.evaluate(target["layer"], family, right)
            left_value, right_value = left_result[metric], right_result[metric]
            finite = all(math.isfinite(value) for value in (left_value, right_value, target_value))
            bracketed = finite and min(left_value, right_value) <= target_value <= max(left_value, right_value)
            root = None
            iterations = 0
            if not finite:
                numerical = True
            elif not bracketed:
                no_bracket = True
                pools[family].update(logspace(low, high, 17))
            else:
                increasing = right_value >= left_value
                for iterations in range(1, int(cfg["root_max_iterations"]) + 1):
                    middle = math.sqrt(left * right)
                    middle_result = evaluator.evaluate(target["layer"], family, middle)
                    middle_value = middle_result[metric]
                    pools[family].add(middle)
                    if not math.isfinite(middle_value):
                        numerical = True
                        break
                    relative_error = abs(middle_value - target_value) / max(abs(target_value), 1e-12)
                    if relative_error <= float(cfg["root_relative_metric_tolerance"]):
                        root = middle
                        break
                    if abs(math.log(right / left)) <= float(cfg["root_log_alpha_tolerance"]):
                        root = middle
                        break
                    if (middle_value < target_value) == increasing:
                        left = middle
                    else:
                        right = middle
                if root is None and not numerical:
                    root = math.sqrt(left * right)
                    pools[family].add(root)
            if root is not None:
                roots.append((family, metric, root))
            manifest.append({
                "target_id": target["target_id"], "run_id": target["run_id"],
                "step": target["step"], "layer": target["layer"], "family": family,
                "target_metric": metric, "target_value": target_value,
                "alpha_min": low, "alpha_max": high, "bracketed": bracketed,
                "root_alpha": root, "iterations": iterations,
            })

    for family in ("block", "noise"):
        family_roots = [root for root_family, _, root in roots if root_family == family]
        if len(family_roots) == 2:
            pools[family].add(math.sqrt(family_roots[0] * family_roots[1]))

    def select_best():
        best = None
        for block_alpha in sorted(pools["block"]):
            block = evaluator.evaluate(target["layer"], "block", block_alpha)
            for noise_alpha in sorted(pools["noise"]):
                noise = evaluator.evaluate(target["layer"], "noise", noise_alpha)
                objective = pair_objective(block, noise, target)
                candidate = (objective, block_alpha, noise_alpha, block, noise)
                if best is None or candidate[0] < best[0]:
                    best = candidate
        return best

    best = select_best()
    previous = best[0]
    converged = False
    for round_index in range(int(cfg["coordinate_refinement_rounds"])):
        step = float(cfg["coordinate_initial_log_step"]) / (2 ** round_index)
        for family, current in (("block", best[1]), ("noise", best[2])):
            pools[family].add(max(low, min(high, current * math.exp(-step))))
            pools[family].add(max(low, min(high, current * math.exp(step))))
        best = select_best()
        relative_change = abs(previous - best[0]) / max(abs(previous), 1e-12)
        if relative_change <= float(cfg["objective_relative_convergence"]):
            converged = True
        previous = best[0]

    objective, block_alpha, noise_alpha, block, noise = best
    selected_values = list(block.values()) + list(noise.values()) + [objective]
    numerical = numerical or not all(math.isfinite(value) for value in selected_values)
    pathological = numerical or any(
        value > limit for value, limit in (
            (block["kl"], 5.0), (noise["kl"], 5.0),
            (block["nll_damage"], 5.0), (noise["nll_damage"], 5.0),
            (block["hidden_relative_norm"], 2.0), (noise["hidden_relative_norm"], 2.0),
        )
    )
    log_width = math.log(high / low)
    boundary = (
        min(math.log(block_alpha / low), math.log(high / block_alpha),
            math.log(noise_alpha / low), math.log(high / noise_alpha)) / log_width <= 0.01
    )
    row = {
        "target_id": target["target_id"], "run_id": target["run_id"],
        "step": target["step"], "layer": target["layer"],
        "selected_beta": beta, "target_kl": target["target_kl"],
        "target_nll_damage": target["target_nll_damage"],
        "alpha_min": low, "alpha_max": high,
        "block_alpha": block_alpha, "noise_alpha": noise_alpha,
        "block_alpha_multiplier": block_alpha / beta,
        "noise_alpha_multiplier": noise_alpha / beta,
        "objective": objective,
        **{f"block_{key}": value for key, value in block.items()},
        **{f"noise_{key}": value for key, value in noise.items()},
        "no_bracket": no_bracket, "numerical_issue": numerical,
        "pathological": pathological, "boundary_selected": boundary,
        "coordinate_converged": converged,
        "block_evaluations": sum(key[0] == target["layer"] and key[1] == "block" for key in evaluator.cache),
        "noise_evaluations": sum(key[0] == target["layer"] and key[1] == "noise" for key in evaluator.cache),
    }
    return row, manifest


def load_targets(path: Path, run_id: int) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != ALLOWED_TARGETS:
            raise SystemExit("BLINDING_FAILURE: sanitized target schema changed")
        rows = [row for row in reader if int(row["run_id"]) == run_id and row["match_class"] == "A"]
    for row in rows:
        row.update(
            run_id=int(row["run_id"]), step=int(row["step"]), layer=int(row["layer"]),
            selected_beta=float(row["selected_beta"]), target_kl=float(row["target_kl"]),
            target_nll_damage=float(row["target_nll_damage"]),
        )
    return rows


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--run-id", type=int, required=True)
    args = parser.parse_args()
    for name in ("HF_HUB_OFFLINE", "TRANSFORMERS_OFFLINE", "HF_DATASETS_OFFLINE", "WANDB_MODE"):
        expected = "offline" if name == "WANDB_MODE" else "1"
        if os.environ.get(name) != expected:
            raise SystemExit(f"LOCAL_ARTIFACT_MISSING: required offline variable {name}={expected} not set")
    cfg = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    targets = load_targets((ROOT / cfg["sanitized_targets"]).resolve(), args.run_id)
    if not targets:
        raise SystemExit("LOCAL_ARTIFACT_MISSING: no sanitized targets for run")
    model_name = f"EleutherAI/pythia-{cfg['model_scale']}m-seed{args.run_id}"
    tokenizer = AutoTokenizer.from_pretrained(model_name, revision="main", local_files_only=True)
    text_path = (ROOT / cfg["text_file"]).resolve()
    if not text_path.is_file():
        raise SystemExit("LOCAL_ARTIFACT_MISSING: frozen text absent")
    tokens = tokenizer(
        text_path.read_text(encoding="utf-8"), add_special_tokens=False, return_tensors="pt"
    )["input_ids"][0]
    sequences = choose(tokens, int(cfg["calibration_seed"]), int(cfg["calibration_sequences"]), int(cfg["sequence_length"]))

    started = time.perf_counter()
    cpu_started = time.process_time()
    torch.cuda.reset_peak_memory_stats()
    output_rows = []
    manifest_rows = []
    checkpoints = []
    for revision, step in zip(cfg["revisions"], cfg["checkpoint_steps"]):
        checkpoint_started = time.perf_counter()
        model = AutoModelForCausalLM.from_pretrained(
            model_name, revision=revision, dtype=torch.float16, local_files_only=True
        ).to("cuda").eval()
        original = model.gpt_neox.layers
        evaluator = Evaluator(
            model, original, sequences, int(cfg["calibration_seed"]), cfg["noise_direction_ids"]
        )
        checkpoint_targets = [target for target in targets if target["step"] == int(step)]
        for target in checkpoint_targets:
            row, manifest = solve_cell(evaluator, target, cfg)
            output_rows.append(row)
            manifest_rows.extend(manifest)
        torch.cuda.synchronize()
        checkpoints.append({
            "revision": revision, "step": int(step), "cells": len(checkpoint_targets),
            "commit_hash": getattr(model.config, "_commit_hash", None),
            "runtime_seconds": time.perf_counter() - checkpoint_started,
        })
        del evaluator, model
        gc.collect()
        torch.cuda.empty_cache()

    raw = ROOT / "raw"
    write_csv(raw / f"calibration_seed{args.run_id}.csv", output_rows)
    write_csv(raw / f"alpha_manifest_seed{args.run_id}.csv", manifest_rows)
    metadata = {
        "arc": cfg["arc"], "run_id": args.run_id, "outcome_blind": True,
        "cells": len(output_rows), "wall_seconds": time.perf_counter() - started,
        "cpu_seconds": time.process_time() - cpu_started,
        "peak_cuda_bytes": int(torch.cuda.max_memory_allocated()),
        "peak_working_set_bytes": peak_working_set(), "checkpoints": checkpoints,
        "downloads": 0, "api_cost_usd": 0, "external_compute_cost_usd": 0,
    }
    (raw / f"calibration_seed{args.run_id}.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )
    print(json.dumps(metadata, indent=2), flush=True)


if __name__ == "__main__":
    main()

