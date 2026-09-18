# Numerical results and provenance

The value-by-value canonical ledger is `paper/current/numerical_provenance.csv`. All intervals below are the bootstrap intervals reported by the source ARC. No number is supplied from conversational memory alone.

| Result | Value | Package-local source |
| --- | --- | --- |
| Pythia-160M block bypass | 9/9 negative; mean `Delta S=-0.103527681`; median `-0.104101563`; 95% CI `[-0.111494502,-0.095847620]` | `results/ARC-003/results/independent_run_summary.json`; rows in `run_level_results.csv` |
| Held-out seed 9 | `Delta S=-0.118945313`; prediction interval `[-0.134625,-0.063661]` | `logs/arc_records/ARC-003/reports/heldout_run_prediction.md` |
| WikiText confidence control | 45/45 negative; mean `-0.113884` | `results/ARC-003/results/independent_run_summary.json` |
| Layer breadth | 90/90 run-layer endpoint changes negative; 10/10 layer medians negative | `results/ARC-003/results/layer_endpoint_deltas.csv` |
| Pythia-70M replication | 5/5 negative; median `Delta S=-0.143338`; 95% CI `[-0.153852,-0.110297]` | `results/ARC-003/results/independent_run_summary.json` |
| HellaSwag-derived endpoint | 6/6 negative; mean `Delta S=-0.079264`; 95% CI `[-0.088509,-0.067672]` | `results/ARC-011/results/cross_corpus_summary.json` |
| HellaSwag confidence control | 30/30 negative; mean `-0.089488`; 95% CI `[-0.100292,-0.074097]` | same JSON |
| Absolute HellaSwag/WikiText effect ratio | `0.765634`; 95% CI `[0.644852,0.880142]` | same JSON |
| Magnitude-matched functional-damage contrast | 185 pairs; mean run-median `+0.04296875`; 95% CI `[0.0353733,0.0524631]`; 6/6 positive | `results/ARC-004/results/mechanism_summary.json` |
| Damage-matched raw-magnitude contrast | 162 pairs; mean run-median `+0.002459`; 95% CI `[-0.000904,0.005751]` | same JSON |
| Activation-noise endpoint | 5/5 negative; mean `Delta S=-0.0724648`; 95% CI `[-0.0843764,-0.0630449]` | `results/ARC-005/results/family_robustness_summary.json` |
| Prospective matching support | 103/150 strict Class A (`68.67%`); 134/150 A+B (`89.33%`); Class A KL/NLL relative errors `1.94%/1.87%` | `results/ARC-006-INVALIDATED/match_diagnostics/targeting_quality.json` (matching only) |
| Corrected family residual | `-0.016833044`; 95% CI `[-0.020044850,-0.012615741]`; 5/5 negative run medians | `results/ARC-006R/results/corrected_summary.json` |
| Equivalence half-width | `0.010742188` | same JSON |
| Tie-repair point-estimate change | `+0.002401620`, `12.49%` of withdrawn estimate magnitude | same JSON |
| Corrected sign reversals | 24/103 (`23.3%`) strict matched cells | same JSON and `results/ARC-006R/root/corrected_results.csv` |
| Geometry shrinkage | `20.18%` | `results/ARC-007R/results/geometry_summary.json` |
| Geometry-adjusted residual | `-0.0134364`; 95% CI `[-0.0176410,-0.0092317]` | same JSON |
| Geometry-matched sensitivity | 31/103 cells; residual `-0.0243634`; 95% CI `[-0.0300637,-0.0181858]` | same JSON |
| Direction observational boundary | held-out RMSE reduction `9.63%`; reversal AUC gain `0.0026`; both miss gates | `results/ARC-008/root/results.json` |
| ARC-008 counterfactual support | 15/103 cells; top-1 outcome not revealed | `results/ARC-008/root/calibration_summary.json` |
| Continuous-alpha support | PASS-A 47/103; PASS-B 29/103; no `D_S` reveal | `results/ARC-009/root/feasibility_summary.json` |

## Interpretation of the reported “1.68%”

`-0.016833044` is an **absolute difference in top-1 damage**, averaged as the frozen run-level family residual `D_S(noise)-D_S(block)`. It is approximately `-1.68` percentage points. It is not a relative percent improvement, not a horizontal-axis distance, not KL, and not NLL.

## Training stage and layer observations

- The main replication uses early/middle/late trajectory checkpoints and finds negative run-level Spearman correlations across the five selected checkpoints, but the paper does not claim a universal continuous or phase-transition law.
- Layer-location direction is broad in ARC-003, but magnitude is heterogeneous. In corrected cross-family cells, weighted layer-mean standard deviation is `0.017455`; layer 7 has low strict support.
- The cross-corpus effect is about 76.6% of the absolute WikiText mean, so corpus magnitude invariance is rejected.

## Statistical unit and significance

All headline confidence intervals bootstrap independent pretraining-run summaries. Tokens, layers, pairs, checkpoints, and evaluation shards are not counted as independent experimental replicates. The package preserves per-run/per-cell rows for independent recalculation. No claim should be upgraded solely because a cell-level sample is large.

## Invalidated values

Original ARC-006 top-1 outcomes and any residual derived from them are invalid. They are preserved under `results/ARC-006-INVALIDATED/` only to show what failed. Use ARC-006R for every corrected outcome number.
