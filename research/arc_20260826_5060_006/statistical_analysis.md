# Statistical analysis

## Frozen estimand and population

The primary cellwise estimand is
`D_S(activation noise) - D_S(block deletion)` for the same run, checkpoint,
layer, evaluation corpus, and frozen assay. Negative values mean activation
noise causes fewer top-1 changes than block deletion at prospectively matched
functional damage. The confirmatory population is all 150 eligible anchors
(five runs, three checkpoints, ten interior layers); no outcome-based selection
was performed.

Primary inference uses only the 103 Class A matches. A+B (134 cells) is the
preregistered sensitivity analysis. The unit of replication is the pre-existing
training run. We summarize each run by its median cell residual, average those
five medians, and bootstrap runs. The frozen equivalence region is
[-0.0107421875, +0.0107421875].

## Match quality

| Quantity | Result |
| --- | ---: |
| Class A | 103/150 (68.67%) |
| Class A+B | 134/150 (89.33%) |
| All-target mean relative KL error | 3.89% |
| All-target mean relative NLL error | 4.17% |
| Class A mean relative KL error | 1.94% |
| Class A mean relative NLL error | 1.87% |
| Boundary solutions | 0 |

The preregistered quality gate passed every overall, run, checkpoint, layer,
harness, median-error, and reproducibility condition. Coverage was weakest at
layer 7 (3 Class A, 8 A+B), which remains a limitation rather than an exclusion.

## Primary result

| Run | Class A cells | Median residual |
| ---: | ---: | ---: |
| 2 | 20 | -0.018772 |
| 3 | 24 | -0.020833 |
| 5 | 19 | -0.008970 |
| 6 | 21 | -0.022859 |
| 8 | 19 | -0.024740 |

- Mean of run medians: **-0.019235**.
- 90% run-bootstrap CI: **[-0.022801, -0.014851]**.
- 95% run-bootstrap CI: **[-0.023206, -0.013715]**.
- Direction: **5/5 runs negative**.
- Leave-one-run-out range: **[-0.021801, -0.017858]**.
- Frozen equivalence: **failed**; the entire 95% interval is below the lower
  equivalence bound.

The A+B sensitivity result is slightly more negative: mean run median
-0.021376, 95% CI [-0.025434, -0.016529], 5/5 negative.

## ARC-005 comparison

ARC-005's post-hoc estimate was -0.019604 (95% CI
[-0.025919, -0.014041]) from only 26 strict matches. ARC-006's prospective
estimate is -0.019235. Frozen shrinkage is
`1 - abs(ARC006) / abs(ARC005) = 0.01882`, or **1.88%**. The much larger support
did not materially move the point estimate toward zero.

## Common-curve and heterogeneity checks

A frozen linear diagnostic on 206 paired family observations produced a family
offset of -0.020066. The family-by-damage coefficient was -0.003335. Across-run
slope-difference mean was -0.001689 with 95% CI [-0.006043, +0.002665], only
1.95% of the common damage coefficient. Thus the data support near-parallel
curves with a family-specific intercept, not a strong family-by-damage slope
interaction.

Heterogeneity is real. Mean residual was -0.015867 at step 14k and -0.024992 at
143k. Layer means ranged from +0.012016 (layer 10) to -0.048418 (layer 7), but
layer 7 had only three Class A cells. Eighteen of 103 Class A cells reversed the
aggregate sign. These observations constrain any claim of cellwise invariance.

## Data-quality checks

The target, reveal, and merged tables each contained exactly 150 unique keys;
there were no duplicate keys or non-finite numeric values. Recomputed reveal
KL/NLL agreed with the sealed targeting values to at most 2.22e-16 and 4.44e-16.
All 15 checkpoint harness evaluations passed. Raw hashes are recorded in the
machine-readable summary and final integrity manifest.

## Interpretation boundary

This experiment identifies a reproducible family-associated residual conditional
on two functional-damage summaries in one frozen assay. It does not prove a
biological-style mechanism, establish causality for a named latent factor, or
show that the offset generalizes to another corpus, scale, architecture, or
intervention family.
