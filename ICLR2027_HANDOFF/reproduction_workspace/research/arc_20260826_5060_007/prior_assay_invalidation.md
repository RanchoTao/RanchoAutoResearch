# PRIOR ASSAY INVALIDATION

## Decision

ARC-007 terminated at the frozen data-quality gate. The ARC-006 family residual
compares block and activation-noise outcomes defined with different intact
top-1 tie-breaking rules. This violates the shared-outcome contract and is
material at the scale of the reported effect.

This is not a `GEOMETRY-GO`, `GEOMETRY-PARTIAL`, `GEOMETRY-NO`, or
`GEOMETRY-NONIDENTIFIABLE` result. Those verdicts require a valid frozen
ARC-006 baseline, and no geometry-conditioned outcome was inspected.

## Root cause

The block-family path inherited from the Candidate A assay uses:

```python
top_values, top_indices = probs.topk(2, dim=-1)
top1 = top_indices[..., 0]
```

The ARC-006 noise reveal uses:

```python
intact_top1 = logits.argmax(-1)
```

With exactly tied FP16 logits, these operations need not select the same class.
ARC-006 then computes `D_S(noise)-D_S(block)` from two different intact-class
anchors. The affected source locations are recorded in
`provenance_and_commands.md`.

## Materiality

The frozen ARC-006 estimate was -0.0192347 with a run-bootstrap 95% interval
[-0.0232060, -0.0137153]. Recomputing the same 103 Class A cells under a single
tie rule gives:

| Definition | Residual | 95% run-bootstrap CI | Negative runs | Equivalence |
|---|---:|---:|---:|---|
| ARC-006 mixed | -0.0192347 | [-0.0232060, -0.0137153] | 5/5 | no |
| consistent `topk` | -0.0167969 | [-0.0207827, -0.0123626] | 5/5 | no |
| consistent `argmax` | -0.0168330 | [-0.0200448, -0.0126157] | 5/5 | no |

The consistent-`topk` estimate is 12.67% smaller in magnitude than the frozen
mixed estimate. More importantly, the largest cellwise residual correction is
0.0180845, nearly the entire frozen aggregate effect. The pathwise maximum
discrepancies are:

| Recomputed rule | Block vs ARC-006 | Noise vs ARC-006 |
|---|---:|---:|
| `topk` | 1.1e-16 | 0.0198206 |
| `argmax` | 0.0323351 | 1.4e-16 |

Thus the qualitative direction appears robust in this minimal diagnostic, but
the exact frozen estimate, cell residuals, sign-reversal membership, layer
heterogeneity, and HIGH-confidence ARC-006 claim are not valid inputs to
ARC-007 until formally repaired.

## What was and was not executed

- The ARC-007 preregistration was committed before extraction.
- All 150 cells, five runs, and 15 checkpoints were extracted twice: once with
  the historical `topk` path and once with the intended `argmax` path.
- Both frozen analysis attempts stopped at the `D_S` reproduction check.
- No geometry-conditioned regression, geometry residual reveal, layer model,
  sign-reversal classifier, or seven-figure confirmatory package was executed.
- The only post-stop analysis was the smallest diagnostic needed to establish
  root cause and materiality. It is explicitly not an ARC-007 hypothesis test.

## Strongest surviving evidence

Both internally consistent definitions retain a negative mean of run medians,
5/5 negative runs, and intervals outside the frozen equivalence band. This is
evidence that Candidate A may survive a corrected assay.

## Strongest counterevidence

The outcome-definition correction is cell-dependent and can be as large as the
effect being explained. ARC-006's exact residual structure cannot be treated as
frozen evidence even though the coarse direction survives this diagnostic.

## Required repair

Run exactly one repair ARC: `ARC-006R — deterministic top-1 assay repair and
reseal`. Pre-register one canonical top-1 rule for both families, recompute all
150 outcomes from the same logits and tokens, rerun the unchanged ARC-006
matching/statistical contract, and use the alternative tie rule only as a
sensitivity analysis. Resume ARC-007 only if the corrected family residual and
its key heterogeneity claims survive.
