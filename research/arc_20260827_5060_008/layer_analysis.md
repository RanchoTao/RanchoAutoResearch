# Layer analysis

To avoid mechanically removing layer effects, this diagnostic residualized on
checkpoint plus continuous damage/output features, then compared the same
model with hidden disagreement and norm ratio added.

| Layer | Cells | Raw median | Baseline residual | Hidden-augmented residual |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 15 | 0.00210 | 0.01594 | 0.00575 |
| 2 | 15 | -0.00774 | 0.00324 | -0.00420 |
| 3 | 10 | -0.02879 | -0.01041 | -0.00454 |
| 4 | 14 | -0.03371 | -0.01225 | 0.00003 |
| 5 | 9 | -0.03139 | -0.00055 | 0.00763 |
| 6 | 8 | -0.03588 | -0.00638 | 0.00248 |
| 7 | 3 | -0.04521 | -0.02040 | -0.01802 |
| 8 | 8 | -0.01447 | -0.00356 | -0.00344 |
| 9 | 12 | -0.02398 | -0.00783 | -0.00474 |
| 10 | 9 | 0.02337 | 0.02757 | 0.01441 |

Weighted layer SD shrank 46.4%, exceeding the observational 25% threshold.
Layer 7 remains low support and is not interpreted. Because hidden direction
angle has negligible variation and calibration failed, this result most likely
reflects hidden magnitude/layer structure; it is not evidence that direction
causes layer heterogeneity.
