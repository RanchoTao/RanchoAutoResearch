# Corrected baseline check

Status: **PASS**.

The Class A corrected residual was reconstructed from
`ARC-20260827-5060-006R/corrected_results.csv` as the mean of the five
run-specific cell medians.

| Run | Median corrected residual |
| ---: | ---: |
| 2 | -0.018337674 |
| 3 | -0.017216435 |
| 5 | -0.008969907 |
| 6 | -0.021556713 |
| 8 | -0.018084491 |

- Frozen value: `-0.01683304398148147`
- Reproduced value: `-0.016833043981481437`
- Absolute error: `3.469446951953614e-17`
- Required tolerance: `1e-12`

All 300 saved geometry family rows matched corrected top-1 flip rate, KL, and
NLL sources to `1e-10`; the anchored margin identity matched to `1e-8`.
Invalid mixed-rule ARC-006 outcomes were not used.
