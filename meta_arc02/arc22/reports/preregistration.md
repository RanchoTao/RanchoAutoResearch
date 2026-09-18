# ARC-22 preregistration

Written before model training.

## Question

At fixed duplicate count, total tokens, examples, capacity, initialization,
optimizer steps, and complete duplicate multiset, does temporal burstiness of
duplicate exposure change fresh-distribution generalization?

## Hypotheses

- **H0:** final fresh-validation NLL is invariant to duplicate spacing within
  seed-level variation.
- **H1:** massing all duplicate exposures into a contiguous block produces worse
  fresh-validation NLL than evenly spacing the same exposures.

## Conditions

1. `all_unique`: token-budget reference containing no intentional duplicates.
2. `duplicate_random`: the duplicate multiset randomly shuffled.
3. `duplicate_spaced`: duplicate exposures evenly distributed through training.
4. `duplicate_massed_early`.
5. `duplicate_massed_middle`.
6. `duplicate_massed_late`.

The five duplicate conditions contain exactly the same example IDs with exactly
the same multiplicities. They differ only in order. All use a constant learning
rate to prevent scheduler position from explaining an effect.

## Generators and held-out condition

- `markov`: stochastic structured token transitions.
- `recurrence4`: deterministic fourth-order modular recurrence.

The second generator is an early construction-level replication, not a post-hoc
pivot. A scheduling law must have the same direction in both.

## Model and budget controls

- One causal Transformer architecture and training budget.
- Same initialization within each seed across scheduling conditions.
- Same data multiset within each seed/generator across duplicate conditions.
- Same batch size, optimizer, constant LR, number of updates, sequence length,
  and next-token loss reduction.
- Five seeds: 11, 23, 37, 53, 71.

## Metrics

- **Primary:** fresh-distribution next-token NLL after the fixed stream.
- Secondary: fresh token accuracy, repeated-subset NLL, and memorization gap
  (`fresh NLL - repeated-subset NLL`).
- Primary contrast: mean of three massed placements minus evenly spaced NLL.
- Position control: each massed placement and their range.
- Standardized effect: paired mean difference divided by the across-seed SD of
  paired differences (reported descriptively; no threshold shopping).

## GO/KILL

**GO only if all hold:**

1. massed-minus-spaced fresh NLL is positive in at least 4/5 seeds for both
   generators;
2. the mean difference is at least 0.5 pooled within-generator seed SD for both;
3. the average massed effect remains after averaging early/middle/late, so a
   single block position cannot explain it;
4. duplicate-spaced is not itself an anomalous outlier relative to
   duplicate-random;
5. the effect is accompanied by the preregistered memorization diagnostic.

**KILL if any hold:**

- massed-minus-spaced is below 0.2 pooled SD in either generator;
- direction changes across generators;
- only one massed block position drives the result;
- the effect is not distinguishable from run-to-run noise;
- implementation/budget equality fails validation.

No second-stage natural-language model is authorized unless this gate is passed.

