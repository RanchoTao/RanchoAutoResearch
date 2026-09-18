# Next ARC recommendation

Recommend exactly one focused ARC:

## ARC-006 — Per-cell inverse damage targeting

Prospectively choose activation-noise strength independently for each frozen
run/checkpoint/layer by root-finding on KL and NLL only, while keeping D_S
blinded during calibration. Target the exact retained block-deletion damage
cells, then reveal D_S once a preregistered coverage and balance gate is met.

This experiment directly addresses ARC-005's largest uncertainty: coarse beta
support yielded only 26/150 valid matches. It should require no new model family,
scale, corpus, or paid compute. Predefine a minimum of 100/150 exact targets,
run-level equivalence testing, monotone root-finding failure rules, and a holdout
set of target cells. If adequate exact targeting still produces a stable family
residual, H_partial is strengthened; if the residual collapses, ARC-005's family
effect was primarily a support/matching artifact.

Do not run a larger model before this identification test.
