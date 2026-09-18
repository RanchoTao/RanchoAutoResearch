# ARC-20260826-5060-004 preregistration

Frozen before any ARC-004 mechanism-assay result was generated or inspected.

## Frozen prior assay

ARC-003 remains immutable evidence. This ARC does not redefine its quantities.

- Model family and scale: PolyPythias/Pythia-160M, 12 GPT-NeoX blocks.
- Evaluation corpus: the cached WikiText-2 train text used by ARC-001 through
  ARC-003.
- Evaluation selections: seeds 11, 23, and 37; six sequences of 256
  next-token positions per selection.
- Candidate locations: every interior block, layers 1 through 10; the first
  and last blocks remain excluded.
- Frozen deletion: remove exactly one target block from the executed module
  list, directly connecting its input to the next block.
- `S`: token-level top-1 agreement between intact and intervened logits,
  averaged equally over the frozen interior layers, tokens, and evaluation
  selections for the prior checkpoint/run contrast.
- `Delta S`: within-run step143000 `S` minus step14000 `S`.
- NLL damage: intervened next-token NLL minus intact next-token NLL.
- KL damage: token-mean `KL(p_intact || p_intervened)`.
- Confidence control: intact top-1 confidence bins `[0,.05)`, `[.05,.1)`,
  `[.1,.2)`, `[.2,.4)`, and `[.4,1.01]`.
- No corpus, token, layer, or metric normalization is changed.

For intervention-level mechanism comparisons, the response is written
`D_S = 1 - S`. This is only an algebraic sign convention: larger values mean
more top-1 prediction damage. It is not a redefinition of `S` or `Delta S`.

## Competing hypotheses

### H_damage

Prediction damage is the primary measured driver of `D_S` and hence of the
training-associated `Delta S`. At closely matched raw intervention magnitude,
interventions with larger KL/NLL damage should have larger `D_S`. Once damage
is matched, residual magnitude/location contrasts should shrink substantially.

Primary functional-damage variable: KL. NLL damage is the prespecified
sensitivity measure. A joint KL+NLL model is secondary because collinearity is
expected.

### H_magnitude

Raw intervention magnitude is primary. At closely matched KL and NLL damage,
larger raw intervention magnitude should still produce larger `D_S`; the
damage contrast should materially attenuate when magnitude is matched.

Primary raw magnitude is the token-mean local relative activation change at
the target block output:

`M_rel = mean(||h_intervened - h_intact_block||_2 / (||h_intact_block||_2 + eps))`.

The corresponding absolute hidden-state RMS change is retained as a fixed
sensitivity measure. `alpha * ||theta_layer||_2` is recorded only as a
parameter-scale proxy because the intervention acts on a residual update, not
by directly changing stored parameters.

### H_location

Layer/location has a reproducible effect on `D_S` beyond functional damage and
raw intervention magnitude. This requires cross-run stability of residual
layer profiles, not merely a significant omnibus coefficient from pooled
layer observations.

### H_other/confound

No simple candidate dominates, effects reverse by checkpoint/run, or the
result is explained by confidence conditioning, normalization, data order,
intervention state leakage, metric construction, or failed equivalence to the
frozen deletion.

## Intervention family

Use the existing single-block bypass machinery with prespecified continuous
strengths `alpha = 0.25, 0.50, 0.75, 1.00`. For a target block with input `x`
and intact output `b(x)`, execute

`h_alpha = x + (1 - alpha) * (b(x) - x)`.

Thus `alpha=0` is intact and `alpha=1` is exactly the frozen block bypass.
Only one block is intervened on per forward pass. No new model family is used.

Before formal evaluation, two harness tests are mandatory:

1. `alpha=0` versus intact: maximum absolute logit difference <= `1e-4` and
   identical top-1 predictions.
2. `alpha=1` versus the original module-list deletion: maximum absolute logit
   difference <= `1e-4` and identical top-1 predictions.

Failure caused by a prior-assay bug yields `ASSAY INVALIDATION` and stops the
ARC. Failure confined to the new wrapper invalidates the new harness and must
be corrected before any formal result; it does not alter ARC-003.

## Runs, checkpoints, and staging

- Pilot mechanism runs: combined seeds 1, 4, and 9.
- Confirmatory mechanism runs: combined seeds 6, 7, and 8.
- Checkpoints: step14000, step72000, step143000 (early, middle, final).
- Each run/checkpoint evaluates all 10 interior layers at all four strengths.
- Existing model cache is used offline. No new weights or paid APIs are needed.

Pilot output may be inspected only for matching feasibility and technical
integrity before the confirmatory runs start. Pilot hypothesis contrasts are
not used to change calipers, outcomes, checkpoints, strengths, or gates.

## Deterministic matched contrasts

Matching is performed separately within each run and checkpoint. Candidate
pairs are sorted by normalized balance error, then greedily selected without
replacement. Scientific uncertainty is computed over run-level summaries;
matched pairs, layers, evaluation selections, and tokens are not treated as
independent scientific replicates.

### Experiment A: magnitude matched

A candidate pair must satisfy:

- symmetric relative `M_rel` difference <= 10%, i.e.
  `abs(log(M_rel_1/M_rel_2)) <= log(1.10)`;
- absolute KL difference >= 0.03;
- the two observations are distinct layer-strength interventions.

The directional contrast is
`D_S(higher KL) - D_S(lower KL)`. Match quality and the NLL-damage difference
are reported. The run-level statistic is the median directional contrast over
its matched pairs.

### Experiment B: damage matched

A candidate pair must satisfy both:

- absolute KL difference <= `max(0.01, 0.10 * pair-mean KL)`;
- absolute NLL-damage difference <= `max(0.015, 0.10 * pair-mean absolute NLL damage)`;

and must differ by at least three layers or have an `M_rel` ratio >= 1.25.
The directional magnitude contrast is
`D_S(higher M_rel) - D_S(lower M_rel)`. Location is assessed from residual
layer profiles after fitting the prespecified covariates.

### Feasibility gate

The matching design is feasible only if each of the three pilot runs provides:

- at least six disjoint Experiment-A pairs across its checkpoints; and
- at least six disjoint Experiment-B pairs across its checkpoints;

and the pooled median balance satisfies the relevant caliper. If either arm
fails, no caliper will be relaxed. The ARC stops as `MECHANISM-AMBIGUOUS` with
the matching failure documented rather than brute-forcing an altered design.

## Prespecified analyses

Primary evidence is the two matched contrasts. For each, report every pair,
run medians, sign counts, confirmatory-only results, and a 100,000-sample
run-level bootstrap interval for the mean run statistic (seed 20260826).

Secondary models, with continuous predictors standardized, are:

1. pooled diagnostic:
   `D_S ~ KL + M_rel + layer + checkpoint + run`;
2. NLL sensitivity:
   `D_S ~ NLL_damage + M_rel + layer + checkpoint + run`;
3. exploratory collinearity diagnostic:
   `D_S ~ KL + NLL_damage + M_rel + layer + checkpoint + run`;
4. longitudinal diagnostic:
   `D_S ~ KL + M_rel + progress + layer + run`.

Checkpoint and numeric progress are never included in the same design matrix
because they are deterministically collinear. Coefficients are descriptive;
condition diagnostics and leave-one-run-out stability are mandatory. A
damage-adjusted training-progress coefficient is not interpreted causally.

Residual location evidence requires both: (a) the between-layer residual range
exceeds a within-run label-permutation 95% interval, and (b) the layer-residual
profile has positive median pairwise Spearman correlation across runs. This is
supportive evidence only because location is not randomized independently of
block identity.

Confidence robustness repeats the Experiment-A direction within each frozen
intact-confidence bin when at least 100 token observations are available per
member. Absolute and relative activation magnitudes are both reported to expose
normalization dependence.

## Falsification and interpretation logic

Evidence favors **H_damage** when Experiment A is positive in at least 5/6
runs, its run-bootstrap interval excludes zero, the confirmatory-only mean is
positive, and Experiment B is materially weaker or compatible with zero.

Evidence favors **H_magnitude** when Experiment B is positive in at least 5/6
runs with a run-bootstrap interval excluding zero, while the magnitude-matched
damage contrast is weak or inconsistent.

Evidence favors **H_location** only when the residual-location criteria above
replicate and damage matching is adequate. A visible raw layer curve alone is
insufficient.

Evidence against a simple mechanism includes bootstrap intervals spanning
zero, opposite confirmatory signs, strong seed/checkpoint interactions,
dominance by one run/checkpoint, poor matching, or incompatible KL-versus-NLL
conclusions.

An artifact warning is triggered by failed alpha equivalence, order-dependent
outputs, substantial conclusions changing under the fixed absolute-magnitude
sensitivity, or disappearance/reversal across all eligible confidence bins.

Final verdict:

- `MECHANISM-GO`: a clear reproducible matched discrimination survives the
  confirmatory runs and key artifact controls.
- `MECHANISM-AMBIGUOUS`: Candidate A remains valid but these mechanisms are not
  cleanly distinguishable or matching is infeasible.
- `MECHANISM-KILL`: a trivial assay artifact/confound substantially explains
  Candidate A or invalidates its paper direction.

No one result is required to be positive. No thresholds, exclusions, or
primary hypotheses may be altered after freezing. Technical failures may be
excluded only with retained logs and explicit documentation. Any later idea or
analysis is labeled in `posthoc_notes.md`.

## Resource ceiling

Local RTX 5060 only; no paid services. Target GPU-active time <= 2 hours and
wall time <= 3 hours. No 70M or larger-scale confirmation is run unless the
160M result is already clear; this ARC does not authorize such expansion.
