# Targeting method

The new-family strength is selected prospectively from KL and NLL damage only.
For each target, a deterministic grid plus bounded golden-section refinement
minimizes the preregistered joint normalized-error objective. Directions,
evaluation selections, tokens, model, and target location match ARC-005.

The method is deliberately one-dimensional and non-adaptive across targets.
It tests whether the two intervention families share a sufficiently similar
KL/NLL damage manifold; it does not force an exact two-dimensional solution
when one scalar degree of freedom is insufficient.

No surrogate model, Bayesian optimization, outcome metric, or post-reveal
retargeting is permitted.

