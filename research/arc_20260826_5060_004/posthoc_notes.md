# Post-result implementation notes

No scientific hypothesis, primary outcome, run, checkpoint, strength, caliper,
or decision threshold was changed after confirmatory results were revealed.

The first deterministic aggregation omitted three diagnostics that were already
explicitly required by the frozen preregistration: absolute-activation-
magnitude sensitivity, leave-one-run-out stability, and checkpoint-specific
matched summaries. The analyzer was extended to emit those prespecified
diagnostics using the original raw data and unchanged matching algorithm. It
also emits simple correlations requested in the ARC brief. These additions are
not new hypotheses and the initial primary matched results are retained.

Because the frozen Experiment-B eligibility rule permitted either a three-layer
separation or a magnitude ratio of at least 1.25, the final report also separates
those two prespecified eligibility components. This exposes whether the pooled
damage-matched contrast lacked a sufficiently large magnitude difference; it
does not change or replace the pooled primary Experiment-B statistic.

The final consistency audit found that the residual-location helper still
included both numeric progress and checkpoint indicators even though the main
regression implementation had correctly separated them. This redundant column
does not affect either matched primary analysis. It was removed before final
report lock, and the location permutation/profile was regenerated from the
checkpoint-controlled design.
