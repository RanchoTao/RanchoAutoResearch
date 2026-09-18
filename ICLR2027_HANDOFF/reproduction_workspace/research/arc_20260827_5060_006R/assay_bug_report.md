# Assay bug report

ARC-006 inherited block-family `D_S` from an assay using
`probs.topk(2)[..., 0]`, while its newly evaluated noise-family `D_S` used
`logits.argmax(-1)`. Exact FP16 ties can resolve to different token indices,
making the frozen cross-family residual an inconsistent outcome contrast.

ARC-007 detected the issue at its preregistered reproduction gate before any
geometry model was fitted. The maximum observed single-cell correction was
0.0180845, comparable with the invalid aggregate residual magnitude 0.0192347.

ARC-006R changes only the intact top-1 identity convention. It does not change
targeting, KL/NLL, matching, seeds, checkpoints, layers, corpus, intervention
strength, equivalence bounds, exclusions, or statistical protocol.
