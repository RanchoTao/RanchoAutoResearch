# Confirmatory protocol freeze

Frozen and committed after damage-support-only calibration and before any
confirmatory model forward pass.

## Selected grid

- New family: token-wise norm-controlled additive activation noise.
- Betas: `0.35`, `0.50`, `0.75`; every value passing the deterministic
  calibration rule.
- Independent runs: combined seeds `2, 3, 5, 6, 8`.
- Checkpoints: `step14000`, `step72000`, `step143000`.
- Interior layers: `1-10`.
- Noise direction IDs: `101, 202, 303`.
- Evaluation selections: `11, 23, 37`; six sequences x 256 next-token
  positions; batch size 2.
- Original anchor: exact retained block-deletion cells for the same
  run/checkpoint/evaluation/layer keys.

## Frozen analysis

All endpoints, matching rules, common-support requirements, family-equivalence
bound `0.0107421875`, interaction rule, exclusions, bootstrap seed/sample count,
confidence bins, counterevidence queries, sensitivity calipers, and verdict
logic remain exactly as written in `preregistration.md`.

Pre-execution schema clarification: the retained five-run deletion anchor lacks
local activation magnitude, so the full cross-family regression excludes that
unavailable covariate rather than imputing it. Magnitude remains primary in the
within-new-family matched analyses; an available two-run ARC-004 sensitivity is
supportive only. This clarification was committed before any confirmatory
forward pass.

No pilot `S`, `D_S`, or checkpoint-direction result was inspected when this
file was frozen. The selected betas were determined only by finite status,
catastrophic count, KL/NLL support, exact matchability, and anchor-quartile
coverage.
