# ARC-009 feasibility report

## Question

Can continuous/high-resolution alpha calibration make the frozen internal
direction counterfactual broadly identifiable without accessing `D_S`?

## Result

- PASS-A: **47/103**.
- PASS-B (descriptive): **29/103**.
- ARC-008 strict support: 15/103.
- Absolute support gain: **+32 cells**.
- Relative support increase: **213.3%**.
- Coverage gate: **PASS**.
- Numerical-failure rate: 0.0%.
- Boundary selections: 0/103.

Median diagnostic values were: target log-error 0.0277,
block/noise KL imbalance 1.6%, NLL imbalance
1.0%, hidden-norm ratio
1.184, output-norm ratio
1.070, and alignment difference
0.0003.

Per-caliper strict pass counts were KL 97/103, NLL 100/103, hidden norm
65/103, output norm 91/103, and output alignment 103/103. Relative to ARC-008,
continuous alpha repaired most damage-balance failures (30 -> 97 KL; 31 ->
100 NLL), but hidden-norm balance fell from 90 to 65. This opposing movement
is the central identification tradeoff.

## Interpretation

Continuous alpha did not identify broad causal support under the current assay; terminate this internal-direction branch.

This is only an identification-feasibility result. It is not evidence that
direction changes `D_S`, and no causal effect was estimated.

The below-60 decision cannot be rescued by adding the 29 PASS-B cells: the
preregistration explicitly states that PASS-A+B does not replace the primary
gate. No caliper was changed after results.

## Final verdict

**ALPHA-NOT-FEASIBLE**
