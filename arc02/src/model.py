from __future__ import annotations

import math
from dataclasses import dataclass

import torch
from torch import nn


Component = tuple[int, str, int]


class IndependentHead(nn.Module):
    def __init__(self, d_model: int, d_head: int):
        super().__init__()
        self.q = nn.Linear(d_model, d_head, bias=False)
        self.k = nn.Linear(d_model, d_head, bias=False)
        self.v = nn.Linear(d_model, d_head, bias=False)
        self.o = nn.Linear(d_head, d_model, bias=False)
        self.scale = d_head ** -0.5

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        scores = self.q(x) @ self.k(x).transpose(-2, -1) * self.scale
        probs = scores.softmax(dim=-1)
        return self.o(probs @ self.v(x))


class IntervenableBlock(nn.Module):
    def __init__(self, d_model: int, n_heads: int, d_mlp: int, layer: int):
        super().__init__()
        assert d_model % n_heads == 0
        self.layer = layer
        self.ln1 = nn.LayerNorm(d_model)
        self.heads = nn.ModuleList(
            [IndependentHead(d_model, d_model // n_heads) for _ in range(n_heads)]
        )
        self.ln2 = nn.LayerNorm(d_model)
        self.mlp = nn.Sequential(
            nn.Linear(d_model, d_mlp), nn.GELU(), nn.Linear(d_mlp, d_model)
        )

    def forward(self, x: torch.Tensor, scales: torch.Tensor,
                patch: dict[Component, torch.Tensor] | None,
                cache: dict[Component, torch.Tensor] | None) -> torch.Tensor:
        normalized = self.ln1(x)
        attention_sum = torch.zeros_like(x)
        for head_index, head in enumerate(self.heads):
            key = (self.layer, "head", head_index)
            value = head(normalized)
            if patch is not None and key in patch:
                value = patch[key]
            if cache is not None:
                cache[key] = value.detach()
            attention_sum = attention_sum + value * scales[self.layer, head_index]
        x = x + attention_sum
        key = (self.layer, "mlp", 0)
        value = self.mlp(self.ln2(x))
        if patch is not None and key in patch:
            value = patch[key]
        if cache is not None:
            cache[key] = value.detach()
        return x + value * scales[self.layer, -1]


@dataclass(frozen=True)
class ModelSpec:
    vocab_size: int
    max_seq_len: int
    n_entities: int
    d_model: int
    n_layers: int
    n_heads: int
    d_mlp: int


class TinyReasoner(nn.Module):
    def __init__(self, spec: ModelSpec):
        super().__init__()
        self.spec = spec
        self.token_embed = nn.Embedding(spec.vocab_size, spec.d_model)
        self.position_embed = nn.Parameter(torch.empty(spec.max_seq_len, spec.d_model))
        self.blocks = nn.ModuleList([
            IntervenableBlock(spec.d_model, spec.n_heads, spec.d_mlp, layer)
            for layer in range(spec.n_layers)
        ])
        self.final_ln = nn.LayerNorm(spec.d_model)
        self.unembed = nn.Linear(spec.d_model, spec.n_entities)
        nn.init.normal_(self.position_embed, std=0.02)

    @property
    def components(self) -> list[Component]:
        keys: list[Component] = []
        for layer in range(self.spec.n_layers):
            keys.extend((layer, "head", h) for h in range(self.spec.n_heads))
            keys.append((layer, "mlp", 0))
        return keys

    def default_scales(self, device: torch.device) -> torch.Tensor:
        return torch.ones(
            self.spec.n_layers, self.spec.n_heads + 1, device=device
        )

    def scales_for(self, enabled: set[Component] | None = None,
                   disabled: set[Component] | None = None) -> torch.Tensor:
        device = next(self.parameters()).device
        scales = self.default_scales(device)
        if enabled is not None:
            scales.zero_()
            for layer, kind, index in enabled:
                scales[layer, index if kind == "head" else -1] = 1.0
        if disabled is not None:
            for layer, kind, index in disabled:
                scales[layer, index if kind == "head" else -1] = 0.0
        return scales

    def forward(self, tokens: torch.Tensor, scales: torch.Tensor | None = None,
                patch: dict[Component, torch.Tensor] | None = None,
                return_cache: bool = False,
                return_representations: bool = False):
        if scales is None:
            scales = self.default_scales(tokens.device)
        x = self.token_embed(tokens) + self.position_embed[: tokens.shape[1]]
        cache: dict[Component, torch.Tensor] | None = {} if return_cache else None
        representations: list[torch.Tensor] = [x[:, 0].detach()] if return_representations else []
        for block in self.blocks:
            x = block(x, scales, patch, cache)
            if return_representations:
                representations.append(x[:, 0].detach())
        logits = self.unembed(self.final_ln(x[:, 0]))
        if return_cache or return_representations:
            return logits, cache, representations
        return logits

