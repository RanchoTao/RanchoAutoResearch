# Caliper diagnostics

| strict condition | ARC-008 pass | ARC-009 pass | change |
|---|---:|---:|---:|
| KL relative difference <=15% | 30 | 97 | +67 |
| NLL relative difference <=15% | 31 | 100 | +69 |
| hidden norm ratio <=1.25 | 90 | 65 | -25 |
| output norm ratio <=1.25 | 61 | 91 | +30 |
| absolute alignment difference <=0.10 | 103 | 103 | 0 |

Continuous alpha did what the pilot suggested numerically: every frozen KL and
NLL target was bracketed, with no multiple-root or solver failure. It did not,
however, make all downstream states jointly comparable. Matching the frozen
damage targets often required different block/noise alpha magnitudes, which
increased hidden-norm imbalance.

Strict PASS-A therefore rose from 15 to 47, not to the 60-cell minimum. PASS-B
contains 27 hidden-norm-only misses and 2 output-norm-only misses; these are
reported for diagnosis but are not counted in the verdict.

