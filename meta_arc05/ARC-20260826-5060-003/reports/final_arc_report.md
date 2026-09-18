# ARC-20260826-5060-003 final report

## Decision

**PROMOTE-FULL**

Candidate A passes the independent-pretraining-run stability gate. The result
is not driven by evaluation resamples, one training run, one tested interior
layer, or fixed intact-confidence composition.

## Exact question

Across independent pretraining runs, does single-middle-layer top-1
substitutability tend to decrease as language-model pretraining progresses?

## Experimental contract

- Source: genuine PolyPythias combined-seed replicas.
- Primary: nine Pythia-160M runs; seeds1-8 discovery and seed9 prospectively
  held out.
- Confirmatory scale: five existing Pythia-70M independent runs, reused from
  ARC-002 after its primary gate passed.
- Checkpoints: steps 14k, 36k, 72k, 107k, 143k, approximately normalized
  progress 0.10, 0.25, 0.50, 0.75, 1.00.
- Intervention: bypass exactly one of blocks1-10 in the 12-block 160M model.
- Corpus: same WikiText-2 cached text; fixed evaluation selections 11, 23, 37,
  each six sequences x 256 next-token positions.
- Primary statistic: intact/deleted top-1 agreement averaged over frozen
  interior layers and evaluation selections.
- Scientific replicate: independent pretraining run.

## Main run-level results

| Run | Early S | Mid S | Late S | Delta late-early | Direction |
| ---: | ---: | ---: | ---: | ---: | --- |
| 1 | 0.648980 | 0.605794 | 0.558789 | -0.090191 | negative |
| 2 | 0.660786 | 0.614670 | 0.556684 | -0.104102 | negative |
| 3 | 0.649978 | 0.607487 | 0.560872 | -0.089106 | negative |
| 4 | 0.667947 | 0.602821 | 0.549761 | -0.118186 | negative |
| 5 | 0.656120 | 0.621701 | 0.565820 | -0.090299 | negative |
| 6 | 0.658225 | 0.610525 | 0.538303 | -0.119922 | negative |
| 7 | 0.652105 | 0.599761 | 0.555729 | -0.096376 | negative |
| 8 | 0.659570 | 0.609918 | 0.554948 | -0.104622 | negative |
| 9 held out | 0.652387 | 0.602192 | 0.533442 | -0.118945 | negative |

- Negative runs: 9/9.
- Mean endpoint change: `-0.103528`.
- Median endpoint change: `-0.104102`.
- Run-level bootstrap 95% interval for the mean:
  `[-0.111495, -0.095848]`.
- All nine Spearman correlations over the five checkpoints are `-1.0`.
- All 27/27 fixed evaluation-shard endpoint changes are negative.
- All leave-one-run-out medians remain negative; range
  `[-0.104362, -0.100239]`.

## Held-out run

The seed9 prediction was frozen before model-weight download or inference:
negative endpoint sign, expected `Delta S` range
`[-0.134625, -0.063661]`, and broad non-required-to-be-monotonic decline.

Observed seed9 trajectory:

```text
0.652387 -> 0.627257 -> 0.602192 -> 0.557292 -> 0.533442
```

Observed `Delta S = -0.118945`: sign PASS and inside-range PASS.

## Competence and confidence controls

- Endpoint intact NLL range across primary runs: early 3.8302-3.9218; late
  3.6825-3.7675. All are far below the frozen NLL <=5.5 competence threshold.
- Mean intact NLL improves from 3.877665 to 3.726002 while substitutability
  declines, so failure to learn next-token prediction does not explain the
  result.
- 45/45 eligible fixed confidence run-bin changes are negative; mean
  confidence-matched change `-0.113884`.
- Pooled fixed-bin changes from lowest to highest intact confidence are:
  `[-0.115052, -0.115334, -0.123607, -0.118383, -0.097044]`.
- In the preregistered linear robustness analysis, within-run progress remains
  negative controlling intact NLL (`-0.111148` standardized coefficient;
  partial correlation `-0.6390`). This is supportive adjustment, not causal
  identification.

## Functional metrics

- Mean deleted-minus-intact NLL rises from `0.434315` to `0.773157`;
  late-minus-early NLL damage is positive in 9/9 runs.
- Mean `KL(p_intact || p_deleted)` rises from `0.402381` to `0.746438`;
  late-minus-early KL change is positive in 9/9 runs.
- Margin damage: **NOT EVALUATED**. It was optional and unavailable in the
  frozen comparable raw assay.
- Token-difficulty stratification: **NOT EVALUATED** for the same comparability
  reason.

## Layer-location robustness

- 90/90 individual run-layer endpoint changes are negative.
- 10/10 interior layers have a negative median endpoint change across runs.
- Layer-median changes range from `-0.065321` at layer1 to `-0.183811` at
  layer10. The direction is broad, but magnitude is location-dependent.

## Second scale

The reused PolyPythias-70M evidence points in the same direction:
5/5 independent runs negative, median `Delta S = -0.143338`, and run-bootstrap
95% interval `[-0.153852, -0.110297]`. It was not rerun or used to tune this
ARC's primary protocol.

## Frozen gate audit

| Gate | Result |
| --- | --- |
| >=8 competent primary runs | PASS (9) |
| >=80% negative | PASS (9/9) |
| median <= -0.05 | PASS (-0.104102) |
| run-bootstrap interval excludes zero | PASS |
| leave-one-run-out sign | PASS |
| evaluation-resample stability | PASS (9/9 runs meet 2/3; actually all 3/3) |
| NLL-damage direction | PASS (9/9) |
| KL direction | PASS (9/9) |
| fixed-confidence control | PASS (45/45 negative) |
| held-out run | PASS |
| layer-location breadth | PASS (90/90 negative) |
| confirmatory second scale | PASS (5/5 negative) |

## Figures

1. `fig1_independent_trajectories.png`: one line per 160M run; held-out seed9
   is dashed.
2. `fig2_late_minus_early_distribution.png`: all run-level endpoint changes
   relative to zero and the frozen -0.05 gate.
3. `fig3_run_level_forest.png`: diagnostic three-shard bootstrap intervals.
4. `fig4_confidence_matched.png`: early versus late within fixed intact
   confidence bins.
5. `fig5_layer_progress_heatmap.png`: layer x training-progress agreement.
6. `fig6_functional_metrics.png`: NLL damage and KL trajectories.

## Negative evidence and limitations

The strongest counterevidence is reported separately and not hidden. The main
limitations are: combined seeds do not separate initialization from data-order
variance; one evaluation corpus is used; only five public checkpoints are
sampled; fixed confidence bins are not exact propensity matching; margin and
difficulty controls are absent; and block bypass is an operational functional
intervention, not a mechanism claim.

## Resources

- New GPU checkpoint-evaluation runtime: 235.24 seconds (3.92 minutes).
- Peak allocated VRAM: 1,061,554,688 bytes (0.99 GiB).
- Gross wall clock: approximately 13 h 55 min including roughly 10 h of task
  interruptions/pauses; active execution/download wall approximately 3 h 45
  min. The <=3 h target was exceeded because the public checkpoint downloads
  repeatedly reset through the local proxy; the <=2 GPU-hour ceiling was not
  approached.
- Estimated disk added: 7,815,013,368 bytes (7.28 GiB), primarily replaceable
  Hugging Face model cache.
- API cost: USD 0.

## Exact supported claim

Across independent PolyPythias-160M pretraining runs, single-interior-layer
top-1 substitutability on the frozen WikiText-2 block-bypass assay decreases as
pretraining progresses. This direction replicates in a prospectively held-out
run, across every tested interior layer, after fixed-confidence stratification,
and at a reused 70M confirmation scale; NLL damage and KL move consistently.

This does **not** establish why substitutability declines, a universal scaling
law, continuous monotonicity, or general model fragility.

## Recommended next action

Stop validation expansion and promote Candidate A to a full project. The next
ARC should preregister one low-cost mechanism-discrimination experiment. It
should test competing causal predictions, not add another model family or
retrofit an explanation to these trajectories.

