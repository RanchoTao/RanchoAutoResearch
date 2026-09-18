# ARC-008 preregistration

Frozen before any internal-direction relationship with corrected `D_S` is
computed. Only sealed ARC-006R outcomes and ARC-007R geometry are valid.

## Population and site

- Unchanged 103 Class A cells: runs 2,3,5,6,8; checkpoints 14k,72k,143k;
  frozen layers 1-10 and frozen selected beta values.
- Same WikiText assay, token ordering, canonical lowest-index `argmax`, and
  evaluation seeds 11,23,37.
- Sole site: original GPT-NeoX block `L` output, as defined in
  `representation_site.md`.
- No cell may be selected using corrected residual or reversal status.

## Stage A metrics

For each token, `delta_h_block=h_before-h_after`. Noise vectors use the exact
existing deterministic seeds for direction IDs 101,202,303. Tokens with either
norm <=1e-6 are invalid; a cell requires >=99.9% valid direction comparisons.

Primary cell summaries, pooled over token positions, three evaluation seeds,
and the three noise directions:

1. mean and median cross-family directional cosine;
2. mean directional disagreement `1-cos`;
3. mean block and noise perturbation norm;
4. log noise/block norm ratio.

Cosine q10/q90 and valid-token fraction are diagnostics. No other hidden metric
is primary.

Stage A1 is outcome blind. Directions are substantially distinct if mean
disagreement exceeds 0.75 in >=4/5 run medians with a 95% run-bootstrap lower
bound >0.75. Usable cross-cell variation requires disagreement SD >=0.002;
absence of variation weakens observational prediction but does not prohibit a
controlled Stage B direction contrast.

## Stage A2 observational analysis

The baseline cell model predicts corrected family residual from mean KL/NLL,
ARC-007R boundary displacement difference, log-norm ratio, absolute-cosine
difference, checkpoint, and layer. The augmented model adds hidden-direction
disagreement and hidden log-norm ratio. Primary evaluation is leave-one-run-out
RMSE reduction. >=10% is material. Corrected reversal prediction is secondary:
an augmented leave-one-run-out AUC >=0.70 and >=0.05 improvement is informative.

Layer heterogeneity is the cell-weighted SD of layer-median residuals before
and after augmented-model residualization; >=25% reduction is material. Tokens
are never treated as independent scientific replicates.

## Stage B intervention and calibration

Eligibility requires reliable Stage A extraction, substantial direction
difference, clean post-block injection, no retraining, outcome-blind
calibration, and runtime remaining. Lack of Stage A predictive association does
not bar the stronger counterfactual if directions are distinct.

For each token and direction, inject
`h_cf=h_after+alpha*||h_after||*u`. Block `u` is the normalized deletion vector;
noise `u` is the frozen Gaussian direction. Candidate alpha values are the
frozen selected beta times `[0.125,0.25,0.5,1,1.5,2]`.

Calibration uses only two sequences from seed 11 and never computes or stores
top-1 flips. For every cell, jointly select one block alpha and one noise alpha
that minimize:

`sum absolute log errors to frozen target KL/NLL + pair KL/NLL log imbalance +
0.5 hidden-norm log imbalance + 0.5 output-logit-norm log imbalance +
5 absolute alignment difference`.

The noise candidate averages direction IDs 101,202,303. Corrected `D_S` is
revealed only on seeds 23 and 37 after selection.

Primary confirmatory eligibility requires all:

- relative block/noise KL difference <=15%;
- relative block/noise NLL-damage difference <=15%;
- hidden norm ratio <=1.25;
- output-logit norm ratio <=1.25;
- absolute boundary-alignment difference <=0.10.

Support requires >=30 eligible cells, >=3 per run, and >=5 per checkpoint.
Calipers cannot be loosened. Calibration and confirmation balance are both
reported; confirmatory eligibility defines the causal set.

The primary paired effect is
`D_S(noise_direction)-D_S(block_direction)`, summarized as the mean of five
run-median effects with a 100,000-draw run bootstrap and leave-one-run-out
means. The noise condition averages three frozen direction IDs. A fixed
`+/-0.003` direction-effect equivalence band is used.

## Verdicts

- `DIRECTION-GO`: identifiable support; 95% CI excludes zero; >=4/5 run
  medians share sign; absolute effect >=0.005; effect direction matches the
  corrected family residual; confirmatory balances pass.
- `DIRECTION-PARTIAL`: identifiable and either CI excludes zero with absolute
  effect 0.0025-0.005, or a larger reproducible effect leaves clear
  run/layer heterogeneity.
- `DIRECTION-CORRELATIONAL`: Stage A2 is materially predictive but Stage B is
  identified and its 95% CI includes zero or opposes the observational story.
- `DIRECTION-NO`: Stage A2 is not material and an identified Stage B point plus
  90% CI lie wholly inside +/-0.003.
- `DIRECTION-NONIDENTIFIABLE`: Stage B support/balance fails or direction cannot
  be independently manipulated; observational results cannot rescue causality.

No outcome is preferred. Counterfactual injection tests the effect of the
specified direction analogue; it does not prove that literal layer deletion
works solely through this vector.

## Stop and resources

Local-only, <=35 minutes preferred and <=60 minutes absolute. Missing required
local checkpoint/data returns `LOCAL_ARTIFACT_MISSING`; exceeding the absolute
budget returns `008-INCOMPLETE`. No downloads, APIs, package changes, remote
compute, new model/corpus, or follow-on ARC.
