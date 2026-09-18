# ARC-23 preregistration

Written before training.

## Question

Is the parity-associative shortcut observed in permutation state tracking one
instance of a broader tendency to learn a group's cheap abelian quotient before
its exact product?

## H0 / H1

- **H0:** after controlling group order and final ID accuracy, abelianization
  compression `|G| / |G/[G,G]|` does not predict quotient-first learning or OOD
  length accuracy.
- **H1:** larger compression produces a larger quotient-before-exact learning gap,
  which predicts worse exact-product length extrapolation.

## Groups

Discovery cohort, order 12: `C12`, `C6xC2`, `D6`, `A4`.

Held-out construction cohort, order 24: `C24`, `C12xC2`, `Q8xC3`, `D12`, `S4`.

The commutator subgroup and quotient cosets are computed from each exact Cayley
table rather than hand-labelled.

## Training and metrics

- Opaque group-element tokens; predict the exact product of a random sequence.
- Train online on depths 2–4; test depth 4 (ID) and depths 8/12 (OOD).
- Same architecture, batches, update count, and initialization within each
  group-order/seed comparison.
- Five seeds.
- At fixed checkpoints, compute exact accuracy and quotient accuracy by summing
  output probabilities over exact elements in each quotient coset.
- Primary mechanism metric: checkpoint AUC of `quotient accuracy - exact accuracy`
  at ID depth 4.
- Primary behavioral metric: mean exact accuracy at depths 8 and 12.

## Controls

1. within-order comparisons prevent vocabulary/output size from explaining the
   ordering;
2. all groups must exceed 95% final ID exact accuracy;
3. the order-24 cohort is held out from hypothesis selection;
4. quotient labels are an independent algebraic calculation from the group table;
5. online data removes finite-dataset memorization/grokking as the explanation.

## GO/KILL

**GO only if:** all groups reach ≥95% ID exact accuracy; compression versus
quotient-gap Spearman rho is ≥0.7 in order 12 and has the same positive ordering
in held-out order 24; quotient-gap versus OOD exact accuracy is ≤-0.7 overall;
and the direction holds in ≥4/5 seeds.

**KILL if:** ID control passes but either relationship is weak/reversed in a
cohort, seed directions are inconsistent, or abelian groups show an equivalent
gap. If ID control fails for multiple groups, mark INCONCLUSIVE rather than tune
until success.

No causal probing or full permutation task follows unless this gate passes.

