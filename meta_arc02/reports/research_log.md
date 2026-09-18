# META-ARC-02 research log

## Iteration 0 — scope lock

Known dead directions were excluded before ideation: surprisal-guided reasoning
trace selection, circuit phase transitions with reasoning depth, neuron-versus-SAE
basis-selection laws, and fixed-budget critical-step supervision. The search is
literature-driven and restricted to cheap controlled tests.

## Iteration 1 — literature mining and triage

**Hypothesis:** recent literature contains cheap, controlled boundaries that are
not subsumed by the known failed ARC history.

**Experiment:** construct 30 source-linked wedges across six themes, reduce them
to 15 falsifiable questions, then apply novelty, Reviewer-2, feasibility, and
information-per-hour filters.

**Observed:** four candidates were direct novelty collisions, four failed the
Reviewer-2 filter, and two required too much compute. Five survived.

**Decision:** GO to MVP selection. C01 ranked first; C02 remained eligible for the
single automatic second MVP.

## Iteration 2 — ARC-22 duplicate burstiness

**Hypothesis:** at an identical duplicate multiset and update budget, massed
duplicates harm fresh generalization more than evenly spaced duplicates.

**Experiment:** 60 real tiny-Transformer runs: two exact generators, six
schedules, five seeds, with early/middle/late block controls.

**Observed:** Markov massed-minus-spaced NLL was +0.00835 but was entirely driven
by late placement. The held-out recurrence generator reversed on average
(-0.02180) and was seed-unstable.

**Decision:** KILL. The signal is schedule-position/recovery dependence, not a
generator-independent burstiness law. No pivot was justified.

## Iteration 3 — ARC-23 quotient-first state tracking

**Hypothesis:** abelianization compression predicts quotient-before-exact
learning and exact-product length failure after order and difficulty controls.

**Experiment:** 45 real runs over nine finite groups in order-12 discovery and
order-24 held-out cohorts, five seeds, online data, exact/quotient trajectories,
and depth-8/12 evaluation.

**Observed:** compression-gap rho was 1.0 in both cohorts, but compression-ID
accuracy was -0.949 and -0.975. All non-abelian groups missed the ≥95% ID gate;
gap-OOD rho was -0.095, and OOD exact accuracy was near chance for all groups.

**Decision:** INCONCLUSIVE as a scientific test and KILL as the second/final ARC.
The attractive quotient ordering is inseparable from task difficulty. No post-hoc
tuning or second pivot was allowed.

