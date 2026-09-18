"""ARC-22 fixed-multiset duplicate-burstiness experiment."""

from __future__ import annotations

import argparse
import json
import math
import random
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import yaml


@dataclass(frozen=True)
class DataSpec:
    vocab_size: int
    sequence_length: int
    total_exposures: int
    duplicate_fraction: float
    repeated_subset_size: int
    validation_sequences: int


class TinyCausalTransformer(nn.Module):
    def __init__(self, vocab: int, seq_len: int, d_model: int, n_layers: int,
                 n_heads: int, d_mlp: int) -> None:
        super().__init__()
        self.token = nn.Embedding(vocab, d_model)
        positions = torch.arange(seq_len, dtype=torch.float32)[:, None]
        frequencies = torch.exp(
            torch.arange(0, d_model, 2, dtype=torch.float32)
            * (-math.log(10000.0) / d_model)
        )
        pe = torch.zeros(seq_len, d_model)
        pe[:, 0::2] = torch.sin(positions * frequencies)
        pe[:, 1::2] = torch.cos(positions * frequencies)
        self.register_buffer("position", pe, persistent=False)
        layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=n_heads, dim_feedforward=d_mlp,
            dropout=0.0, activation="gelu", batch_first=True, norm_first=True,
        )
        self.encoder = nn.TransformerEncoder(
            layer, num_layers=n_layers, enable_nested_tensor=False
        )
        self.norm = nn.LayerNorm(d_model)
        self.output = nn.Linear(d_model, vocab, bias=False)

    def forward(self, tokens: torch.Tensor) -> torch.Tensor:
        length = tokens.shape[1]
        hidden = self.token(tokens) + self.position[:length]
        mask = torch.triu(
            torch.ones(length, length, dtype=torch.bool, device=tokens.device),
            diagonal=1,
        )
        return self.output(self.norm(self.encoder(hidden, mask=mask)))


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def generate_sequences(generator: str, count: int, spec: DataSpec,
                       rng: np.random.Generator) -> np.ndarray:
    sequences = np.empty((count, spec.sequence_length), dtype=np.int64)
    if generator == "markov":
        sequences[:, 0] = rng.integers(0, spec.vocab_size, size=count)
        offsets = np.asarray([1, 3, 7, 13], dtype=np.int64)
        probabilities = np.asarray([0.55, 0.25, 0.15, 0.05])
        for position in range(1, spec.sequence_length):
            choice = rng.choice(len(offsets), size=count, p=probabilities)
            sequences[:, position] = (
                sequences[:, position - 1] + offsets[choice]
            ) % spec.vocab_size
    elif generator == "recurrence4":
        sequences[:, :4] = rng.integers(
            0, spec.vocab_size, size=(count, 4)
        )
        for position in range(4, spec.sequence_length):
            sequences[:, position] = (
                sequences[:, position - 1]
                + 2 * sequences[:, position - 2]
                + 3 * sequences[:, position - 3]
                + 5 * sequences[:, position - 4]
            ) % spec.vocab_size
    else:
        raise ValueError(generator)
    return sequences


def duplicate_layout(spec: DataSpec) -> tuple[int, int, int]:
    repeated_exposures = round(spec.total_exposures * spec.duplicate_fraction)
    if repeated_exposures % spec.repeated_subset_size:
        raise ValueError("repeated exposures must divide repeated_subset_size")
    repetitions = repeated_exposures // spec.repeated_subset_size
    nonrepeated = spec.total_exposures - repeated_exposures
    return nonrepeated, repeated_exposures, repetitions


def make_schedule(condition: str, spec: DataSpec,
                  rng: np.random.Generator) -> np.ndarray:
    nonrepeated, repeated_exposures, repetitions = duplicate_layout(spec)
    if condition == "all_unique":
        return rng.permutation(spec.total_exposures)

    unique_ids = rng.permutation(nonrepeated)
    repeated_ids = nonrepeated + np.tile(
        np.arange(spec.repeated_subset_size, dtype=np.int64), repetitions
    )
    # One shared shuffle pattern per condition RNG seed; the multiset is exact.
    rng.shuffle(repeated_ids)
    if condition == "duplicate_random":
        schedule = np.concatenate([unique_ids, repeated_ids])
        rng.shuffle(schedule)
        return schedule
    if condition == "duplicate_spaced":
        schedule = np.empty(spec.total_exposures, dtype=np.int64)
        positions = np.floor(
            (np.arange(repeated_exposures) + 0.5)
            * spec.total_exposures / repeated_exposures
        ).astype(np.int64)
        repeated_mask = np.zeros(spec.total_exposures, dtype=bool)
        repeated_mask[positions] = True
        if repeated_mask.sum() != repeated_exposures:
            raise AssertionError("spaced positions are not unique")
        schedule[repeated_mask] = repeated_ids
        schedule[~repeated_mask] = unique_ids
        return schedule
    insertion = {
        "duplicate_massed_early": 0,
        "duplicate_massed_middle": nonrepeated // 2,
        "duplicate_massed_late": nonrepeated,
    }.get(condition)
    if insertion is None:
        raise ValueError(condition)
    return np.concatenate([
        unique_ids[:insertion], repeated_ids, unique_ids[insertion:]
    ])


def token_loss(logits: torch.Tensor, targets: torch.Tensor,
               generator: str) -> torch.Tensor:
    # In recurrence4 the first four values are random; target index 3 is the
    # first deterministic recurrence target. Markov targets are all predictable.
    start = 3 if generator == "recurrence4" else 0
    return F.cross_entropy(
        logits[:, start:].reshape(-1, logits.shape[-1]),
        targets[:, start:].reshape(-1),
    )


@torch.no_grad()
def evaluate(model: nn.Module, sequences: np.ndarray, generator: str,
             batch_size: int, device: torch.device) -> dict[str, float]:
    model.eval()
    total_loss = total_correct = total_tokens = 0.0
    start = 3 if generator == "recurrence4" else 0
    for offset in range(0, len(sequences), batch_size):
        batch = torch.from_numpy(sequences[offset:offset + batch_size]).to(device)
        inputs, targets = batch[:, :-1], batch[:, 1:]
        logits = model(inputs)
        relevant_logits = logits[:, start:]
        relevant_targets = targets[:, start:]
        count = relevant_targets.numel()
        total_loss += float(F.cross_entropy(
            relevant_logits.reshape(-1, logits.shape[-1]),
            relevant_targets.reshape(-1), reduction="sum"
        ))
        total_correct += float(
            (relevant_logits.argmax(-1) == relevant_targets).sum()
        )
        total_tokens += count
    return {
        "nll": total_loss / total_tokens,
        "accuracy": total_correct / total_tokens,
        "tokens": int(total_tokens),
    }


def train_one(config: dict, generator: str, condition: str, seed: int,
              output_dir: Path, device: torch.device) -> dict:
    data_cfg = config["data"]
    spec = DataSpec(**data_cfg)
    nonrepeated, repeated_exposures, repetitions = duplicate_layout(spec)

    # Data are fixed within generator/seed across conditions.
    data_rng = np.random.default_rng(10_000 + seed * 101 +
                                     (0 if generator == "markov" else 1))
    pool = generate_sequences(generator, spec.total_exposures, spec, data_rng)
    validation = generate_sequences(
        generator, spec.validation_sequences, spec, data_rng
    )
    repeated_subset = pool[nonrepeated:nonrepeated + spec.repeated_subset_size]

    schedule_seed = 20_000 + seed * 103 + {
        "all_unique": 1,
        "duplicate_random": 2,
        "duplicate_spaced": 3,
        "duplicate_massed_early": 4,
        "duplicate_massed_middle": 5,
        "duplicate_massed_late": 6,
    }[condition]
    schedule = make_schedule(condition, spec, np.random.default_rng(schedule_seed))
    expected_length = spec.total_exposures
    assert len(schedule) == expected_length
    if condition != "all_unique":
        counts = np.bincount(schedule, minlength=nonrepeated + spec.repeated_subset_size)
        assert np.all(counts[:nonrepeated] == 1)
        assert np.all(counts[nonrepeated:] == repetitions)

    seed_everything(seed)
    model = TinyCausalTransformer(
        vocab=spec.vocab_size, seq_len=spec.sequence_length - 1,
        **config["model"],
    ).to(device)
    parameters = sum(parameter.numel() for parameter in model.parameters())
    training = config["training"]
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=float(training["learning_rate"]),
        weight_decay=float(training["weight_decay"]),
    )
    batch_size = int(training["batch_size"])
    torch.cuda.reset_peak_memory_stats(device)
    started = time.perf_counter()
    loss_sum = token_count = 0.0
    model.train()
    for offset in range(0, len(schedule), batch_size):
        ids = schedule[offset:offset + batch_size]
        batch = torch.from_numpy(pool[ids]).to(device)
        inputs, targets = batch[:, :-1], batch[:, 1:]
        optimizer.zero_grad(set_to_none=True)
        logits = model(inputs)
        loss = token_loss(logits, targets, generator)
        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), float(training["gradient_clip"]))
        optimizer.step()
        relevant = targets[:, 3:] if generator == "recurrence4" else targets
        loss_sum += float(loss.detach()) * relevant.numel()
        token_count += relevant.numel()

    fresh = evaluate(model, validation, generator, batch_size, device)
    repeated = evaluate(model, repeated_subset, generator, batch_size, device)
    runtime = time.perf_counter() - started
    result = {
        "generator": generator, "condition": condition, "seed": seed,
        "parameters": parameters, "stream_examples": len(schedule),
        "optimizer_updates": math.ceil(len(schedule) / batch_size),
        "repeated_exposures": repeated_exposures if condition != "all_unique" else 0,
        "repeat_count_per_repeated_item": repetitions if condition != "all_unique" else 1,
        "fresh_nll": fresh["nll"], "fresh_accuracy": fresh["accuracy"],
        "repeated_nll": repeated["nll"],
        "memorization_gap": fresh["nll"] - repeated["nll"],
        "mean_train_nll": loss_sum / token_count,
        "runtime_seconds": runtime,
        "peak_cuda_bytes": int(torch.cuda.max_memory_allocated(device)),
    }
    run_dir = output_dir / generator / f"seed_{seed}" / condition
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result), flush=True)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    config_path = Path(args.config).resolve()
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    root = Path(__file__).resolve().parents[1]
    output_dir = root / config["output_dir"]
    output_dir.mkdir(parents=True, exist_ok=True)
    device = torch.device("cuda")
    if not torch.cuda.is_available():
        raise RuntimeError("ARC-22 requires the audited CUDA device")

    generators = config["generators"][:1] if args.smoke else config["generators"]
    seeds = config["seeds"][:1] if args.smoke else config["seeds"]
    conditions = config["conditions"][:2] if args.smoke else config["conditions"]
    results = []
    for generator in generators:
        for seed in seeds:
            for condition in conditions:
                results.append(train_one(
                    config, generator, condition, int(seed), output_dir, device
                ))
    name = "smoke_results.json" if args.smoke else "results.json"
    (output_dir / name).write_text(json.dumps(results, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
