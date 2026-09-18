# Technical failure log

## 2026-08-26 — first frozen analysis stopped at top-1 consistency gate

The first execution of `analyze_geometry.py` stopped before fitting any model
or producing a verdict. Block `D_S`, all KL values, and all NLL values reproduced
ARC-006 to floating-point precision, but activation-noise `D_S` differed by as
much as 0.019821.

The initial diagnosis was local to ARC-007: its extractor used
`torch.topk(..., 2)` while ARC-006 noise used `argmax`. The raw extraction was
therefore invalidated, the historical first seal was retained, and the
extractor was changed to preserve `argmax` as `c1`. No outcome model had run.

## 2026-08-26 — second quality gate exposed a prior assay inconsistency

All 15 checkpoints were regenerated with the `argmax` anchor and resealed.
The second execution again stopped before any model fit. Noise `D_S` now
matched ARC-006 to floating-point precision, but block `D_S` differed by as
much as 0.032335.

Code tracing established the actual cross-ARC mismatch:

- Candidate A, ARC-004, and ARC-005 define intact top-1 using
  `probs.topk(2)[..., 0]`;
- ARC-006 inherits those block-family `D_S` values;
- ARC-006 newly evaluates the noise family using `logits.argmax(-1)`.

Under exact FP16 ties, `topk` and `argmax` may choose different intact classes.
ARC-006 therefore subtracts outcomes with different top-1 anchors. KL and NLL
are unaffected, which is why earlier integrity checks passed.

This supersedes the initial local-bug interpretation. The discrepancy is a
material prior-assay error: the largest Class A cell residual correction is
0.018084, versus a frozen residual magnitude of 0.019235. Per the explicit
ARC-007 stop clause, the verdict is `PRIOR ASSAY INVALIDATION`. No
geometry-conditioned regression, layer analysis, sign-reversal model, or
normal ARC-007 verdict was produced.
