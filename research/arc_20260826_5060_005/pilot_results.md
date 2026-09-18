# Calibration results

Calibration was used only for damage-support feasibility. No agreement value,
`D_S`, `Delta S`, or checkpoint-direction contrast was printed, saved in this
summary, or inspected before the confirmatory protocol freeze.

## Harness

All four run/checkpoint calibration records passed exact zero-control,
deterministic-repeat, and distinct-direction checks. Peak allocated CUDA memory
was 1.062 GiB or lower.

## Damage support

| Beta | Median measured relative magnitude | Median KL | Median NLL damage | Joint anchor support | Catastrophic cells | Decision |
| ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 0.05 | 0.05000 | 0.00811 | 0.00555 | 0% | 0/16 | Exclude: damage too low |
| 0.10 | 0.10000 | 0.02354 | 0.02078 | 0% | 0/16 | Exclude: damage too low |
| 0.20 | 0.20000 | 0.08269 | 0.08345 | 0% | 0/16 | Exclude: damage too low |
| **0.35** | **0.35000** | **0.21744** | **0.22389** | **50%** | **0/16** | **Retain: exact low-damage matches** |
| **0.50** | **0.50000** | **0.41228** | **0.42827** | **100%** | **0/16** | **Retain: missing middle quartile** |
| **0.75** | **0.75000** | **0.96422** | **0.97523** | **75%** | **0/16** | **Retain: exact high-damage matches** |
| 1.00 | 1.00000 | 1.62702 | 1.71413 | 12.5% | 0/16 | Exclude: insufficient common support |
| 1.50 | 1.50000 | 2.99406 | 3.10572 | 0% | 12/16 | Exclude: catastrophic/support failure |

Retained grid: `[0.35, 0.50, 0.75]`. It covers all four anchor KL quartiles.
The calibration feasibility gate passes.

The first calibration analyzer omitted the preregistered quartile-coverage
alternative for beta 0.50; `technical_failure_log.md` records the pre-
confirmatory correction. No hypothesis outcome was unsealed.

