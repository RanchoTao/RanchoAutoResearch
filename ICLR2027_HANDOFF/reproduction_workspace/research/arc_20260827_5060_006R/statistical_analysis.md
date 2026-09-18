# Statistical analysis

## Primary corrected result

Canonical rule: lowest token index among exact maximum logits, identically for
both families. The population remains the 103 frozen Class A cells.

| run_id | cells | median_residual | mean_residual |
|---|---|---|---|
| 2 | 20 | -0.018338 | -0.016992 |
| 3 | 24 | -0.017216 | -0.016017 |
| 5 | 19 | -0.008970 | -0.011860 |
| 6 | 21 | -0.021557 | -0.019686 |
| 8 | 19 | -0.018084 | -0.020731 |

- Mean of run medians: **-0.016833044**.
- 90% run-bootstrap CI: **[-0.019524016, -0.013360822]**.
- 95% run-bootstrap CI: **[-0.020044850, -0.012615741]**.
- Negative runs: **5/5**.
- Leave-one-run-out range: **[-0.018798828, -0.015652127]**.
- Frozen equivalence: **FAIL**; the 95% interval is wholly below the negative bound.
- Correction from invalid ARC-006: **+0.002401620** (12.49% of the old magnitude).

## Global-rule sensitivity

Consistent `topk`: -0.016796875, 95% CI
[-0.020782697, -0.012362558],
5/5 negative runs. The aggregate
rule difference is 0.000036169; numeric-instability gate:
**PASS**.

Class A+B canonical sensitivity: -0.018156829,
95% CI [-0.021629051,
-0.015234375].

Inference is clustered at the run level; no token/cell pseudoreplication is
used. The final verdict is **006R-RESIDUAL-CONFIRMED**.
