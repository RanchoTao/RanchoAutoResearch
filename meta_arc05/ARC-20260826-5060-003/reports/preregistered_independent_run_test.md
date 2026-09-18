# Preregistered independent-run extension

Frozen on 2026-08-26 before generating any deletion result for combined seeds
6-9. Results for seeds 1-5 at 160M and 70M already existed and are treated as
established evidence, not prospective observations.

## Contract

- **Primary model scale:** PolyPythias/Pythia 160M (162,322,944 parameters).
- **Independent runs:** combined initialization/data-order seeds 1-8 for
  discovery/estimation; seed 9 is prospectively held out. Existing seeds 1-5
  are reused exactly, while seeds 6-9 are new to this ARC.
- **Second scale:** the already completed 70M combined seeds 1-5 are reused
  only after the earlier 160M gate has passed. They are not rerun.
- **Checkpoint rule:** nearest public checkpoints to normalized progress
  0.10, 0.25, 0.50, 0.75, and 1.00: steps 14k, 36k, 72k, 107k, and 143k.
  The rule is identical for every run and was chosen without inspecting new
  deletion results.
- **Layer subset:** every interior GPT-NeoX block, excluding only the
  structurally special first and last blocks. At 160M this is layers 1-10 of
  12. The bypass removes one block from the executed module list and directly
  connects its input to the following block, exactly matching ARC-002.
- **Evaluation corpus:** the same cached WikiText-2 train text, with fixed
  selection seeds 11, 23, and 37; six sequences of 256 next-token positions
  per resample. Evaluation resamples are not independent scientific units.
- **Primary metric:** mean token-level top-1 agreement between intact and
  single-block-deleted logits, equally averaged over the fixed evaluation
  resamples and preregistered interior layers.
- **Primary contrast:** step143000 minus step14000 within each independent
  run. Prediction: negative.
- **Secondary metrics:** deleted-minus-intact next-token NLL and
  `KL(p_intact || p_deleted)`. Predictions: positive late-minus-early changes.
  Margin damage and token-difficulty stratification are optional in the
  supplied request and are not evaluated because the frozen ARC-002 assay did
  not store deleted-logit margins or per-token label NLL. Adding them only for
  new runs would break assay comparability.
- **Competence threshold:** intact NLL <= 5.5 at both endpoint checkpoints.
  It will not be adjusted after results.
- **Confidence control:** fixed intact-confidence bins `[0,.05)`, `[.05,.1)`,
  `[.1,.2)`, `[.2,.4)`, `[.4,1.01]`; a run-bin is eligible when both endpoints
  contain at least 100 token-layer observations. PASS requires at least three
  bins, >=75% of eligible run-bin changes negative, and negative pooled mean.
- **Uncertainty:** scientific units are independent pretraining runs. The
  aggregate 95% interval is a 100,000-sample nonparametric run-level bootstrap
  of the mean contrast (seed 20260826). Per-run forest intervals resample only
  the three fixed evaluation shards and are diagnostic, not extra independent
  pretraining evidence.

## Frozen gates

Primary independent-run stability passes only when all apply:

1. At least eight competent 160M runs and at least 80% have negative primary
   contrasts (7/8 preferred; with all nine available, at least 8/9).
2. Median primary contrast is at most -0.05. This preserves the stricter gate
   frozen in ARC-002 rather than relaxing it to the request's approximate
   -0.03 threshold after observing five prior runs.
3. The run-level bootstrap 95% interval for the mean excludes zero.
4. Every leave-one-run-out median remains negative.
5. At least 80% of runs decline in at least two of three evaluation resamples.
6. At least 80% have positive late-minus-early NLL-damage and KL changes.
7. The fixed-bin confidence control passes.

Layer-location robustness passes when at least 70% of run-layer endpoint
contrasts are negative and at least 70% of interior layers have a negative
median contrast across runs. This is a breadth check, not a new primary metric.

The held-out prediction will be written after seeds 1-8 are aggregated and
before seed 9 is evaluated. Its expected numeric range is the Tukey inner fence
`[Q1 - 1.5*IQR, Q3 + 1.5*IQR]` of discovery-run primary contrasts. The held-out
sign prediction is negative. A positive held-out contrast rules out
PROMOTE-FULL; a strong reversal that also breaks the aggregate gates yields
KILL-STABILITY.

`PROMOTE-FULL` requires the primary gates, held-out negative sign, confidence
PASS, layer-location PASS, and the reused 70M second scale pointing in the same
direction. `PROMOTE-WEAK` is used when the main signal is credible but one of
those supportive requirements is weak or heterogeneous. Confidence removal
yields `KILL-CONFOUND`; inconsistent independent-run signs or outlier dominance
yields `KILL-STABILITY`; missing genuine runs yields `INCONCLUSIVE-DATA`; an
invalid intervention or evaluation yields `INVALID-HARNESS`.

## Compute ceiling

- New GPU-active time: at most two hours.
- New wall time: target at most three hours.
- Models: 160M only for new inference; no paid APIs.

