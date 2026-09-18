# ARC-20260826-5060-004 mechanism report

## Primary verdict

**MECHANISM-GO**

**Confidence: MEDIUM**

Candidate A should proceed to one reviewer-critical robustness ARC. The
controlled result is clear enough to discriminate against a simple raw-
magnitude explanation, but not causal enough to identify KL/NLL as a biological
or optimization mechanism.

## 1. Mechanism hypotheses tested

- **H_damage:** top-1 substitutability damage tracks functional predictive
  damage (forward KL and NLL degradation) at matched raw perturbation size.
- **H_magnitude:** raw local activation displacement drives the effect, with
  KL/NLL acting mainly as correlated consequences.
- **H_location:** layer identity contributes beyond damage and magnitude.
- **H_other/confound:** confidence conditioning, normalization, state leakage,
  checkpoint/run dependence, or metric implementation creates the result.

## 2. Which survived best?

**H_damage survived best.** At a median 1.019 relative-magnitude ratio, the
higher-KL intervention produced 0.04297 more top-1 damage at the run-median
level (95% interval `[0.03537, 0.05246]`), positive in 6/6 runs and 3/3
independent confirmatory runs. Absolute-RMS matching replicated the direction
in 6/6 runs.

## 3. What was falsified or weakened?

A simple H_magnitude account was weakened. After joint KL/NLL matching, the
pooled residual magnitude contrast was 0.00246 with an interval spanning zero.
Restricting to pairs whose raw magnitude differed by at least 25% produced
-0.00054, interval `[-0.00456, 0.00371]`, and only 3/6 positive run medians.

H_location was not falsified: residual layer profiles showed modest replicated
structure. It did not, however, yield a stable damage-matched directional
effect across checkpoints.

## 4. What remains unidentified?

- Whether KL/NLL is a causal mediator or simply a close output-space descriptor
  of top-1 flips.
- Which block computation or representation property creates larger functional
  damage later in training.
- Whether the discrimination survives attention-only, MLP-only, random
  equal-magnitude, or block-swap interventions.
- Whether it survives another corpus or downstream task.
- Whether residual location structure is mechanistic or a layer-specific
  measurement geometry artifact.

## 5. Is this causal enough for a mechanism claim?

No. Matching controls measured magnitude and known design variables, but KL is
not independently randomized. KL, NLL, and top-1 agreement all derive from the
same intervened logits. The study supports a **controlled mechanism
discrimination** claim, not “KL causes the erosion.”

## 6. Strongest safe claim

Within the frozen Pythia-160M single-block residual-attenuation assay,
training-associated loss of top-1 block substitutability is aligned with growth
in functional predictive damage rather than explained by raw local activation
displacement alone. This alignment replicates across six independent
pretraining runs, two magnitude normalizations, all three tested checkpoints,
and fixed intact-confidence strata.

## 7. Currently overstated claim

“Continued pretraining causally makes layers specialized through KL damage,” or
“perturbation magnitude and layer location do not matter,” would both overstate
the evidence.

## 8. First ICLR reviewer attack

The verifier variables are not mechanistically independent: `D_S`, KL, and NLL
all come from the same output distributions, while the strength sweep stays
inside one residual-attenuation intervention family. Matching may merely expose
metric geometry rather than a general property of layer substitutability.

## 9. Highest-information response

Prospectively repeat the same magnitude/damage matching with independent
intervention families—attention-only bypass, MLP-only bypass, and equal-local-
magnitude random residual directions—on a minimal three-run,
early/middle/final design. Require the H_damage discrimination to transfer
without changing calipers or outcomes.

## Evidence ledger

- **Strongest evidence:** 6/6 positive magnitude-matched run medians; run-level
  interval excludes zero; confirmatory 3/3; exact alpha endpoint replication;
  absolute magnitude and confidence sensitivities agree.
- **Strongest counterevidence:** observational regressions retain a large
  magnitude coefficient; residual layer structure passes the supportive
  permutation criterion; output metrics are co-constructed.
- **Remaining fatal-risk candidate:** the apparent functional-damage mechanism
  is specific to residual attenuation or to output-metric geometry.

## Resource use

- Recorded checkpoint runtime sum: 131.30 seconds (2.19 minutes). This is a
  conservative device-bearing wall-time proxy; continuous GPU-utilization
  telemetry was not sampled.
- Peak allocated CUDA memory: 1,062,865,408 bytes (0.99 GiB).
- Formal execution through final consistency/artifact lock: approximately 12
  minutes wall time.
- ARC artifacts added: approximately 5.16 MiB.
- New model downloads: none.
- API/paid-service cost: USD 0.

## Final fields

- **verdict:** MECHANISM-GO
- **confidence:** MEDIUM
- **strongest evidence:** magnitude-matched functional-damage contrast,
  replicated 6/6 with held confirmatory 3/3.
- **strongest counterevidence:** KL/NLL/top-1 co-construction plus residual
  location and observational magnitude effects.
- **remaining fatal-risk candidate:** intervention-family/metric-geometry
  specificity.
- **recommended next ARC:** ARC-005, intervention-family robustness.
