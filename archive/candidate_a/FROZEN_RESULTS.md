# Candidate A frozen results

This file is a human-readable projection of the canonical manuscript ledger at
`manuscript/numerical_provenance.csv`. All intervals are bootstrap intervals at
the level reported by the source ARC. Values from the invalid ARC-006 outcome
analysis are intentionally absent. Byte-identical snapshots of the table's
major JSON/CSV sources are preserved under `evidence/`; the original canonical
ARC directories are shown below so the full provenance chain remains explicit.

| Result | Frozen value | Canonical source |
| --- | --- | --- |
| Primary Pythia-160M `Delta S` | 9/9 negative; mean `-0.103527681`; median `-0.104101563`; 95% CI `[-0.111494502, -0.095847620]` | `meta_arc05/ARC-20260826-5060-003/results/independent_run_summary.json`; run rows in `results/run_level_results.csv` |
| Prospectively held-out seed 9 | `Delta S=-0.118945313`; frozen prediction interval `[-0.134625, -0.063661]` | `meta_arc05/ARC-20260826-5060-003/reports/heldout_run_prediction.md` |
| WikiText-2 confidence control | 45/45 eligible run-bin changes negative; mean `-0.113884` | `meta_arc05/ARC-20260826-5060-003/results/independent_run_summary.json` |
| Layer breadth | 90/90 run-layer endpoint changes negative; 10/10 layer medians negative | `meta_arc05/ARC-20260826-5060-003/results/layer_endpoint_deltas.csv` |
| Pythia-70M replication | 5/5 negative; median `Delta S=-0.143338`; 95% CI `[-0.153852, -0.110297]` | `meta_arc05/ARC-20260826-5060-003/results/independent_run_summary.json` |
| HellaSwag-derived replication | 6/6 negative; mean `Delta S=-0.079264`; 95% CI `[-0.088509, -0.067672]` | `research/arc_20260828_5060_011/results/cross_corpus_summary.json`; run rows in `processed/core_run_results.csv` |
| HellaSwag confidence control | 30/30 negative; mean `-0.089488`; 95% CI `[-0.100292, -0.074097]` | `research/arc_20260828_5060_011/results/cross_corpus_summary.json` |
| Absolute HellaSwag/WikiText effect ratio | `0.765634`; 95% CI `[0.644852, 0.880142]` | `research/arc_20260828_5060_011/results/cross_corpus_summary.json` |
| Magnitude-matched functional-damage contrast | 185 pairs; mean run-median `+0.04296875`; 95% CI `[0.0353733, 0.0524631]`; 6/6 positive | `research/arc_20260826_5060_004/results/mechanism_summary.json` |
| Damage-matched raw-magnitude contrast | 162 pairs; mean run-median `+0.002459`; 95% CI `[-0.000904, 0.005751]` | `research/arc_20260826_5060_004/results/mechanism_summary.json` |
| Activation-noise endpoint | 5/5 negative; mean `Delta S=-0.0724648`; 95% CI `[-0.0843764, -0.0630449]` | `research/arc_20260826_5060_005/results/family_robustness_summary.json` |
| Prospective matching support | 103/150 strict Class A (`68.67%`); 134/150 A+B (`89.33%`); Class A mean relative KL/NLL errors `1.94%`/`1.87%` | `research/arc_20260826_5060_006/match_diagnostics/targeting_quality.json` |
| Corrected family residual | `-0.016833044`; 95% CI `[-0.020044850, -0.012615741]`; 5/5 run medians negative | `research/arc_20260827_5060_006R/results/corrected_summary.json` |
| Frozen equivalence half-width | `0.010742188` | `research/arc_20260827_5060_006R/results/corrected_summary.json` |
| Assay repair effect | `+0.002401620`, or `12.49%` of the withdrawn estimate's magnitude | `research/arc_20260827_5060_006R/results/corrected_summary.json` |
| Corrected sign reversals | 24/103 strict matched cells | `research/arc_20260827_5060_006R/results/corrected_summary.json`; rows in `corrected_results.csv` |
| Full output-geometry shrinkage | `20.18%` | `research/arc_20260827_5060_007R/results/geometry_summary.json` |
| Geometry-adjusted family residual | `-0.0134364`; 95% CI `[-0.0176410, -0.0092317]` | `research/arc_20260827_5060_007R/results/geometry_summary.json` |
| Geometry-matched sensitivity | 31/103 cells; residual `-0.0243634`; 95% CI `[-0.0300637, -0.0181858]` | `research/arc_20260827_5060_007R/results/geometry_summary.json` |

## Non-claim results retained as boundaries

- ARC-008 observational direction features reduce held-out residual RMSE by
  `9.63%` and change reversal AUC by `0.0026`; both miss the frozen explanatory
  gates. Its counterfactual calibration supports only 15/103 cells, so no
  causal outcome is revealed.
- ARC-009 reaches 47/103 PASS-A and 29/103 PASS-B cells but fails the frozen
  feasibility rule; no `D_S` is revealed.

These boundary values are `EXPLORATORY` or `INCONCLUSIVE` and cannot support a
positive internal-mechanism claim.
