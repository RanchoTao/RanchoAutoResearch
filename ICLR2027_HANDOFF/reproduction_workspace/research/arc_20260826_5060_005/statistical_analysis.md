# Statistical analysis

## Analysis contract

The independent unit is a pretraining run. Evaluation seeds, noise directions,
layers, and checkpoints are repeated measurements, not independent scientific
replicates. All reported confirmatory runs are retained. Run-level means or
medians receive deterministic 100,000-sample bootstrap intervals with seed
20260826. The primary family comparison uses same-run, same-checkpoint,
same-layer joint caliper matching on KL and NLL damage.

Data-quality validation passed: 4,050/4,050 raw noise rows, 450/450 aggregated
noise cells, 150/150 retained block-anchor cells, zero duplicate composite
keys, zero non-finite values, exact shared intact NLL, and 15/15 harness
validations. One of 450 noise cells met the frozen catastrophic criterion.

## Test A — sign-level replication

| run | ΔS, step143k - step14k |
| ---: | ---: |
| 2 | -0.09510 |
| 3 | -0.06829 |
| 5 | -0.05851 |
| 6 | -0.07547 |
| 8 | -0.06496 |

The direction replicated in 5/5 runs. Mean ΔS was -0.07246, median -0.06829,
with run-bootstrap 95% CI [-0.08438, -0.06304]. Removing the one catastrophic
cell preserved 5/5 negative, mean -0.07064, 95% CI [-0.07968, -0.06304]. The
weakest run was seed5 at -0.05851. All 25 eligible run x intact-confidence-bin
contrasts were negative.

## Test B — within activation noise

Magnitude-matched pairs held beta fixed while requiring a KL gap of at least
0.03. Across 196 pairs, all 5 run medians were positive. The mean run-median
high-damage minus low-damage contrast in D_S was +0.07642, 95% CI
[+0.06931, +0.08309]. This passes the frozen functional-alignment criterion.

Damage-matched pairs jointly matched KL/NLL while requiring a measured
magnitude ratio of at least 1.25. Across 54 pairs, all 5 run medians remained
positive. The mean run-median high-magnitude minus low-magnitude contrast was
+0.02624, 95% CI [+0.02472, +0.02791]. It is 34.3% of the magnitude-matched
functional contrast, exceeding the frozen 25% small-residual criterion. Thus
the preregistered claim that raw magnitude becomes negligible after damage
matching fails in this family.

## Test C — primary cross-family match

At the frozen 10% joint KL/NLL caliper, 26/150 block cells were matched (17.3%).
Matches per run were 7, 6, 2, 4, and 7. This fails the preregistered requirement
of at least 50 total, at least 5 per run, and at least 30% coverage. Within the
selected pairs, median relative gaps were 3.37% for KL and 5.18% for NLL, so
balance is locally acceptable but support is too sparse for a confirmatory
equivalence claim.

The run-median family residual D_S(noise) - D_S(block) was -0.01960, 90% CI
[-0.02476, -0.01466], 95% CI [-0.02592, -0.01404]. The frozen equivalence band
was ±0.01074; equivalence fails. The absolute residual is 45.6% of ARC-004's
+0.04297 functional contrast. Leave-one-run-out mean residuals ranged from
-0.02181 to -0.01696.

Caliper sensitivity did not rescue equivalence:

| joint relative caliper | matches | mean run-median residual | 95% CI |
| ---: | ---: | ---: | ---: |
| 5% | 9 | -0.02707 | [-0.04411, -0.00689] |
| 10% | 26 | -0.01960 | [-0.02592, -0.01404] |
| 15% | 45 | -0.01269 | [-0.01978, -0.00116] |

## Interaction and secondary regression

The preregistered standardized damage-by-family slope-difference flag was
triggered: mean run slope difference -0.05006, 95% CI [-0.13930, -0.00219],
40.8% of the pooled common slope. This estimate is fragile: seed5 had only two
cross-family matches and supplied a slope difference of -0.227, while the other
four run differences ranged from -0.0158 to +0.00036.

The secondary fixed-effects model
`D_S ~ z(KL) + z(NLL damage) + family + run + checkpoint + layer` used 52 rows,
had full design rank (19/19), condition number 43.84, and estimated a noise
family coefficient of -0.01582. Leave-one-run-out coefficients stayed negative
[-0.01847, -0.01139]. KL and NLL are collinear output-derived diagnostics, so
their individual coefficients are not interpreted causally.

## Diagnostics and interpretation

KL and NLL damage were nondecreasing in beta in 150/150 run-checkpoint-layer
groups. The zero-intervention, deterministic-repeat, and distinct-direction
harness checks passed at every checkpoint. The strongest matched stratum
deviation was seed6, step72k, layer4 at -0.04688, but this stratum contains only
one match. These results support qualitative family robustness, reject simple
cross-family equivalence under the frozen test, and leave exact family-residual
magnitude uncertain because common support is inadequate.
