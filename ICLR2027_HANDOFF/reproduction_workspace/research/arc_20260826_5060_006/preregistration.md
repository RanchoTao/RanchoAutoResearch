# ARC-006 preregistration

Initial freeze: 2026-08-26 Asia/Shanghai, before any ARC-006 target solution or
new-family `D_S` was generated. Pilot-derived numeric feasibility decisions
will be written to `confirmatory_protocol.md` and committed before confirmation.

## Frozen prior assay

No ARC-003/004/005 definition changes.

- Model: PolyPythias/Pythia-160M, 12 GPT-NeoX blocks.
- Runs: confirmatory combined seeds 2, 3, 5, 6, 8; pilot seeds 1 and 4 are
  excluded from confirmation.
- Checkpoints: step14000, step72000, step143000 in confirmation.
- Locations: all interior blocks 1-10.
- Evaluation selections: seeds 11, 23, 37; six sequences of 256 next-token
  positions per selection; identical WikiText-2 tokens and tokenizer.
- Block family: delete exactly one target block.
- Noise family: compute the complete target block, then add deterministic
  token-wise norm-controlled Gaussian activation noise
  `h_beta = h + beta * ||h|| * u/||u||`.
- `S`: token-level top-1 agreement between intact and intervened logits.
- `D_S = 1-S`: algebraic top-1 damage. The ARC-005 cross-family residual and
  the ARC-006 primary residual are cellwise
  `D_S(noise)-D_S(block)` at the same run/checkpoint/layer. This resolves the
  prompt's abbreviated `Delta S` notation in favor of the frozen ARC-005
  estimand; training endpoint `Delta S` remains final `S` minus early `S`.
- KL: token-mean `KL(p_intact || p_intervened)`.
- NLL damage: intervened next-token NLL minus intact NLL.
- Relative and absolute local activation magnitude: frozen ARC-004/005
  definitions.
- Scientific replicate: independent pretraining run. Targets, checkpoints,
  layers, evaluation selections, directions, and tokens are repeated measures.
- ARC-005 equivalence bound: `epsilon = 0.0107421875`.
- ARC-005 residual: `-0.019603587962962975`, 95% CI
  `[-0.02591869212962968, -0.01404079861111110]` on 26/150 matches.
- Frozen catastrophic thresholds: intervened NLL > 8.0, KL > 2.5, or top-1
  agreement <0.20. Targeting cannot access the last quantity; it records the
  first two. Reveal records all three without post-result exclusion changes.

The completed prior audit found no invalidating implementation bug. Discovery
of one stops this ARC as `PRIOR ASSAY INVALIDATION`.

## Hypotheses

- **H_match_artifact:** prospective high-quality matching moves the residual
  into the frozen equivalence band.
- **H_family_real:** adequate prospective matching leaves a stable residual
  materially outside the band.
- **H_partial:** the residual shrinks but remains meaningfully outside
  equivalence or retains structured heterogeneity.
- **H_nonidentifiable:** a scalar noise strength cannot jointly target the two
  output-damage coordinates with adequate coverage.

No hypothesis is preferred.

## Blinding contract

`src/run_targeting.py` is the only targeting executable. It may compute and
write only intact/intervened NLL, forward KL, beta, activation magnitude,
technical validation, objective values, target identifiers, and runtimes. It
must contain no `argmax`, top-1 comparison, agreement accumulator, confidence
bin, `S`, or `D_S` calculation. It reads sanitized target files produced by
`src/prepare_targets.py`; those files contain no agreement/damage outcome.

`src/run_reveal.py` is a separate executable. It may not be run until all
confirmatory beta solutions, match classes, failures, and the sealed manifest
have been committed. Targeting stdout reports only technical progress and
never scientific outcomes. A source-token audit and output-schema audit are
mandatory before each freeze.

## Target selection

Confirmation uses every one of the 150 frozen block cells formed by five runs
x three checkpoints x ten interior layers. No outcome-dependent sampling is
permitted. A block target is eligible if its retained KL and NLL damage are
finite and below the existing catastrophic output thresholds; all ineligible
targets remain in the manifest with a reason. The anchor metrics are equal
averages over the three frozen evaluation selections.

Pilot uses the disjoint 16 cells from seeds 1 and 4 x steps 14000 and 143000 x
layers 2, 5, 8, and 10. It may inspect only target/achieved KL/NLL, beta,
magnitude, objective, monotonicity, runtime, and match class.

## Initial targeting algorithm

For a target `(K_t, N_t)`, evaluate the same three deterministic directions and
evaluation selections used in ARC-005. Minimize the frozen scalar objective

`L(beta) = ((K(beta)-K_t)/max(0.01,0.10*|K_t|))^2 +
           ((N(beta)-N_t)/max(0.015,0.10*|N_t|))^2`.

Both coordinates receive equal weight in units of the original ARC-005 joint
calipers. The pilot fixed grid is `[0, .25, .50, .75, 1.00, 1.25]`. Choose the
best grid point, bracket it by adjacent grid points, then perform deterministic
golden-section minimization for at most eight refinements or bracket width
`<=0.0025`. Search never expands beyond `[0,1.25]` after pilot. Ties choose the
smaller beta. Every evaluated trial is retained.

Pilot may change only the fixed search range, grid density, refinement count,
or numeric stopping tolerance when technical evidence shows boundary clipping
or inadequate numerical resolution. It may not use or reveal `D_S`, change the
objective weights, select targets for matchability, or alter prior evidence.

## Initial match classes

- **Class A:** KL error <= `max(.005, .05*|K_t|)` and NLL error <=
  `max(.0075, .05*|N_t|)`.
- **Class B:** not A, but KL error <= `max(.01, .10*|K_t|)` and NLL error <=
  `max(.015, .10*|N_t|)`.
- **Class C:** outside the Class B joint tolerance.

Confirmation thresholds and any pilot-justified refinements will be frozen in
`confirmatory_protocol.md`. Primary scientific analysis uses Class A only;
A+B is a prespecified sensitivity. Class C is never silently included.

## Statistical and verdict contract

Primary residual is the mean of per-run median Class-A cell residuals. Report
the mean, median, 100,000-sample run bootstrap 90% and 95% intervals (seed
20260826), all per-run values, and checkpoint/layer/damage-stratum structure.
Equivalence requires the point estimate and full 90% interval inside
`[-0.0107421875,+0.0107421875]`.

Report shrinkage as
`1-|residual_006|/0.019603587962962975`; negative shrinkage is allowed. Compare
Class A with A+B and leave-one-run-out results. Secondary fixed-effects models
are `D_S ~ z(KL)+z(NLL)+family+run+checkpoint+layer` and the corresponding
family interactions. These output-derived variables are not causal mediators.

Final confirmatory quality thresholds will be frozen after the blinded pilot.
They must require materially greater coverage than ARC-005's 17.3%, coverage
in every run/checkpoint/layer region, exact target-key integrity, and locally
acceptable KL/NLL balance.

- `TARGETING-GO`: adequate quality and Class-A equivalence passes.
- `TARGETING-FAMILY`: adequate quality, residual 95% interval lies wholly
  outside equivalence, >=4/5 run residuals share its sign, and leave-one-run-out
  results retain the interpretation.
- `TARGETING-PARTIAL`: adequate quality with meaningful shrinkage or ambiguity,
  but neither GO nor FAMILY criteria are met.
- `TARGETING-NONIDENTIFIABLE`: frozen prospective coverage/balance gate fails.

The quality gate is evaluated before outcome interpretation. If it fails, the
verdict is NONIDENTIFIABLE even if the revealed residual looks attractive.

## Exclusions and resources

No converged target is removed for beta, residual, sign, seed, checkpoint, or
layer. Technical corruption, nonfinite output, failed harness, and frozen
catastrophic status are documented, never silently removed. Local RTX 5060,
cached 160M weights, USD 0 API and external compute. No third family, scale,
architecture, corpus, or paid strategist is authorized. Repository DeepSeek
guidance is handled as `codex-only-fallback` because external strategy is not
required or budget-authorized for this fixed identification experiment.

