# ARC-20260827-5060-007R

Decision-boundary geometry analysis of the corrected ARC-006R
intervention-family residual.

## Status

Complete. Final verdict: `GEOMETRY-PARTIAL`.

The corrected baseline reproduced to `3.47e-17`. Boundary displacement alone
did not shrink the family residual. The full non-tautological output-geometry
block shrank it by 20.18%, but the adjusted estimate remained outside the
frozen equivalence region. Geometry did not explain reversal labels or layer
heterogeneity, and the outcome-blind 31-cell geometry-matched subset retained
an even larger negative residual.

## Integrity

- Preregistration commit: `e838a71740eefb74bb4d69dcb90aa0781ef6613d`.
- Mechanical dtype repair commit: `967370465eb4d80e43311ac1a4459e1f7539cc16`.
- Presentation-only figure repair commit:
  `ade79a135de6bce82482642336d7796c0d39c93c`.
- Execution: Level 1 local CPU analysis; no new inference, network retrieval,
  model/data download, package change, API, or external compute.

Start with `EXECUTIVE_SUMMARY.md`; exact machine-readable results are in
`results/geometry_summary.json`.
