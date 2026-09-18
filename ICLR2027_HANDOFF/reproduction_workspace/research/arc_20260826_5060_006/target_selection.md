# Target selection

## Confirmatory set

Use all 150 retained block-deletion cells: seeds 2/3/5/6/8, checkpoints
14k/72k/143k, and interior layers 1-10. Selection is systematic and does not
consult any ARC-006 activation-noise result. Sanitized targeting inputs retain
only target ID, run, checkpoint, layer, progress, target KL, and target NLL
damage.

## Pilot set

Use 16 disjoint cells: seeds 1/4, checkpoints 14k/143k, layers 2/5/8/10. Pilot
results cannot enter confirmation or the final scientific interval.

## Grain and key

The unique target key is `(run_id, step, layer)`. Anchor metrics average the
same three evaluation selections. The final manifest must have exactly one
targeting decision per key, including explicit Class C/failure records.

