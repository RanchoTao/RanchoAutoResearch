# ARC-007R preregistration

Frozen before executing either analysis stage. ARC-006R is the sole valid
outcome source; invalid ARC-006 residuals, reversal labels, and layer summaries
are historical context only.

## Frozen population and baseline

- Corrected source commit: `de7d659f2cc869563a67eef636e1ff2bfac17d35`.
- Corrected-source final-integrity manifest: zero failures at audit.
- Exactly 150 frozen cells; primary analysis uses the unchanged 103 Class A
  cells and 206 family observations.
- Runs 2, 3, 5, 6, 8; steps 14k, 72k, 143k; layers 1-10.
- Corrected residual: `D_S(noise)-D_S(block)` under the canonical lowest-index
  top-1 rule.
- Required baseline: -0.01683304398148147, reproduced as the mean of five
  run-median Class A cell residuals to absolute tolerance 1e-12.
- Frozen equivalence bound: +/-0.0107421875.

Any baseline, key, family, match-class, or top-1 discrepancy stops as
`CORRECTED_BASELINE_MISMATCH`.

## Metric freeze

### Primary

1. intact margin summaries: mean, median, standard deviation, q10, q25, q75,
   q90 for the canonical intact top-1 and runner-up;
2. intact-class-anchored `delta_boundary = delta_z[c1]-delta_z[c2]`;
3. anchored `delta_margin` as an implementation identity check;
4. corrected top-1 retained, flip, top-1-to-runner-up, and other-flip rates.

`delta_margin` and `delta_boundary` are algebraically identical under frozen
intact-class anchoring. Both are reported, but only `delta_boundary` enters a
design matrix. Total flip rate is exactly the outcome `D_S`; it is descriptive
and is never used to predict or explain `D_S`. These restrictions prevent
perfect collinearity and target leakage.

### Secondary

- mean and median logit-perturbation L2 norm;
- signed and absolute cosine alignment with the top1-runner-up axis;
- boundary-axis projection fraction, represented by absolute cosine;
- intact-margin lower and upper tails;
- top-1-to-intact-runner-up fraction as an outcome-adjacent diagnostic only.

Rank change is not available in the saved artifacts and will not be recreated
with inference. No exploratory primary metric may be added.

## Outcome-blind first stage

Before joining corrected `D_S`, compare noise minus block for
`delta_boundary`, logit norm, and absolute cosine. Intact margin is shared by
the paired families and has zero family difference by construction. Total flip
rate is excluded because it is `D_S`.

A family geometry difference is systematic when the mean of five run-median
paired differences has a 95% run-bootstrap interval excluding zero and at
least four of five run medians share its sign. Layer consistency is descriptive
and reports the number of layer means sharing the aggregate sign.

## Outcome-blind geometry matching

Within the 103 Class A cells, a cell passes only if all hold:

- absolute noise-block mean-`delta_boundary` difference divided by the pooled
  family-observation SD is <=0.50;
- absolute log norm ratio is <=`log(1.25)`;
- absolute mean-absolute-cosine difference is <=0.10.

Support is adequate only with at least 30 cells, at least three per run, and at
least five per checkpoint. Calipers cannot change after residual reveal. The
new matcher must exactly reproduce the 31-cell historical outcome-blind ARC-007
subset or stop for investigation.

## Corrected residual models

The family observation is the model row; the independent scientific replicate
is the pretraining run. Continuous predictors are standardized over the 206
Class A family observations. Because KL and NLL are nearly collinear, the
primary damage covariate is the ARC-006 equal-weight composite
`f_damage=(z(KL)+z(NLL))/2`; separate KL/NLL is a sensitivity only.

Each model is fitted separately within each of five runs with checkpoint and
layer fixed effects. The primary coefficient is the mean of five run-specific
family coefficients. A 100,000-draw run bootstrap with seed 20260827 gives
uncertainty; leave-one-run-out means are reported.

- M0: `D_S ~ f_damage + family + fixed effects`.
- M1: M0 + intact margin mean.
- M2 primary: M1 + mean `delta_boundary`.
- M3 full non-tautological geometry: M2 + mean logit norm + mean absolute
  cosine alignment.

No model includes total flip rate or duplicate `delta_margin`.

Shrinkage uses the corrected aggregate magnitude
`R0=0.01683304398148147`: `1-|beta_family|/R0`. Less than 20% is weak, 20-50%
partial, at least 50% substantial. Negative shrinkage is preserved. Entry into
equivalence requires the adjusted point and 90% run-bootstrap interval wholly
inside the frozen band. At least four of five run coefficients must move toward
zero for a reproducible geometry adjustment.

## Sign reversal, margin strata, and layers

- Reversal labels are the corrected ARC-006R 24/103 labels only.
- A leave-one-run-out L2-logistic model uses intact margin and cross-family
  differences in delta boundary, log norm, and absolute cosine. Geometry is
  predictively informative only if held-out AUC>=0.70 and balanced
  accuracy>=0.65. This is not causal evidence.
- Near/medium/far strata are the extraction-time within-evaluation-seed intact
  margin tertiles already saved in the geometry artifacts. No new cutpoint is
  selected.
- Layer heterogeneity compares weighted SD of family-by-layer effects from a
  damage-only model versus M3. A >=25% reduction is material. Layer 7 remains
  low support and cannot support a strong claim.

## Identifiability and verdicts

Report the continuous-predictor correlation matrix, VIF, design ranks,
condition numbers, and coefficient stability. Exact duplicate margin terms are
excluded before VIF. The primary result is nonidentifiable if M2 is rank
deficient, a primary VIF exceeds 25, a primary condition number exceeds 250,
or run-cluster uncertainty cannot be computed.

- `GEOMETRY-GO`: identifiable; systematic family geometry difference; M2
  shrinkage >=50%; adjusted point and 90% interval enter equivalence; >=4/5
  runs move toward zero; at least one heterogeneity/reversal result is
  materially clarified.
- `GEOMETRY-PARTIAL`: identifiable and M2 shrinkage is 20-50%, or a
  prespecified M3/heterogeneity/reversal analysis supplies reproducible
  material explanation while a substantial family component remains.
- `GEOMETRY-NO`: identifiable; M2 and M3 shrinkage are both <20%; no
  prespecified secondary analysis supplies reproducible material explanation.
- `GEOMETRY-NONIDENTIFIABLE`: the identification gate fails.

No result is preferred. Correlation never establishes that geometry causes the
residual.

## Resources

Level 1 CPU-only analysis from sealed local JSON/NPZ/CSV artifacts. Set all
Hugging Face, Transformers, Datasets, and W&B offline variables. No inference,
download, web access, package change, API, or external compute is authorized.
