# Experimental design

## Frozen grain

The intervention observation is run x checkpoint x evaluation selection x
layer x beta x noise-direction ID. Direction IDs and evaluation selections are
averaged before scientific comparisons. Independent pretraining run is the
only scientific-replicate grain.

## Staging

1. Initial preregistration and family selection commit.
2. Damage-support-only calibration on two excluded pilot runs.
3. Deterministic beta inclusion and second confirmatory-protocol commit.
4. Five-run offline confirmation.
5. Frozen tests A/B/C, counterevidence search, figure regeneration, and
   integrity lock.

## Anchor provenance

Exact block-deletion data are read, not recomputed, from ARC-002 for seeds
2/3/5 and ARC-003 for seeds 6/8. The selected checkpoints, tokens, tokenizer,
layers, metrics, and software version are identical. A 540-cell alpha-endpoint
audit in ARC-004 already established exact equality between its active wrapper
and retained deletion records.

## Data-quality checks

- Composite-key uniqueness at every raw and aggregated grain.
- Expected run/checkpoint/selection/layer/beta/direction coverage.
- Finite and valid probability-derived metrics.
- Exact zero-control logits and deterministic direction repeats.
- Shared intact baselines versus retained anchor files.
- Match-key integrity: same run/checkpoint/layer for Test C.
- Caliper validity, discarded-cell reasons, coverage by run/checkpoint/layer,
  common-support quartiles, and leave-one-run-out stability.
- Raw SHA-256 provenance and deterministic analysis regeneration.

## Compute estimate

Calibration is a few hundred short forwards. Confirmation uses five runs x
three checkpoints x ten layers x retained beta grid x three directions over the
frozen 4,608 tokens per checkpoint. Based on ARC-004, expected GPU-bearing wall
time is well below two hours and peak allocation below 2 GiB.

