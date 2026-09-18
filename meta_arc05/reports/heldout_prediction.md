# Held-out prediction — written before Pythia-70M evaluation

## Condition

New model scale: `EleutherAI/pythia-70m-deduped`, never used in anchor replication
or boundary discovery. Compare immutable checkpoints `step1000` and `step143000`
on the same three text-shard seeds. This model has fewer layers than both discovery
and replication models.

## Prediction

If continued pretraining specializes individual residual blocks, deletion of a
middle block at step143000 will preserve fewer intact top-1 predictions than at
step1000, even though intact language-model NLL improves.

## Expected sign

`agreement(step143000) - agreement(step1000) < 0` in all three shards.

## Expected magnitude/range

- Mean decline: **0.05 to 0.20**.
- Predefined PASS: decline ≥0.05 in every shard, and later agreement is lower in
  at least three populated baseline-confidence bins with ≥100 pooled layer-token
  observations per checkpoint.
- Final-checkpoint intact NLL must be ≤4.5; otherwise the held-out model is not a
  competent LM for this test.

Failure yields `KILL-GENERALIZATION` (or `INVALID-HARNESS` if competence fails),
not a post-hoc change of scale/checkpoint.

