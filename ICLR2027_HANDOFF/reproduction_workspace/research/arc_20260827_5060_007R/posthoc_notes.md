# Post hoc implementation notes

## 2026-08-27: numeric dtype repair before model fitting

The first corrected-outcome execution reproduced the frozen baseline, then
stopped before any model was fitted or result was written. Pandas had placed
numeric pivot columns in an `object` block because the same pivot also included
the boolean corrected-reversal label. Consequently `np.log` raised:

`TypeError: loop of ufunc does not support argument 0 of type float which has no callable log method`

The sole repair casts the already numeric pair columns to `float` immediately
after pivoting. No value, sample, metric, predictor, caliper, model, threshold,
seed, or verdict rule changed. The failed command and traceback remain in
`analysis_run.log`.

## 2026-08-27: figure-contract compliance repair

Visual inspection found that the first Figure 1 draft showed paired family
medians rather than the frozen run-bootstrap intervals, and Figure 5 showed
group means rather than cell-level distributions. The plotting function was
changed to render the already computed run-median 95% intervals in Figure 1
and cell-level jitter plus box summaries in Figure 5. This presentation-only
repair did not change data, analysis, thresholds, results, or verdict.
