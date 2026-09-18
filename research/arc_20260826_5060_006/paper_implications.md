# Paper implications

## What is now supported

Candidate A remains qualitatively robust across block deletion and
norm-controlled activation noise. Functional predictive damage strongly aligns
with top-1 damage within both families, but prospective joint KL/NLL matching
leaves a reproducible family-associated offset. The most defensible result is:

> Under the frozen Pythia-160M assay, block deletion and norm-controlled
> activation noise produce near-parallel functional-damage-to-top-1-damage
> relationships with a reproducible intervention-family offset not explained by
> KL and NLL matching alone.

This updates the paper story from a possibly universal damage curve to a robust
cross-family phenomenon containing both shared functional-damage alignment and
family-specific structure.

## What is not supported

- A family-invariant quantitative mapping from KL/NLL damage to `D_S`.
- A universal law across corpora, scales, architectures, or arbitrary
  interventions.
- A causal explanation for the offset.
- A strong family-by-damage interaction; the estimated slope difference was
  small and its 95% interval crossed zero.
- Cellwise uniformity across layers or checkpoints.

## Likely reviewer attack

An ICLR reviewer should first ask whether the family offset is a mathematical
consequence of how two perturbations redistribute probability mass near the
top-1 decision boundary, rather than a deeper intervention-family mechanism.
KL and NLL summarize total predictive damage but do not identify its direction
relative to the intact top-1-versus-runner-up margin. The shared-logit origin of
all three metrics makes this the most immediate paper-killing risk.

## Possible result-section outline

1. Candidate A replicates across two intervention families.
2. Post-hoc overlap is inadequate for quantitative family comparison.
3. Blinded inverse targeting expands joint KL/NLL support from 17.3% to 68.7%
   strict and 89.3% acceptable.
4. The prospective residual remains outside equivalence with 5/5 run-level
   directional replication.
5. Damage curves are approximately parallel but shifted by family.
6. Layer/checkpoint heterogeneity and shared-logit confounding limit mechanism
   claims.
