# Outcome-blind calibration diagnostics

Calibration used only seed 11, two sequences per cell, the frozen alpha grid,
KL/NLL, hidden relative norm, output-logit norm, and boundary alignment. Top-1
flip outcomes were neither computed nor stored.

## Frozen-caliper coverage

| Gate | Cells passing |
| --- | ---: |
| KL balance | 30/103 |
| NLL balance | 31/103 |
| Hidden-norm ratio | 90/103 |
| Output-logit-norm ratio | 61/103 |
| Absolute-cosine balance | 103/103 |
| All gates | 15/103 |

Support by run was `2,5,2,4,2`; support by checkpoint was `3,9,3`. Required
support was at least 30 total, three per run, and five per checkpoint. All three
requirements fail.

Across all selected best pairs, median block/noise imbalance was 29.7% for KL
and 32.0% for NLL, versus frozen 15% calipers. Median hidden-norm ratio was
approximately 1.00, while median output-norm ratio was 1.172. Alignment was not
the blocker.

The dominant failure is therefore inability to hold downstream functional
damage fixed while changing direction, not inability to match injected norm.
No caliper was relaxed and held-out `D_S` was not revealed.
