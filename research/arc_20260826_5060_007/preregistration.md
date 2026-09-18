# ARC-20260826-5060-007 preregistration

Frozen before generating or inspecting any ARC-007 geometry-conditioned
outcome. ARC-006 remains immutable evidence.

## Frozen source assay

- Source commit: `21d361a24c6bb391e29be87b834b39e6b6235fc9`.
- ARC-006 target-manifest SHA-256:
  `19DF473393F82DC2E2D1E531B6F8DF7C9DBF10590C74DE0CE9FFE39DF003DCD0`.
- Primary cells: the unchanged 103 ARC-006 Class A keys. A+B (134 cells) is
  sensitivity only. No geometry-based rematching changes primary membership.
- Runs: combined seeds 2, 3, 5, 6, and 8.
- Checkpoints: steps 14k, 72k, and 143k.
- Layers: every interior layer 1 through 10.
- Corpus/tokens: the same cached WikiText-2 text, evaluation seeds 11, 23, 37,
  six sequences of 256 next-token positions per seed.
- Block family: delete exactly one target block from the executed module list.
- Noise family: frozen norm-controlled additive activation noise at each
  ARC-006 sealed `beta`, using directions 101, 202, and 303.
- `S`: intact/intervened token-level top-1 agreement. `D_S=1-S`.
- Cell residual: `D_S(noise)-D_S(block)` at the same run/checkpoint/layer.
- KL: token-mean `KL(p_intact || p_intervened)`.
- NLL damage: intervened minus intact next-token NLL.
- Frozen ARC-006 residual: `-0.019234664351851838`, computed as the mean of
  five run-median Class A cell residuals.
- Frozen equivalence bound: `+/-0.0107421875`.

The prior final-integrity manifest was verified with zero failures before this
contract was written. A material mismatch against frozen `D_S`, KL, NLL,
target keys, intervention code, or token selections stops as
`PRIOR ASSAY INVALIDATION`.

## Hypotheses

- **H_geometry:** boundary geometry substantially explains the family
  residual. The primary adjusted family coefficient shrinks by at least 50%,
  enters equivalence with its 90% cluster-bootstrap interval, and at least four
  of five run-specific coefficients move toward zero.
- **H_family_independent:** the primary adjusted residual shrinks by less than
  20% and remains materially outside equivalence.
- **H_partial_geometry:** shrinkage is at least 20% but the complete H_geometry
  gate is not met.
- **H_layer_geometry:** adding boundary geometry reduces the weighted standard
  deviation of layer-specific family effects by at least 25%.
- **H_nonidentifiable:** the frozen geometry extraction fails, the primary
  model is rank deficient, its condition number exceeds 250, a primary VIF
  exceeds 25, or run-cluster uncertainty cannot be computed.

No hypothesis is preferred.

## Metric freeze

Primary geometry variables are:

1. intact logit margin `m=z_c1-z_c2` for the intact top-1 and runner-up;
2. intact-class-anchored margin displacement
   `delta_m=(z'_c1-z'_c2)-(z_c1-z_c2)`;
3. boundary-normal projection `delta_b=delta_z_c1-delta_z_c2`;
4. top-1 flip, retained, top-1-to-intact-top-2, and other-flip rates.

Under intact-class anchoring, `delta_m` and `delta_b` are algebraically
identical. Both are computed as an implementation identity check, but only
`delta_b` enters a design matrix. Total top-1 flip rate is exactly `D_S`; it is
reported as a complementary boundary-crossing outcome and never used as an
independent explanatory predictor of `D_S`.

Secondary variables are the logit-perturbation L2 norm, signed cosine alignment
with the unit top-1-vs-runner-up axis, absolute cosine/projection fraction, and
top-1-to-intact-top-2 rate. Entropy and token ranks are not added, preventing
metric fishing and avoiding another coarse probability-distribution summary.

Metrics are aggregated over exactly the frozen evaluation tokens. Noise-family
statistics average the three frozen directions; block statistics use one
deterministic deletion evaluation. Per-example arrays are retained in
compressed NPZ files.

## Geometry prerequisite

For each cell, compare noise minus block geometry. A variable differs
systematically when the run-median paired difference has a 95% run-bootstrap
interval excluding zero and at least four of five runs share the aggregate
sign. Failure of every non-tautological primary/secondary geometry variable to
meet this condition weakens H_geometry but does not stop the frozen analysis.

## Frozen model sequence

The observational unit is a family observation nested within a frozen cell;
the scientific replicate is the independent pretraining run. Continuous
predictors are standardized over the 206 Class A family observations. Because
the frozen data already show `corr(KL,NLL)=0.997675`, the primary damage term
faithfully reuses ARC-006's equal-weight standardized composite
`f_damage=(z(KL)+z(NLL))/2`; estimating separate KL and NLL coefficients is a
prespecified collinearity sensitivity, not the main model. Every model includes
run, checkpoint, and layer fixed effects.

- **M0 damage baseline:** `D_S ~ f_damage+family+fixed effects`.
- **M1 margin context:** M0 plus `z(intact_margin_mean)`.
- **M2 primary boundary model:** M1 plus `z(mean_delta_b)`.
- **M3 full non-tautological geometry:** M2 plus
  `z(mean_logit_delta_norm)+z(mean_abs_cosine_alignment)`.
- **M4 flip-pattern diagnostic:** M3 plus top-1-to-intact-top-2 rate. M4 is
  outcome-adjacent and cannot determine the verdict.

The primary geometry-adjusted residual is the M2 family coefficient. M3 is a
prespecified sensitivity. M0 must reproduce the ARC-006 damage-model family
coefficient within 0.0025; this is not required to equal the frozen median
residual because the estimands differ.

Primary shrinkage is
`1-|beta_family,M2|/0.019234664351851838`. Model-relative shrinkage
`1-|beta_M2|/|beta_M0|` is also reported. Negative shrinkage is retained.

Interpretation thresholds:

- negligible: less than 20%;
- meaningful partial: 20% to less than 50%;
- substantial: at least 50%;
- near-complete: at least 75% and adjusted point plus 90% interval inside the
  frozen equivalence region.

Uncertainty uses 100,000 deterministic run-cluster bootstrap draws (seed
20260826), memoized over the finite five-run resampling patterns. Tokens,
directions, layers, checkpoints, and cells are never treated as independent
scientific replicates. Report leave-one-run-out and leave-one-layer-out
sensitivity.

## Geometry matching freeze

An outcome-blind script will select a secondary geometry-compatible subset
after extraction but before joining `D_S`. It may read only target identity,
match class, `delta_b`, logit norm, and absolute cosine. A Class A cell passes
when all hold:

- absolute cross-family mean-`delta_b` difference divided by the pooled
  observation SD is at most 0.50;
- absolute log norm ratio is at most `log(1.25)`;
- absolute mean-absolute-cosine difference is at most 0.10.

Support is adequate only with at least 30 cells, at least three in each run,
and at least five in each checkpoint. Calipers are never changed after the
matched residual is revealed. This matching result is corroborative; failure
does not overwrite an otherwise identifiable primary regression.

## Stratified and heterogeneity analyses

- Margin strata use within-run/checkpoint/evaluation-seed token tertiles of
  intact margin, defined before interventions. Cell residuals are computed in
  each stratum, followed by run-level aggregation.
- Flip-conditioned cell summaries use tertiles of the two-family mean cell
  damage and are explicitly descriptive because the stratum variable contains
  the outcome.
- Layer heterogeneity compares weighted SD of ten layer-specific family effects
  from M0-like and M2-like models. Layers with fewer than eight Class A cells
  are marked low support; layer 7 is never interpreted strongly.
- Sign reversals retain all 18 previously observed positive cells. A
  leave-one-run-out logistic classifier uses only intact margin and the three
  cross-family geometry differences. Geometry is considered predictively
  informative for reversal when held-out AUC is at least 0.70 and balanced
  accuracy at least 0.65. This is predictive, not causal evidence.
- Multicollinearity reports the correlation matrix, VIF, design rank,
  condition number, coefficient stability across M0-M3, and the exact
  `delta_m=delta_b` identity.

## Quality and exclusion rules

Required: 150 unique cell keys, 300 unique family rows, 103 unchanged Class A
keys, finite values, all harness checks passing, exact evaluation counts,
recomputed `D_S`/KL/NLL agreeing with ARC-006 to `1e-10`, and maximum
`|delta_m-delta_b| <= 1e-5`. No cell is removed for sign, geometry, layer,
checkpoint, or result. Technical corruption is documented and stops analysis.

## Verdict logic

- `GEOMETRY-GO`: identified; systematic geometry difference; primary
  shrinkage at least 50%; M2 point and 90% interval inside equivalence; at
  least four of five runs shrink toward zero.
- `GEOMETRY-PARTIAL`: identified and primary shrinkage at least 20%, but the GO
  gate is incomplete, or geometry materially reduces layer heterogeneity while
  leaving a substantial residual.
- `GEOMETRY-NO`: identified, primary shrinkage below 20%, and no other frozen
  geometry analysis supplies reproducible material explanation.
- `GEOMETRY-NONIDENTIFIABLE`: the identification gate above fails.

## Resources

Local RTX 5060 only, cached Pythia-160M weights, no downloads, API cost USD 0,
external compute USD 0. No new intervention family, model, scale, corpus, or
post-result causal experiment is authorized.
