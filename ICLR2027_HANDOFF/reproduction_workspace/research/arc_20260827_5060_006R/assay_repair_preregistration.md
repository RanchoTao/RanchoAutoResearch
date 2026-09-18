# ARC-006R assay-repair preregistration

Frozen before executing `src/reseal_arc006.py`. ARC-007's approximate
post-bug diagnostic estimates are known and are not treated as confirmatory
evidence. ARC-006R independently reconstructs the corrected dataset from the
sealed source artifacts and reruns the frozen ARC-006 statistical contract.

## Frozen scientific population

- Exactly 150 ARC-006 target cells.
- Primary set: unchanged 103 Class A matches.
- Sensitivity set: unchanged 134 Class A+B matches.
- Runs: 2, 3, 5, 6, 8.
- Checkpoints: steps 14,000, 72,000, 143,000.
- Interior layers: 1 through 10.
- Frozen target KL/NLL, selected beta, alpha/targeting procedure, exclusions,
  matching classes, and tolerance rules are unchanged.
- Frozen equivalence bound: +/-0.0107421875.
- Cell residual: `D_S(noise)-D_S(block)`.
- Replicate: independent pretraining run. Cell/token rows are not treated as
  independent replicates.

The matching assignment is not recomputed because KL and NLL do not depend on
the intact top-1 identity. Any mismatch in the 150 target keys or A/B/C labels
is a fatal integrity failure.

## Canonical repair

The primary top-1 rule is: among classes whose stored/computed logit equals the
maximum exactly, select the lowest token index. Both families use the identical
path. The sealed ARC-007 `argmax` extraction implements this convention because
`torch.argmax` returns the first maximum along the vocabulary dimension.

The historical globally consistent `topk` extraction is sensitivity only. It
cannot replace the canonical estimate after results are seen.

## Source hierarchy

Level 2 offline repair is preregistered. No inference is needed:

1. ARC-006 supplies frozen target/match/KL/NLL metadata and the invalid mixed
   residual for comparison.
2. ARC-007's current sealed extraction supplies both families under the
   canonical lowest-index/`argmax` rule.
3. Git commit `1a6892b` supplies both families under the historical globally
   consistent `topk` rule.

The script must validate 300 family rows per rule, 150 unique cells, exact
metadata joins, no non-finite values, and the expected pathwise reproduction:
historical `topk` block equals ARC-006 block, while canonical `argmax` noise
equals ARC-006 noise. Source hashes are recorded before analysis.

## Frozen statistics

For Class A and A+B separately:

1. calculate each run's median cell residual;
2. average the five run medians;
3. bootstrap the five runs with replacement for 100,000 draws using seed
   20260826;
4. report 90% and 95% percentile intervals;
5. report all leave-one-run-out means.

Sign reversal uses the exact ARC-006 convention: a cell is marked reversal
when its residual sign differs from the aggregate negative sign. This includes
zero residuals; strict-positive and zero counts are also reported separately.

Layer summaries retain all Class A cells. A layer CI bootstraps run-level
medians only when at least three runs contribute; layers with fewer than eight
cells or three runs are flagged low support.

## Frozen verdict logic

`006R-RESIDUAL-CONFIRMED` requires all of:

- corrected residual magnitude at least 75% of the invalid ARC-006 magnitude;
- 95% bootstrap interval excludes zero and lies wholly below the negative
  equivalence boundary;
- 5/5 run medians are negative;
- every leave-one-run-out estimate is below the negative equivalence boundary.

`006R-RESIDUAL-WEAKENED` applies when a negative residual with a 95% interval
excluding zero remains, but any confirmation condition fails.

`006R-RESIDUAL-NOT-CONFIRMED` applies when the 95% interval includes zero or
the point/90% interval satisfies equivalence.

The two global rules are materially unstable if their aggregate estimates
differ by more than 0.0025 or imply different verdict classes. No threshold is
changed after execution.

## Resource and stop rules

Set `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`,
`HF_DATASETS_OFFLINE=1`, and `WANDB_MODE=offline`. No download, web access,
API, package change, model inference, ARC-007 geometry analysis, or external
compute is authorized. Missing local sources stop as `LOCAL_ARTIFACT_MISSING`.
