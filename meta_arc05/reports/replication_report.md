# Replication report

## Status

**ANCHOR-CONFIRMED.** The competence and all four preregistered replication gates
pass. This status alone was not treated as GO.

## Conditions

- `EleutherAI/pythia-410m-deduped`, 24 layers, 405,334,016 parameters.
- WikiText-2 instead of the source paper’s Pile stream (declared beforehand).
- Whole residual-block bypass, equivalent to zeroing attention and MLP updates.
- Three independently jittered text shards; 6,912 scored positions each; 20,736 total.

## Competence

| Shard | Intact NLL | Perplexity |
|---:|---:|---:|
| 11 | 3.358 | 28.74 |
| 23 | 3.404 | 30.09 |
| 37 | 3.398 | 29.90 |

All are below the preregistered NLL 4.5/perplexity 90 limit.

## Replication gate

| Shard | Middle agreement | Boundary agreement | Gap | Middle excess NLL | Boundary excess NLL |
|---:|---:|---:|---:|---:|---:|
| 11 | 0.764 | 0.600 | 0.165 | 0.191 | 1.465 |
| 23 | 0.760 | 0.593 | 0.167 | 0.185 | 1.493 |
| 37 | 0.759 | 0.589 | 0.170 | 0.199 | 1.515 |

Middle agreement exceeds 0.72 in every shard; boundary agreement is >0.03 lower;
middle deletion has smaller excess NLL. The source headline range is 72–95%, so
the middle-layer qualitative direction and magnitude replicate on a new text domain.

## Harness repairs

1. Hugging Face Xet download failed; standard HTTP retrieved the identical public
   immutable weights.
2. An initial 7,680-token run exposed that `10×256×3` missed the preregistered
   20,000-token minimum. It was discarded and rerun with 27 sequences per shard,
   without changing model, data, thresholds, seeds, or intervention.

No further repair or tuning was performed.

## Artifacts

- [`replication_aggregate.json`](../ARC-20260825-5060-001/results/replication_aggregate.json)
- [`replication_layer_profile.png`](../ARC-20260825-5060-001/figures/replication_layer_profile.png)

