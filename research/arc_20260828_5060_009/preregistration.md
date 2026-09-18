# ARC-009 preregistration

Frozen after the 10-cell outcome-blind numerical pilot and before the
confirmatory 103-cell continuous-alpha calibration.

## Population and blinding

- Exactly the 103 ARC-006R Class A cell IDs in `sanitized_targets.csv`.
- Runs 2, 3, 5, 6, 8; checkpoints 14k, 72k, 143k; frozen layers and selected
  beta values.
- Same local Pythia-160M checkpoints, WikiText assay, seed 11, two sequences,
  direction IDs 101/202/303, representation site, and corrected top-1
  convention as ARC-008.
- Calibration code may read only the eight-column sanitized target table and
  outcome-blind local assay assets. It must never load or compute `D_S`.

## Alpha solver

The direction is fixed. Alpha is bounded to `[0.125 beta, 2 beta]`, exactly the
previously validated range. Primary roots use bisection; joint comparability
uses the deterministic bounded refinement in `solver_definition.md`.

Numerical tolerance is 0.25% relative target-metric error or 0.001 log-alpha
bracket width. The iteration limit is 14 per root. The frozen fallback is a
17-point log-spaced bounded search. No extrapolation is permitted.

Convergence requires finite evaluations, completed root/fallback processing,
and four bounded coordinate rounds. An optimum within 1% of the normalized
log-range boundary is flagged, not silently excluded.

## Frozen objective and calipers

The ARC-008 target/pair objective and primary calipers are unchanged.
`PASS-A` requires all five:

- relative block/noise KL difference <= 15%;
- relative block/noise NLL-damage difference <= 15%;
- hidden perturbation norm ratio <= 1.25;
- output-logit norm ratio <= 1.25;
- absolute output-alignment difference <= 0.10.

`PASS-B` is descriptive only: both core damage calipers pass and exactly one
secondary condition misses `PASS-A` but remains within a frozen relaxed bound
(hidden ratio <=1.35, output ratio <=1.35, or alignment difference <=0.15).
`PASS-A+B` never substitutes for the primary gate.

Failures are classified in priority order as numerical, no-bracket,
pathological, or tradeoff. Pathological means a nonfinite intervention or an
allowed-range candidate with KL/NLL damage above 5.0 or hidden relative norm
above 2.0. All remaining simultaneous-target/caliper failures are tradeoffs.

## Coverage and verdicts

Meaningful representation requires at least 5 `PASS-A` cells per run and 8 per
checkpoint. Adequate balance additionally requires no run to exceed 35% and no
checkpoint to exceed 65% of all `PASS-A` cells. Layer and damage-regime
concentration are reported but are not used to move the primary threshold.

- `ALPHA-FEASIBLE`: at least 70/103 `PASS-A`, adequate coverage/balance, and no
  more than 2% numerical failures.
- `ALPHA-BORDERLINE`: 60-69 `PASS-A` with adequate coverage, or at least 70
  with material coverage imbalance.
- `ALPHA-NOT-FEASIBLE`: fewer than 60 `PASS-A`, or meaningful run/checkpoint
  coverage fails.
- `ALPHA-NUMERICALLY-UNSTABLE`: numerical failures are the largest failure
  class and affect at least half the universe.
- `BLINDING_FAILURE`, `LOCAL_ARTIFACT_MISSING`, and `009-INCOMPLETE` follow the
  prompt literally and override analytical verdicts.

No support outcome, including 103/103, authorizes revealing `D_S` in this ARC.

