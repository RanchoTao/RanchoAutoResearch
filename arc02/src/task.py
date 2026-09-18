from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import torch
from torch.utils.data import TensorDataset


PAD = 0
CLS = 1
DEPTH_BASE = 2  # tokens 2..6 encode depth 1..5
START = 7
EDGE = 8
ENTITY_BASE = 9


@dataclass(frozen=True)
class TaskSpec:
    entities: int = 16
    edges: int = 7
    max_depth: int = 5

    @property
    def vocab_size(self) -> int:
        # Atomic entity tokens followed by one token for every directed edge.
        return ENTITY_BASE + self.entities + self.entities * self.entities

    @property
    def sequence_length(self) -> int:
        return 3 + self.edges


def _encode_graph(chain: np.ndarray, distractor: tuple[int, int], depth: int,
                  start_pos: int, edge_order: np.ndarray, spec: TaskSpec) -> tuple[np.ndarray, int]:
    edges = [(int(chain[i]), int(chain[i + 1])) for i in range(6)] + [distractor]
    ordered = [edges[int(i)] for i in edge_order]
    pair_base = ENTITY_BASE + spec.entities
    tokens = [CLS, DEPTH_BASE + depth - 1, ENTITY_BASE + int(chain[start_pos])]
    for source, target in ordered:
        # Concatenated edge tokens follow the controlled symbolic setup used by
        # Brinkmann et al.; each graph edge occupies exactly one token position.
        tokens.append(pair_base + source * spec.entities + target)
    label = int(chain[start_pos + depth])
    return np.asarray(tokens, dtype=np.int64), label


def generate_dataset(n: int, depths: list[int], seed: int, spec: TaskSpec,
                     fixed_start: int | None = None) -> TensorDataset:
    """Generate balanced fixed-length relation-chain examples.

    Each graph contains a 7-node directed chain (6 edges) and one disconnected
    distractor edge. The query starts at chain position 0 or 1. All depths use
    the same vocabulary, sequence length, edge count, and distractor count.
    """
    rng = np.random.default_rng(seed)
    xs = np.empty((n, spec.sequence_length), dtype=np.int64)
    ys = np.empty(n, dtype=np.int64)
    ds = np.empty(n, dtype=np.int64)
    for i in range(n):
        depth = int(depths[i % len(depths)])
        perm = rng.permutation(spec.entities)
        chain = perm[:7]
        distractor = (int(perm[7]), int(perm[8]))
        edge_order = rng.permutation(spec.edges)
        start_pos = int(fixed_start if fixed_start is not None else rng.integers(0, 2))
        xs[i], ys[i] = _encode_graph(chain, distractor, depth, start_pos, edge_order, spec)
        ds[i] = depth
    shuffle = rng.permutation(n)
    return TensorDataset(
        torch.from_numpy(xs[shuffle]),
        torch.from_numpy(ys[shuffle]),
        torch.from_numpy(ds[shuffle]),
    )


def generate_paired_dataset(n_per_depth: int, depths: list[int], seed: int,
                            spec: TaskSpec) -> dict[int, dict[str, torch.Tensor]]:
    """Create clean/corrupt pairs sharing exactly the same graph.

    Clean starts at chain position 0 and corrupt at position 1. Hence only the
    query entity token and answer change; graph tokens are byte-identical.
    """
    rng = np.random.default_rng(seed)
    result: dict[int, dict[str, torch.Tensor]] = {}
    for depth in depths:
        clean_x, corrupt_x = [], []
        clean_y, corrupt_y = [], []
        for _ in range(n_per_depth):
            perm = rng.permutation(spec.entities)
            chain = perm[:7]
            distractor = (int(perm[7]), int(perm[8]))
            edge_order = rng.permutation(spec.edges)
            x0, y0 = _encode_graph(chain, distractor, depth, 0, edge_order, spec)
            x1, y1 = _encode_graph(chain, distractor, depth, 1, edge_order, spec)
            clean_x.append(x0)
            corrupt_x.append(x1)
            clean_y.append(y0)
            corrupt_y.append(y1)
        result[depth] = {
            "clean_x": torch.from_numpy(np.stack(clean_x)),
            "corrupt_x": torch.from_numpy(np.stack(corrupt_x)),
            "clean_y": torch.tensor(clean_y, dtype=torch.long),
            "corrupt_y": torch.tensor(corrupt_y, dtype=torch.long),
        }
    return result
