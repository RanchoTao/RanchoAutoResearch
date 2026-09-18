from __future__ import annotations

import argparse
import csv
import json
import math
import random
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
import yaml
from torch import nn
from torch.utils.data import DataLoader, TensorDataset


def seed_all(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def apply_function(index: np.ndarray, function: np.ndarray) -> np.ndarray:
    result = np.empty_like(index)
    masks = [function == i for i in range(8)]
    result[masks[0]] = (index[masks[0]] + 1) % 32
    result[masks[1]] = (index[masks[1]] + 3) % 32
    result[masks[2]] = index[masks[2]] ^ 1
    result[masks[3]] = index[masks[3]] ^ 7
    value = index[masks[4]]
    result[masks[4]] = ((value << 1) & 31) | (value >> 4)
    value = index[masks[5]]
    result[masks[5]] = (value >> 1) | ((value & 1) << 4)
    result[masks[6]] = (3 * index[masks[6]] + 1) % 32
    result[masks[7]] = (5 * index[masks[7]] + 7) % 32
    return result


@dataclass(frozen=True)
class TaskSpec:
    max_depth: int = 8
    states: int = 32
    functions: int = 8

    @property
    def pad_token(self) -> int:
        return self.states + self.functions

    @property
    def vocab_size(self) -> int:
        return self.pad_token + 1


def generate_examples(n: int, depths: list[int], seed: int, spec: TaskSpec) -> TensorDataset:
    rng = np.random.default_rng(seed)
    depth = np.asarray([depths[i % len(depths)] for i in range(n)], dtype=np.int64)
    rng.shuffle(depth)
    initial = rng.integers(0, spec.states, size=n, dtype=np.int64)
    functions = rng.integers(0, spec.functions, size=(n, spec.max_depth), dtype=np.int64)
    tokens = np.full((n, spec.max_depth + 1), spec.pad_token, dtype=np.int64)
    tokens[:, 0] = initial
    trajectory = np.full((n, spec.max_depth), -100, dtype=np.int64)
    state = initial.copy()
    for step in range(spec.max_depth):
        active = depth > step
        tokens[active, step + 1] = spec.states + functions[active, step]
        next_state = apply_function(state[active], functions[active, step])
        state[active] = next_state
        trajectory[active, step] = next_state
    sample_id = np.arange(n, dtype=np.int64)
    return TensorDataset(torch.from_numpy(tokens), torch.from_numpy(depth),
                         torch.from_numpy(trajectory), torch.from_numpy(sample_id))


class SinusoidalPosition(nn.Module):
    def __init__(self, length: int, d_model: int):
        super().__init__()
        position = torch.arange(length, dtype=torch.float32)[:, None]
        div = torch.exp(torch.arange(0, d_model, 2, dtype=torch.float32)
                        * (-math.log(10000.0) / d_model))
        encoding = torch.zeros(length, d_model)
        encoding[:, 0::2] = torch.sin(position * div)
        encoding[:, 1::2] = torch.cos(position * div)
        self.register_buffer("encoding", encoding, persistent=False)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x + self.encoding[:x.shape[1]]


class TinyProcessTransformer(nn.Module):
    def __init__(self, spec: TaskSpec, d_model: int, n_layers: int,
                 n_heads: int, d_mlp: int):
        super().__init__()
        self.spec = spec
        self.embedding = nn.Embedding(spec.vocab_size, d_model, padding_idx=spec.pad_token)
        self.position = SinusoidalPosition(spec.max_depth + 1, d_model)
        layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=n_heads, dim_feedforward=d_mlp,
            dropout=0.0, activation="gelu", batch_first=True, norm_first=True,
        )
        self.encoder = nn.TransformerEncoder(layer, num_layers=n_layers,
                                             norm=nn.LayerNorm(d_model))
        self.head = nn.Linear(d_model, spec.states)

    def forward(self, tokens: torch.Tensor) -> torch.Tensor:
        x = self.position(self.embedding(tokens))
        length = tokens.shape[1]
        causal = torch.triu(torch.ones(length, length, dtype=torch.bool,
                                       device=tokens.device), diagonal=1)
        padding = tokens == self.spec.pad_token
        hidden = self.encoder(x, mask=causal, src_key_padding_mask=padding)
        return self.head(hidden[:, 1:])


def selected_positions(condition: str, depth: torch.Tensor,
                       sample_id: torch.Tensor, seed: int) -> torch.Tensor:
    max_intermediate = depth - 1
    if condition == "early_1":
        return torch.ones_like(depth)
    if condition == "late_1":
        return max_intermediate
    if condition == "midpoint_1":
        return (depth // 2).clamp(min=1)
    if condition == "uniform_1":
        return 1 + torch.remainder(sample_id, max_intermediate)
    if condition == "random_1":
        # Deterministic integer hash gives one uniform valid position per sample
        # while keeping exactly the same selection across reruns.
        hashed = sample_id * 1103515245 + seed * 12345 + 1013904223
        return 1 + torch.remainder(hashed.abs(), max_intermediate)
    raise ValueError(condition)


def compute_loss(logits: torch.Tensor, depth: torch.Tensor,
                 trajectory: torch.Tensor, sample_id: torch.Tensor,
                 condition: str, seed: int, auxiliary_weight: float) -> tuple[torch.Tensor, dict]:
    batch_index = torch.arange(len(depth), device=depth.device)
    final_index = depth - 1
    final_logits = logits[batch_index, final_index]
    final_labels = trajectory[batch_index, final_index]
    answer_loss = F.cross_entropy(final_logits, final_labels)
    if condition == "outcome_only":
        return answer_loss, {"answer": float(answer_loss.detach()), "aux": 0.0}
    if condition == "full_process":
        positions = torch.arange(logits.shape[1], device=depth.device)[None, :]
        mask = positions < (depth - 1)[:, None]
        auxiliary = F.cross_entropy(logits[mask], trajectory[mask])
    else:
        selected = selected_positions(condition, depth, sample_id, seed) - 1
        auxiliary = F.cross_entropy(logits[batch_index, selected],
                                    trajectory[batch_index, selected])
    total = answer_loss + auxiliary_weight * auxiliary
    return total, {"answer": float(answer_loss.detach()), "aux": float(auxiliary.detach())}


@torch.no_grad()
def evaluate(model: TinyProcessTransformer, datasets: dict[int, TensorDataset],
             batch_size: int, device: torch.device) -> dict[int, float]:
    model.eval()
    output = {}
    for depth_value, dataset in datasets.items():
        correct = total = 0
        for tokens, depth, trajectory, _ in DataLoader(dataset, batch_size=batch_size):
            tokens, depth, trajectory = tokens.to(device), depth.to(device), trajectory.to(device)
            logits = model(tokens)
            index = torch.arange(len(depth), device=device)
            prediction = logits[index, depth - 1].argmax(-1)
            labels = trajectory[index, depth - 1]
            correct += int((prediction == labels).sum())
            total += len(depth)
        output[depth_value] = correct / total
    return output


def train_condition(condition: str, seed: int, config: dict, spec: TaskSpec,
                    eval_sets: dict[int, TensorDataset], device: torch.device,
                    output_dir: Path) -> dict:
    seed_all(seed)
    model_cfg = config["model"]
    model = TinyProcessTransformer(
        spec, int(model_cfg["d_model"]), int(model_cfg["n_layers"]),
        int(model_cfg["n_heads"]), int(model_cfg["d_mlp"]),
    ).to(device)
    training = config["training"]
    optimizer = torch.optim.AdamW(model.parameters(), lr=float(training["learning_rate"]),
                                  weight_decay=float(training["weight_decay"]))
    epochs = int(training["epochs"])
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
    history = []
    started = time.perf_counter()
    for epoch in range(1, epochs + 1):
        train_set = generate_examples(
            int(config["task"]["train_examples_per_epoch"]),
            [int(x) for x in config["task"]["train_depths"]],
            seed + 1000 + epoch, spec,
        )
        generator = torch.Generator().manual_seed(seed + 2000 + epoch)
        loader = DataLoader(train_set, batch_size=int(training["batch_size"]),
                            shuffle=True, generator=generator, pin_memory=True)
        model.train()
        loss_sum = answer_sum = aux_sum = 0.0
        seen = 0
        for tokens, depth, trajectory, sample_id in loader:
            tokens = tokens.to(device, non_blocking=True)
            depth = depth.to(device, non_blocking=True)
            trajectory = trajectory.to(device, non_blocking=True)
            sample_id = sample_id.to(device, non_blocking=True)
            optimizer.zero_grad(set_to_none=True)
            with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
                logits = model(tokens)
                loss, parts = compute_loss(logits, depth, trajectory, sample_id,
                                           condition, seed, float(training["auxiliary_weight"]))
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            count = len(depth)
            loss_sum += float(loss.detach()) * count
            answer_sum += parts["answer"] * count
            aux_sum += parts["aux"] * count
            seen += count
        scheduler.step()
        row = {"epoch": epoch, "loss": loss_sum / seen,
               "answer_loss": answer_sum / seen, "aux_loss": aux_sum / seen}
        history.append(row)
        if epoch in {1, 5, 10, 15, epochs}:
            print(json.dumps({"condition": condition, **row}), flush=True)
    accuracy = evaluate(model, eval_sets, int(training["batch_size"]), device)
    runtime = time.perf_counter() - started
    condition_dir = output_dir / f"seed_{seed}" / condition
    condition_dir.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), condition_dir / "model.pt")
    with (condition_dir / "history.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(history[0]))
        writer.writeheader(); writer.writerows(history)
    result = {
        "condition": condition, "seed": seed,
        "parameters": sum(p.numel() for p in model.parameters()),
        "accuracy_by_depth": {str(k): v for k, v in accuracy.items()},
        "id_accuracy": float(np.mean([accuracy[d] for d in (2, 3, 4)])),
        "ood_accuracy": float(np.mean([accuracy[d] for d in (5, 6, 7, 8)])),
        "runtime_seconds": runtime,
        "peak_cuda_bytes": int(torch.cuda.max_memory_allocated()),
    }
    (condition_dir / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result), flush=True)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    config_path = args.config.resolve()
    root = config_path.parent.parent
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA device required by audited ARC-21 configuration")
    device = torch.device("cuda")
    torch.backends.cuda.matmul.allow_tf32 = True
    spec = TaskSpec(max_depth=max(config["task"]["eval_depths"]),
                    states=int(config["task"]["states"]),
                    functions=int(config["task"]["functions"]))
    output_dir = root / config["output_dir"]
    output_dir.mkdir(parents=True, exist_ok=True)
    all_results = []
    for seed in config["seeds"]:
        eval_sets = {
            int(depth): generate_examples(
                int(config["task"]["validation_examples_per_depth"]), [int(depth)],
                int(seed) + 3000 + int(depth), spec,
            ) for depth in config["task"]["eval_depths"]
        }
        for condition in config["conditions"]:
            torch.cuda.reset_peak_memory_stats()
            all_results.append(train_condition(
                condition, int(seed), config, spec, eval_sets, device, output_dir
            ))
    (output_dir / "results.json").write_text(json.dumps(all_results, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
