# Paper implications

## What ARC-004 adds

ARC-003 established a replicated training-associated decline in single-block
top-1 substitutability. ARC-004 shows that this decline should not be narrated
as a generic consequence of “bigger perturbations.” Within a controlled dose
family, nearly equal local activation displacement can produce systematically
different top-1 damage when functional distributional damage differs; conversely,
substantially different displacement has no stable residual effect after KL and
NLL are matched.

## Potential result-section outline

1. **Frozen phenomenon and assay.** State the nine-run ARC-003 endpoint law and
   retain its limitations.
2. **Continuous intervention dose.** Define residual attenuation and prove its
   exact endpoints reproduce intact and deletion assays.
3. **Magnitude-matched discrimination.** Report six run-level effects, balance,
   confidence strata, absolute/relative normalization, and checkpoint breadth.
4. **Damage-matched falsification of pure magnitude.** Report pooled and >=25%
   magnitude-separated null contrasts without treating null as equivalence
   proof.
5. **Residual factors.** Report location permutation evidence and observational
   regressions as limitations, not cleanup.
6. **Boundary of the claim.** Explicitly distinguish functional-damage alignment
   from causal mediation.

## Contribution statement currently defensible

“Across independent Pythia-160M pretraining runs, the erosion of block
substitutability is better discriminated by intervention-induced predictive
damage than by raw local activation displacement, under preregistered
within-run/checkpoint matching.”

## Contribution statement not yet defensible

“Pretraining causes causal circuit specialization,” “KL mediates layer
fragility,” and “the mechanism is universal across intervention families,
corpora, architectures, or scales” are unsupported.

## Paper-killing risks

1. Functional-damage alignment may be an output-metric tautology.
2. The result may disappear for attention-only, MLP-only, swap, or random
   residual perturbations.
3. One corpus and next-token prediction may not transfer to downstream behavior.
4. Residual layer effects may undermine a one-variable mechanism story.
5. Matching is observational and cannot independently set KL.

