# Preregistered cross-family test

Frozen 2026-08-25 before cross-family model inference.

## Preserved ARC-002 contract

- Primary quantity: token-level top-1 agreement between intact and one-block-
  bypassed next-token logits.
- Secondary quantities: deleted-minus-intact next-token NLL and
  `KL(p_intact || p_deleted)`.
- Candidate layers: all Transformer blocks except first and last (layers 1–30).
- Evaluation text: the same cached WikiText-2 source.
- Resamples: seeds 11, 23, 37; six length-256 sequences per resample.
- Confidence bins: `[0,.05), [.05,.1), [.1,.2), [.2,.4), [.4,1.01]`.
- LM competence gate: intact WikiText NLL at most 5.5 at both primary endpoints.
- Primary comparison: step2.56M minus step320k. Strict intermediate
  monotonicity is not required.

## Downstream competence gate

Before deletion inference, evaluate intact step2.56M on a fixed 256-example
sample of the official HellaSwag validation set, selected without replacement
using seed 20260825. Score only continuation tokens for all four endings.

- Primary task score: length-normalized conditional-log-likelihood accuracy.
- Secondary task score: unnormalized conditional-log-likelihood accuracy.
- PASS requires normalized accuracy >= 0.40, raw accuracy >= 0.30, at least
  three distinct predicted labels, and no label used for more than 60% of
  examples.
- Inspect tokenization on ten stored examples and require all continuations to
  contain at least one token and context+continuation to fit the 2,048-token
  limit after documented left truncation (if any).

An incompetent late model is rejected and its deletion behavior is not treated
as scientific negative evidence.

## Verdict gate

`PROMOTE` requires all of:

1. downstream and endpoint LM competence gates pass;
2. primary late-minus-early agreement delta <= -0.05;
3. all three fixed evaluation resamples have negative endpoint delta and a
   10,000-sample resample bootstrap 95% CI for the mean delta is below zero;
4. endpoint NLL-damage and KL changes are both positive;
5. at least three fixed confidence bins have >=100 token-layer observations at
   both endpoints, >=75% of eligible bins decline, and their mean delta is
   negative;
6. tokenizer/label sanity checks pass and no single intermediate checkpoint is
   substituted or removed after results are visible.

`MIXED` applies when the valid trajectory is directionally negative but fails
one or more magnitude/robustness gates. `KILL-CROSS-FAMILY` requires a valid,
competent trajectory with a flat/reversed endpoint effect supported by
uncertainty. `BLOCKED` is reserved for inability to run a valid trajectory.

