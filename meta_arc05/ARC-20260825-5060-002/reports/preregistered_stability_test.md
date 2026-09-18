# Preregistered independent-run stability test

Frozen: 2026-08-25, before inspecting any ARC-002 deletion result.

## Units and models

- Independent-run unit: a PolyPythias pretraining run, not an evaluation seed.
- Scales: 70M and 160M, analyzed separately.
- Runs: `seed1` through `seed5` at each scale. PolyPythias states that these
  runs vary the combined initialization/data-order seed.
- Checkpoints: steps 14k, 36k, 72k, 107k, 143k, corresponding approximately to
  normalized progress 0.098, 0.252, 0.503, 0.748, 1.0.
- Evaluation resamples: fixed WikiText-2 train shards selected by seeds
  11, 23, and 37; six length-256 sequences per shard.

## Intervention

Bypass one Transformer block at a time by removing it from the executed
`GPTNeoXLayer` module list for that forward pass. This is the same operational
intervention used in META-ARC-05. Exclude the structurally special first and
last blocks; all remaining blocks form the preregistered middle-layer set.

## Metrics

- Primary: token-level top-1 agreement between deleted and intact logits,
  averaged equally over preregistered middle layers, tokens, and the three
  evaluation resamples.
- Secondary: deleted-minus-intact next-token NLL and
  `KL(p_intact || p_deleted)`.
- Primary comparison: step143000 minus step14000 within each pretraining run.
- Primary prediction: agreement delta is negative.
- Secondary predictions: NLL-damage and KL deltas are positive.

## Promotion gate

Both model scales must independently satisfy all of the following:

1. At least five competent independent runs, with at least 80% showing negative
   agreement delta.
2. Median agreement delta at most -0.05.
3. At least 80% of runs have positive late-minus-early NLL-damage and KL deltas.
4. At least 80% of runs decline in at least two of the three evaluation
   resamples; leave-one-run-out median deltas remain negative.
5. In fixed confidence bins `[0,.05), [.05,.1), [.1,.2), [.2,.4), [.4,1.01]`
   with at least 100 token-layer observations at both endpoints, at least 75%
   of eligible run-bin comparisons decline and the pooled matched-bin effect is
   negative. At least three bins must be eligible.

If both scales pass, functional secondary metrics agree, and the confidence
control passes, the ARC may return `PROMOTE`. Mixed/reversed independent-run
directions imply `KILL-STABILITY`; disappearance under confidence matching
implies `KILL-CONFOUND`; insufficient accessible runs/checkpoints imply
`INCONCLUSIVE`; a failed intervention/evaluation check implies
`INVALID-HARNESS`. Strict checkpoint-by-checkpoint monotonicity is secondary.

