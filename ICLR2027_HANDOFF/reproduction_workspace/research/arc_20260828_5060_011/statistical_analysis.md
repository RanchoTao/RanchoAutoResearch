# Statistical analysis

## Analysis population and grain

The primary population is six independently pretrained Pythia-160M runs. Each
run's `S` first averages over the same 18 sampled sequences and ten interior
layers; inference tokens, layers, confidence bins, and matching cells are never
treated as independent training-run replicates.

No run was excluded. All six passed intact NLL ≤5.5 at both endpoints, contained
all three checkpoints, used identical corpus/manifest hashes, and passed every
assay harness.

## Primary endpoint

`ΔS = S_143k - S_14k`.

- 6/6 values negative.
- Mean -0.0792643; median -0.0813911; SD 0.0144614.
- 100,000-run-bootstrap 95% CI for the mean:
  [-0.0885091, -0.0676722], seed 20260828.
- Every leave-one-run-out mean is negative:
  [-0.0844705, -0.0766450].
- Every fixed evaluation resample is negative: 18/18.

These satisfy all frozen core criteria without relying on token-level standard
errors or a p-value.

## Effect ratio

The descriptive ratio is:

```text
|mean ΔS_HellaSwag| / |mean ΔS_WikiText2, nine runs| = 0.765634
```

The 95% interval [0.644852, 0.880142] independently resamples each corpus's
run-level effects. The two samples overlap in six run IDs, so this independent
bootstrap is a conservative descriptive device rather than a paired causal
test. The paired same-six point ratio is 0.733655 and is reported without a new
inferential claim.

## Matched contrasts

The ARC-004 calipers and greedy non-reuse algorithm are unchanged.

| Contrast | Pairs | Positive runs | Mean run median | 95% run-bootstrap CI |
|---|---:|---:|---:|---:|
| Magnitude matched, higher minus lower KL | 161 | 6/6 | +0.0404369 | [+0.0376338, +0.0437102] |
| KL/NLL matched, higher minus lower magnitude | 194 | 6/6 | +0.00298394 | [+0.00155527, +0.00448495] |

Independent validation found no caliper violation or within-run/checkpoint cell
reuse. The smaller contrast is statistically above zero but only 7.4% of the
larger contrast; “raw magnitude weakened, not eliminated” is the warranted
interpretation.

## Confidence control

Thirty run-bin comparisons span all five frozen bins. All are negative. The
bootstrap over six per-run mean bin effects gives
[-0.1002919, -0.0740966]. Bin observations are a robustness analysis, not 30
independent pretraining replicates.

## Validation assessment

**Ready to share with explicit scope caveats.** The methodology answers the
frozen corpus question, raw outcomes and hashes are present, headline numbers
were independently recomputed, matching balance is valid, figures show the
correct grain and zero references, and negative evidence is visible. Required
caveats are two corpora only, HellaSwag preprocessing, easier/higher-confidence
intact regime, smaller effect magnitude, and the small positive damage-matched
magnitude residual.
