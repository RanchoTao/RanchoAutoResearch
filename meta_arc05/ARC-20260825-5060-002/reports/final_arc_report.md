# ARC-20260825-5060-002 — Independent-Run Stability Validation

## Decision

**PROMOTE.** The preregistered early-to-late decline in middle-layer deletion
robustness survives ten genuinely independent PolyPythias pretraining runs,
functional secondary metrics, three evaluation resamples, confidence
stratification, and an intact-NLL control. PROMOTE means the phenomenon merits
cross-family validation; it is not paper-ready and does not establish a
mechanism.

## Design

- Model scales: Pythia-70M (70,426,624 parameters, 6 blocks) and Pythia-160M
  (162,322,944 parameters, 12 blocks).
- Independent runs: combined initialization/data-order seeds 1–5 at each scale.
- Checkpoints/run: step14k, 36k, 72k, 107k, 143k.
- Primary endpoints: competent step14k versus step143k.
- Candidate layers: all blocks except first/last (70M: 1–4; 160M: 1–10).
- Fixed evaluation: three WikiText-2 resamples × 1,536 tokens/checkpoint.
- Competence gate: mean intact NLL at most 5.5; all 10 runs passed both endpoints.
- Primary metric: top-1 agreement between intact and one-block-bypassed logits.
- Secondary metrics: deleted-minus-intact NLL and
  `KL(p_intact || p_deleted)`.

## Primary result

| Scale | Runs late < early | Mean early | Mean late | Mean delta | Median delta | SD | Bootstrap 95% CI of mean |
|---|---:|---:|---:|---:|---:|---:|---:|
| 70M | 5/5 | 0.4255 | 0.2891 | -0.1363 | -0.1433 | 0.0285 | [-0.1539, -0.1103] |
| 160M | 5/5 | 0.6568 | 0.5584 | -0.0984 | -0.0903 | 0.0127 | [-0.1097, -0.0898] |

Every run also declined in all three fixed evaluation resamples. All
leave-one-run-out median deltas remained negative. A one-sided sign test for
5/5 negative directions is 1/32 per scale; this is supporting context rather
than the sole decision statistic.

### Individual run deltas

| Scale | seed1 | seed2 | seed3 | seed4 | seed5 |
|---|---:|---:|---:|---:|---:|
| 70M | -0.1433 | -0.1484 | -0.1616 | -0.1411 | -0.0873 |
| 160M | -0.0902 | -0.1041 | -0.0891 | -0.1182 | -0.0903 |

## Functional metrics

| Scale | NLL damage early → late | Runs with increase | KL early → late | Runs with increase |
|---|---:|---:|---:|---:|
| 70M | 1.2507 → 1.8552 | 5/5 | 1.1949 → 1.8261 | 5/5 |
| 160M | 0.4292 → 0.7539 | 5/5 | 0.3986 → 0.7252 | 5/5 |

The secondary metrics therefore agree with the top-1 result: later checkpoints
are functionally more damaged by bypassing one middle block.

## Confidence and competence controls

Fixed intact-confidence bins were frozen at `[0,.05), [.05,.1), [.1,.2),
[.2,.4), [.4,1.01]`. All 25 eligible run-bin comparisons at 70M and all 25 at
160M had lower late agreement. Mean bin deltas ranged from -0.07 to -0.15 at
70M and -0.09 to -0.12 at 160M.

Mean intact NLL improved 4.3652→4.3228 at 70M and 3.8935→3.7325 at 160M.
Nine of ten individual runs improved from early to late on this finite sample;
70M seed5 slightly worsened (4.3662→4.3801) while its deletion agreement still
declined by 0.0873.

In a simple checkpoint-level model, standardized progress coefficients after
controlling intact NLL were -0.0463 (70M) and -0.0350 (160M), with partial
correlations -0.906 and -0.953. A post-sweep within-run-centered robustness
check also remained negative: progress coefficients -0.144 (70M) and -0.107
(160M), partial correlations -0.922 and -0.654. This rules against the observed
trend being only a between-run NLL offset, but it does not identify a causal
mechanism.

## Layer and trajectory diagnostics

The heatmap shows declining agreement across multiple relative middle-layer
positions, rather than a single layer producing the scale average. Strict
monotonicity is not universal at 70M: seed4 rebounds from step107k to 143k and
seed5 rises from step36k to 72k. Spearman progress/agreement correlations are
-0.8 to -1.0 at 70M and -1.0 for every 160M run. This supports only a broad
early-to-late decline, not a monotone law at every checkpoint.

## Strongest negative evidence

1. The weakest endpoint effect is 70M seed5 at -0.0873, materially smaller than
   the other 70M runs.
2. Several 70M intermediate trajectories are nonmonotonic.
3. One run does not improve intact WikiText NLL from early to late.
4. Confidence control is fixed-bin conditioning, not exact token-level
   propensity matching; residual within-bin confidence shifts remain possible.
5. Both scales share the GPT-NeoX/Pythia architecture and Pile training recipe,
   so this is seed stability, not cross-family generality.
6. The combined-seed runs do not separate initialization variance from data
   order variance, despite PolyPythias making decoupled 160M variants available.

## Exact supported claim

For ten independent PolyPythias training runs (five 70M and five 160M), on
fixed WikiText-2 samples, middle-block top-1 substitutability is lower at the
competent final checkpoint than at a competent approximately 10%-progress
checkpoint. The decline is present in every run and every evaluation resample,
co-occurs with increased deleted-model NLL damage and KL divergence, and remains
within fixed intact-confidence strata and after simple intact-NLL adjustment.

## Claims not supported

- Universal monotonic decline at every training checkpoint.
- Generality outside Pythia/GPT-NeoX or outside next-token prediction.
- A decline in all forms of representational redundancy.
- Layer specialization, causal mechanism, or a pruning prescription.
- Independence of initialization and data-order effects.
- Downstream-task impact.

## Figures and artifacts

- `figures/fig1_independent_run_trajectories.png`
- `figures/fig2_delta_distribution.png`
- `figures/fig3_nll_damage.png`
- `figures/fig4_kl_divergence.png`
- `figures/fig5_confidence_matched.png`
- `figures/fig6_layer_progress_heatmap.png`
- Machine-readable summary: `results/stability_summary.json`
- Checkpoint table: `results/checkpoint_metrics.csv`
- Independent-run deltas: `results/run_deltas.csv`
- Raw provenance and hashes: `reports/provenance.md`

## Resources

- Conservative checkpoint-runtime upper bound: 3,598.7 seconds (1.00 hour),
  including model loading/download time; true active GPU time is lower.
- Peak allocated VRAM: 0.99 GiB.
- Artifact directory: 2.08 MiB.
- Observed disk-space decrease from model caching: about 13.95 GiB (current
  measured seed-repository cache footprint 14.55 GiB).
- End-to-end wall time from frozen preregistration through validated aggregate:
  about 1 hour 20 minutes including final integrity checks and reporting.
- API cost: USD 0.

## Recommended next action

**CROSS-FAMILY.** Run the same preregistered competent-early/final test on one
non-Pythia family with public checkpoints and add one downstream task on which
the intact models are competent. Do not begin mechanism claims or scale beyond
1B until cross-family survival is known.
