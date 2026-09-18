# ARC-20260826-5060-005 preregistration

Initial freeze: 2026-08-26 Asia/Shanghai, before generating or inspecting any
ARC-005 intervention outcome. A second commit will freeze the confirmatory
strength grid after damage-support-only calibration.

## Frozen prior evidence and assay

No ARC-003/004 definition is changed.

- Model: PolyPythias/Pythia-160M, 12 GPT-NeoX blocks.
- Interior locations: blocks 1-10; first and last blocks excluded.
- Corpus: cached WikiText-2 train text.
- Confirmatory evaluation selections: seeds 11, 23, 37; six sequences of 256
  next-token positions each.
- Checkpoints: step14000, step72000, step143000.
- `S`: token-level top-1 agreement between intact and intervened logits.
- `D_S = 1-S`: algebraic damage convention only.
- `Delta S`: step143000 `S` minus step14000 `S`, within pretraining run under
  an otherwise identical intervention grid.
- KL damage: token-mean `KL(p_intact || p_intervened)`.
- NLL damage: intervened next-token NLL minus intact NLL.
- Confidence bins: `[0,.05)`, `[.05,.1)`, `[.1,.2)`, `[.2,.4)`, `[.4,1.01]`
  using intact top-1 confidence.
- Relative magnitude: token-mean
  `||h_intervened-h_intact||_2/(||h_intact||_2+eps)` at the target output.
- Absolute magnitude: token-mean hidden-state RMS displacement.
- Scientific replicate: independent combined initialization/data-order
  pretraining run. Tokens, directions, layers, and evaluation selections are
  not independent scientific replicates.

Prior anchor values available before this ARC:

- ARC-004 magnitude-matched functional contrast: `0.04296875`.
- ARC-004 damage-matched residual: `0.00245949`, 95% interval crossing zero.
- Historical exact-deletion 5th-95th support over eligible 160M cells:
  KL `[0.212317, 1.307634]`, NLL damage `[0.226265, 1.271642]`.

The prior code/raw audit found no implementation bug. A genuine prior-assay bug
discovered later stops the ARC as `PRIOR ASSAY INVALIDATION`.

## Hypotheses

### H_general

Functional predictive damage is the central cross-intervention descriptor.
The new family reproduces negative `Delta S`, preserves the within-family
ordering functional damage > raw magnitude, and has a scientifically small
family residual after joint KL/NLL matching to exact block deletion.

### H_family

Intervention identity has a large reproducible residual after joint damage,
run, checkpoint, and layer control.

### H_partial

The sign and some functional alignment transfer, but the equivalence bound or
interaction criterion fails, leaving reproducible family-specific structure.

### H_artifact

The sign fails under the distinct intervention or cross-family evidence is so
incompatible that the original result is likely block-bypass-specific.

## New intervention family

Use token-wise norm-controlled additive Gaussian activation noise after one
complete target block, exactly as defined in `intervention_selection.md`.
`beta=0` must produce max absolute logit difference <= `1e-4` and identical
top-1 outputs versus intact. Repeated identical seeds must produce max logit
difference <= `1e-4`. A failed new harness stops until corrected; it does not
invalidate prior evidence unless the failure exposes a prior-assay bug.

## Stage 1 calibration contract

- Runs: combined seeds 1 and 4 only.
- Checkpoints: step14000 and step143000.
- Layers: 2, 5, 8, 10.
- Evaluation: selection seed11, six length-256 sequences, exactly matching the
  retained anchor selection for cell-level support calibration.
- Direction IDs: 101 and 202.
- Prespecified broad beta sweep:
  `[0.05, 0.10, 0.20, 0.35, 0.50, 0.75, 1.00, 1.50]`.

Calibration may inspect only implementation validity, measured magnitude, KL,
NLL damage, finite/catastrophic rates, and overlap/matchability to retained
block-deletion data. It may not inspect `S`, `D_S`, `Delta S`, agreement by
checkpoint, or any hypothesis-direction contrast before the confirmatory grid
is frozen.

### Deterministic strength inclusion

A beta enters confirmation when all apply:

1. all values are finite;
2. no more than 5% of pilot cells have intervened NLL > 8.0, KL > 2.5, or
   top-1 agreement below 0.20 (the script may use the last field only as a
   catastrophic count and may not reveal its values or checkpoint direction);
3. at least 20% of its pilot cells lie jointly inside the historical block
   5th-95th KL and NLL support above; and
4. it contributes at least one additional exact block cell match under the
   frozen cross-family caliper, or is needed to cover a different anchor damage
   quartile.

Every beta satisfying these rules is retained, up to all eight. No retained
beta may be removed for an unfavorable `S` result. If fewer than three betas or
fewer than two anchor quartiles survive, calibration fails and ARC-005 stops as
`FAMILY-PARTIAL` for insufficient support rather than changing the sweep.

## Stage 2 confirmatory contract

- Independent confirmatory runs: combined seeds 2, 3, 5, 6, 8.
- Checkpoints: step14000, step72000, step143000.
- Layers: all interior blocks 1-10.
- Direction IDs: 101, 202, 303.
- Evaluation corpus/selections/length/count: frozen ARC-004 contract above.
- Strength grid: every beta passing the deterministic calibration rule; frozen
  in `confirmatory_protocol.md` and committed before these runs.
- Original anchor: retained exact block-deletion raw cells at the same runs,
  checkpoints, evaluation selections, and layers. No block rerun unless an
  exact consistency check fails.

Formal cell metrics average equally over the three direction IDs and three
evaluation selections. The strength grid is averaged equally for Test A.

### Exclusions

No completed confirmatory run/cell is excluded based on `S`, KL, NLL, effect
direction, or strength. Only nonfinite/corrupt output or a documented harness
failure is excluded. Cross-family matching discards out-of-caliper cells as
common-support failures, retaining counts and reasons. Catastrophic cells are
reported and excluded only from cross-family interpretation under the frozen
thresholds above; Test A still reports them and a sensitivity excluding them.

## Test A: sign-level replication

For each run/checkpoint, average `S` over frozen strengths, layers, direction
IDs, evaluation selections, and tokens. Primary contrast is final minus early.
Sign replication passes when at least 4/5 run contrasts are negative and the
100,000-sample run-bootstrap 95% interval for their mean lies below zero.

## Test B: within-new-family mechanism discrimination

### Magnitude matched

Within run, checkpoint, and beta (thus exactly matched intended relative
magnitude), greedily pair different layers with absolute KL difference >=0.03.
Sort by largest KL separation, then stable layer ID; do not reuse a cell. The
directional contrast is `D_S(higher KL)-D_S(lower KL)`. Evidence for functional
alignment requires >=4/5 positive run medians and a run-bootstrap 95% interval
above zero.

### Damage matched

Within run and checkpoint, greedily pair different beta/layer cells satisfying:

- KL gap <= `max(0.01, 0.10 * pair-mean absolute KL)`;
- NLL-damage gap <= `max(0.015, 0.10 * pair-mean absolute NLL damage)`;
- magnitude ratio >=1.25.

The contrast is `D_S(higher magnitude)-D_S(lower magnitude)`. Raw magnitude is
weakened when its run-bootstrap interval includes zero and its absolute point
estimate is <25% of the new-family magnitude-matched functional contrast.

## Test C: primary cross-family damage matching

Aggregate both families to the same run-checkpoint-layer grain. Within each
exact run, checkpoint, and layer, match one exact-deletion cell to the closest
unused new-family beta satisfying the same joint KL/NLL calipers used above.
Minimize the sum of normalized KL and NLL gaps; ties use smaller beta.

Required match quality:

- at least 50 matched block cells total;
- at least five per independent run;
- at least 30% of the 150 eligible block cells;
- every retained pair satisfies both calipers;
- median standardized KL and NLL gaps are each <=0.10 of pair means.

Primary family residual is the run-level median of
`D_S(new)-D_S(block)` over matched pairs. Estimate its mean with 100,000
run-level bootstrap samples (seed 20260826).

## Prespecified family equivalence and interaction thresholds

The scientifically small family-residual bound is

`epsilon_family = 0.25 * 0.04296875 = 0.0107421875`.

This is one quarter of the frozen ARC-004 functional-damage contrast and nearly
twice the upper magnitude of ARC-004's damage-matched residual interval. It was
chosen from prior evidence, not ARC-005 outcomes.

Report
`R_family = |mean family residual| / 0.04296875`.
Family residual is equivalent/small only when its 90% run-bootstrap interval is
fully inside `[-epsilon_family, +epsilon_family]` and its point estimate is
inside the same bound. The 95% interval is also reported for estimation.

Secondary common-support regressions are frozen as:

1. cross-family primary diagnostic:
   `D_S ~ KL + NLL_damage + family + checkpoint + layer + run`;
2. cross-family interaction diagnostic:
   `D_S ~ F_damage * family + checkpoint + layer + run`, where
   `F_damage` is the mean of pooled-common-support z-scored KL and NLL damage.

The five-run historical exact-deletion records do not contain local activation
magnitude. `M_rel` is therefore analyzed in the prespecified within-new-family
models/matches, not silently imputed into the five-run cross-family regression.
A clearly labeled two-run sensitivity may add ARC-004 alpha=1 magnitude for
runs 6 and 8, but it cannot replace the five-run primary analysis.

Strong interaction evidence requires both a run-bootstrap 95% interval for the
family slope difference excluding zero and an absolute point slope difference
greater than 25% of the pooled common slope magnitude. Regression is secondary
because KL/NLL/`D_S` share logits.

## Confidence, monotonicity, and falsification

- Repeat Test A inside every frozen intact-confidence bin with >=100
  token-layer-direction observations at both endpoints.
- Report beta monotonicity of KL/NLL for every run-checkpoint-layer; do not
  require it for promotion.
- Report the weakest run, checkpoint, layer, damage quartile, and largest
  cross-family residual stratum.
- Repeat Test C with 5% and 15% relative calipers as prespecified sensitivity;
  do not choose among them based on favorability.
- Report final verdict with and without catastrophic cells where applicable.

## Verdict logic

### FAMILY-GO

Requires Test A pass, within-family functional alignment pass, adequate Test C
matching, family-residual equivalence pass, and no strong family x damage
interaction. Perfect numeric equality is not required.

### FAMILY-PARTIAL

Use when the sign/general functional ordering transfers but family equivalence,
interaction, common-support quality, or one robustness component remains
materially family-specific or uncertain.

### FAMILY-KILL

Use when Test A fails decisively—defined as at most 1/5 negative runs with its
bootstrap interval not below zero, or at least 4/5 positive runs with an
interval above zero—or cross-family results show a large,
reproducible family residual at least 50% of the ARC-004 functional contrast
(`>=0.021484375`) in a direction incompatible with a cross-family account,
especially when matching quality is adequate.

If neither GO nor KILL conditions hold, return PARTIAL. Confidence is HIGH only
with all five runs, adequate common support, stable leave-one-run-out results,
and no single checkpoint/layer dominance.

## Resource contract

Local RTX 5060 only; no model >160M, no new architecture, no paid API, no
external compute. All available weights must load offline. GPU-bearing runtime,
wall time, peak CUDA allocation, RAM, storage growth, downloads, and cost are
recorded.
