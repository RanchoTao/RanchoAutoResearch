# Harness validation

Smoke-tested before the multi-run sweep on `EleutherAI/pythia-70m-seed1` at
steps 14,000 and 143,000.

- Hugging Face revision refs resolve to distinct immutable commits.
- Loaded parameter count: 70,426,624; six GPT-NeoX blocks.
- Preregistered candidate blocks: 1, 2, 3, 4 (first/last excluded).
- Intact evaluation is restored before every deletion series.
- Three fixed evaluation resamples each contain 1,536 next-token positions.
- Intact and deleted logits were finite; NLL, KL, agreement, confidence and
  per-layer/per-bin records were produced for every intervention.
- Peak allocated CUDA memory was 0.81 GiB.
- Intact NLL was 4.328 at step14k and 4.193 at step143k, so both endpoints pass
  the frozen competence gate.

Smoke-test deletion agreement was 0.445 at step14k and 0.302 at step143k. This
value was inspected only after the protocol and promotion gates were frozen and
is not treated as independent-run stability evidence by itself.

