# Competence gate (frozen before ARC-002 deletion results)

## Gate

A preregistered checkpoint is competent only if its intact-model mean
validation NLL on the three fixed WikiText-2 shards is **at most 5.5** and every
shard has finite NLL. Each shard contains 1,536 next-token positions, for 4,608
positions per checkpoint.

The primary early checkpoint is step 14,000 (about 9.8% of the 143,000-step
trajectory). A run is excluded from the primary early/late comparison if this
specific early checkpoint fails the gate; a later checkpoint will not be
silently substituted. Step 143,000 must also pass. Exclusions and their intact
NLL are reported.

## Rationale

NLL 5.5 corresponds to perplexity about 245 and excludes initialization-like or
grossly nonfunctional language models while retaining deliberately early but
meaningful checkpoints. The threshold is fixed without inspecting ARC-002
layer-deletion outputs. It is not tuned per scale or seed.

