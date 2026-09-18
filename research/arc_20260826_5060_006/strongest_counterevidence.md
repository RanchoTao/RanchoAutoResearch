# Strongest counterevidence

1. **Strict coverage did not reach 70%.** Class A was 103/150 (68.67%), although
   the preregistered gate was 70 cells and A+B reached 89.33%. The result is not
   a claim about every anchor.
2. **Cellwise sign is not invariant.** Eighteen of 103 Class A cells had a
   positive residual despite all five run medians being negative.
3. **Layer heterogeneity is substantial.** Layer 10's mean residual was
   +0.012016, whereas layer 7's was -0.048418. Layer 7 was also the weakest
   support stratum (3 Class A, 8 A+B), so its apparent extremity is uncertain.
4. **The largest Class A deviation is large.** `r8_s143000_l4` had residual
   -0.082755, showing that the aggregate is not a uniform shift.
5. **The strongest run-checkpoint stratum is localized.** Seed 6 at step 143000
   had seven Class A cells with mean residual -0.034423.
6. **Some targets remain off-manifold.** The worst target,
   `r5_s14000_l7`, was Class C with relative KL error 16.45% and relative NLL
   error 23.42%. It was retained in diagnostics and excluded only by the frozen
   primary Class A rule.
7. **The functional-damage summaries share the same output distribution as the
   outcome.** KL, NLL, and top-1 damage are not independent measurement sources;
   a shared-logit geometry confound remains possible.

The most damaging interpretation is not that the aggregate residual vanished—it
did not—but that a stable run-level offset may conceal layer-, checkpoint-, and
decision-boundary-specific structure. Figure 6 displays the strongest
predefined residual-deviation stratum without smoothing.
