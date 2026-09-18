"""ARC-23 quotient-first learning in finite-group state tracking."""

from __future__ import annotations

import argparse
import itertools
import json
import math
import random
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Hashable

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import yaml


@dataclass
class FiniteGroup:
    name: str
    elements: list[Hashable]
    table: np.ndarray
    identity: int
    quotient_map: np.ndarray
    quotient_size: int

    @property
    def order(self) -> int:
        return len(self.elements)


def build_group(name: str, elements: list[Hashable],
                operation: Callable[[Hashable, Hashable], Hashable],
                identity_element: Hashable) -> FiniteGroup:
    index = {element: i for i, element in enumerate(elements)}
    table = np.empty((len(elements), len(elements)), dtype=np.int64)
    for i, left in enumerate(elements):
        for j, right in enumerate(elements):
            table[i, j] = index[operation(left, right)]
    identity = index[identity_element]
    inverses = np.empty(len(elements), dtype=np.int64)
    for i in range(len(elements)):
        valid = np.where((table[i] == identity) & (table[:, i] == identity))[0]
        if len(valid) != 1:
            raise AssertionError(f"invalid inverse in {name}")
        inverses[i] = valid[0]

    generators = {identity}
    for a in range(len(elements)):
        for b in range(len(elements)):
            commutator = table[table[table[a, b], inverses[a]], inverses[b]]
            generators.add(int(commutator))
    subgroup = set(generators)
    changed = True
    while changed:
        changed = False
        current = list(subgroup)
        for a in current:
            for b in current:
                product = int(table[a, b])
                if product not in subgroup:
                    subgroup.add(product)
                    changed = True

    quotient_map = np.full(len(elements), -1, dtype=np.int64)
    quotient_id = 0
    for g in range(len(elements)):
        if quotient_map[g] >= 0:
            continue
        coset = {int(table[g, h]) for h in subgroup}
        for member in coset:
            quotient_map[member] = quotient_id
        quotient_id += 1
    if np.any(quotient_map < 0):
        raise AssertionError("incomplete quotient")
    return FiniteGroup(name, elements, table, identity, quotient_map, quotient_id)


def cyclic(name: str, n: int) -> FiniteGroup:
    elements = list(range(n))
    return build_group(name, elements, lambda a, b: (a + b) % n, 0)


def cyclic_product(name: str, a: int, b: int) -> FiniteGroup:
    elements = [(x, y) for x in range(a) for y in range(b)]
    return build_group(
        name, elements, lambda x, y: ((x[0] + y[0]) % a, (x[1] + y[1]) % b),
        (0, 0),
    )


def dihedral(name: str, n: int) -> FiniteGroup:
    # (r, k) represents reflection^r followed by rotation^k.
    elements = [(r, k) for r in range(2) for k in range(n)]
    def operation(a: tuple[int, int], b: tuple[int, int]) -> tuple[int, int]:
        r, k = a
        s, ell = b
        return ((r + s) % 2, (k + (-1 if r else 1) * ell) % n)
    return build_group(name, elements, operation, (0, 0))


def permutation_parity(permutation: tuple[int, ...]) -> int:
    inversions = sum(
        permutation[i] > permutation[j]
        for i in range(len(permutation)) for j in range(i + 1, len(permutation))
    )
    return inversions % 2


def permutation_group(name: str, n: int, even_only: bool) -> FiniteGroup:
    elements = list(itertools.permutations(range(n)))
    if even_only:
        elements = [element for element in elements if permutation_parity(element) == 0]
    def operation(p: tuple[int, ...], q: tuple[int, ...]) -> tuple[int, ...]:
        return tuple(p[q[i]] for i in range(n))
    return build_group(name, elements, operation, tuple(range(n)))


def quaternion_times_c3() -> FiniteGroup:
    # Q8 indices: +1,+i,+j,+k,-1,-i,-j,-k.
    q_elements = [(sign, basis) for sign in (0, 1) for basis in range(4)]
    positive = {(1, 2): 3, (2, 3): 1, (3, 1): 2}
    negative = {(2, 1): 3, (3, 2): 1, (1, 3): 2}
    def qmul(a: tuple[int, int], b: tuple[int, int]) -> tuple[int, int]:
        sign = (a[0] + b[0]) % 2
        x, y = a[1], b[1]
        if x == 0:
            return sign, y
        if y == 0:
            return sign, x
        if x == y:
            return (sign + 1) % 2, 0
        if (x, y) in positive:
            return sign, positive[(x, y)]
        return (sign + 1) % 2, negative[(x, y)]
    elements = [(q, c) for q in q_elements for c in range(3)]
    def operation(a, b):
        return (qmul(a[0], b[0]), (a[1] + b[1]) % 3)
    return build_group("Q8xC3", elements, operation, ((0, 0), 0))


def all_groups() -> dict[str, FiniteGroup]:
    groups = [
        cyclic("C12", 12), cyclic_product("C6xC2", 6, 2),
        dihedral("D6", 6), permutation_group("A4", 4, True),
        cyclic("C24", 24), cyclic_product("C12xC2", 12, 2),
        quaternion_times_c3(), dihedral("D12", 12),
        permutation_group("S4", 4, False),
    ]
    return {group.name: group for group in groups}


class ProductTransformer(nn.Module):
    def __init__(self, order: int, max_depth: int, d_model: int, n_layers: int,
                 n_heads: int, d_mlp: int) -> None:
        super().__init__()
        self.token = nn.Embedding(order, d_model)
        positions = torch.arange(max_depth, dtype=torch.float32)[:, None]
        freq = torch.exp(torch.arange(0, d_model, 2) * (-math.log(10000.0) / d_model))
        pe = torch.zeros(max_depth, d_model)
        pe[:, 0::2] = torch.sin(positions * freq)
        pe[:, 1::2] = torch.cos(positions * freq)
        self.register_buffer("position", pe, persistent=False)
        layer = nn.TransformerEncoderLayer(
            d_model, n_heads, d_mlp, dropout=0.0, activation="gelu",
            batch_first=True, norm_first=True,
        )
        self.encoder = nn.TransformerEncoder(
            layer, n_layers, enable_nested_tensor=False
        )
        self.norm = nn.LayerNorm(d_model)
        self.output = nn.Linear(d_model, order)

    def forward(self, tokens: torch.Tensor) -> torch.Tensor:
        hidden = self.token(tokens) + self.position[:tokens.shape[1]]
        hidden = self.encoder(hidden)
        return self.output(self.norm(hidden[:, -1]))


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def products(tokens: torch.Tensor, table: torch.Tensor, identity: int) -> torch.Tensor:
    result = torch.full(
        (tokens.shape[0],), identity, dtype=torch.long, device=tokens.device
    )
    for position in range(tokens.shape[1]):
        result = table[result, tokens[:, position]]
    return result


@torch.no_grad()
def evaluate(model: nn.Module, group: FiniteGroup, depth: int, seed: int,
             examples: int, batch_size: int, device: torch.device) -> dict[str, float]:
    model.eval()
    rng = np.random.default_rng(90_000 + group.order * 1000 + seed * 17 + depth)
    # The random integer sequences are identical across groups of equal order.
    token_array = rng.integers(0, group.order, size=(examples, depth), dtype=np.int64)
    table = torch.as_tensor(group.table, device=device)
    quotient_map = torch.as_tensor(group.quotient_map, device=device)
    exact_correct = quotient_correct = total = 0
    nll_sum = 0.0
    for offset in range(0, examples, batch_size):
        tokens = torch.from_numpy(token_array[offset:offset + batch_size]).to(device)
        targets = products(tokens, table, group.identity)
        logits = model(tokens)
        nll_sum += float(F.cross_entropy(logits, targets, reduction="sum"))
        exact_correct += int((logits.argmax(-1) == targets).sum())
        probabilities = logits.softmax(-1)
        qprob = torch.zeros(
            len(tokens), group.quotient_size, device=device, dtype=probabilities.dtype
        )
        qprob.scatter_add_(1, quotient_map[None, :].expand(len(tokens), -1), probabilities)
        quotient_correct += int((qprob.argmax(-1) == quotient_map[targets]).sum())
        total += len(tokens)
    return {
        "exact_accuracy": exact_correct / total,
        "quotient_accuracy": quotient_correct / total,
        "nll": nll_sum / total,
    }


def train_one(config: dict, group: FiniteGroup, seed: int,
              output_dir: Path, device: torch.device) -> dict:
    seed_everything(seed + group.order * 100)
    model = ProductTransformer(
        order=group.order, max_depth=max(config["eval_depths"]), **config["model"]
    ).to(device)
    training = config["training"]
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=float(training["learning_rate"]),
        weight_decay=float(training["weight_decay"]),
    )
    table = torch.as_tensor(group.table, device=device)
    rng = np.random.default_rng(30_000 + group.order * 1000 + seed)
    batch_size = int(training["batch_size"])
    checkpoints = []
    torch.cuda.reset_peak_memory_stats(device)
    started = time.perf_counter()
    for step in range(1, int(training["steps"]) + 1):
        depth = int(rng.choice(config["train_depths"]))
        token_array = rng.integers(
            0, group.order, size=(batch_size, depth), dtype=np.int64
        )
        tokens = torch.from_numpy(token_array).to(device)
        targets = products(tokens, table, group.identity)
        model.train()
        optimizer.zero_grad(set_to_none=True)
        loss = F.cross_entropy(model(tokens), targets)
        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        if step % int(training["eval_every"]) == 0:
            metric = evaluate(
                model, group, 4, seed, int(training["eval_examples"]),
                batch_size, device,
            )
            checkpoints.append({"step": step, **metric})

    evaluations = {
        str(depth): evaluate(
            model, group, int(depth), seed, int(training["eval_examples"]),
            batch_size, device,
        ) for depth in config["eval_depths"]
    }
    gaps = [row["quotient_accuracy"] - row["exact_accuracy"] for row in checkpoints]
    result = {
        "group": group.name, "order": group.order,
        "quotient_size": group.quotient_size,
        "compression_ratio": group.order / group.quotient_size,
        "seed": seed,
        "parameters": sum(p.numel() for p in model.parameters()),
        "checkpoints": checkpoints,
        "quotient_gap_auc": float(np.mean(gaps)),
        "evaluations": evaluations,
        "id_exact_accuracy": evaluations["4"]["exact_accuracy"],
        "ood_exact_accuracy": float(np.mean([
            evaluations["8"]["exact_accuracy"], evaluations["12"]["exact_accuracy"]
        ])),
        "runtime_seconds": time.perf_counter() - started,
        "peak_cuda_bytes": int(torch.cuda.max_memory_allocated(device)),
    }
    run_dir = output_dir / group.name / f"seed_{seed}"
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "checkpoints"}), flush=True)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    config_path = Path(args.config).resolve()
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    groups = all_groups()
    selected_groups = config["groups"][:1] if args.smoke else config["groups"]
    seeds = config["seeds"][:1] if args.smoke else config["seeds"]
    if args.smoke:
        config["training"]["steps"] = 10
        config["training"]["eval_every"] = 10
        config["training"]["eval_examples"] = 256
    output_dir = Path(__file__).resolve().parents[1] / config["output_dir"]
    output_dir.mkdir(parents=True, exist_ok=True)
    device = torch.device("cuda")
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA unavailable")
    results = []
    for name in selected_groups:
        group = groups[name]
        for seed in seeds:
            results.append(train_one(config, group, int(seed), output_dir, device))
    filename = "smoke_results.json" if args.smoke else "results.json"
    (output_dir / filename).write_text(json.dumps(results, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
