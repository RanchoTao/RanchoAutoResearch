# Statistical analysis

## Confirmatory ARC-007 analysis

Not run. Both attempts stopped at the preregistered outcome-reproduction gate,
before fitting M0 or any geometry-conditioned model.

## Post-stop invalidation diagnostic

The diagnostic uses the unchanged 103 Class A cells. For each top-1 rule it
computes cell residuals, then run medians, then their mean. Uncertainty is a
100,000-draw bootstrap over the five independent pretraining runs with seed
20260826. The frozen equivalence bound is +/-0.0107421875.

Results are in `results/prior_assay_invalidation.json` and
`processed/top1_consistency_diagnostic.csv`. These numbers establish that the
bug is material and that a repaired assay is plausible; they do not test any
ARC-007 geometry hypothesis.
