# Next ARC recommendation

## ARC-007: Decision-boundary geometry of the family residual

Run exactly one focused, no-new-family experiment on the existing frozen
Pythia-160M cells.

### Question

At matched KL/NLL damage, is the family residual explained by the direction of
the logit perturbation relative to the intact top-1-versus-runner-up decision
boundary?

### Prospective test

Before inspecting new conditional residuals, freeze a decomposition containing:

- intact top-1 margin;
- perturbation projection onto the intact top-1-minus-runner-up logit direction;
- probability mass transferred into versus outside the top-two set;
- entropy change and rank of the largest competing token.

Use the existing 150 sealed interventions and identical tokens. Fit a simple
run-blocked model that adds these frozen geometry terms to KL/NLL and family,
then repeat a prospective caliper match on KL, NLL, intact margin, and boundary
projection. The decisive result is whether the family offset enters the frozen
equivalence band without changing intervention family, corpus, scale, or model.

### Why this is highest information gain

It directly attacks the strongest remaining confound, requires no new model
downloads or training, and can distinguish an output-geometry explanation from
unidentified family structure. A null result would justify moving beyond
shared-logit explanations; a positive result would sharply narrow the paper
claim before expensive robustness work.
