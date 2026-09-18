# Outcome-blind geometry matching

The matcher was frozen before joining corrected outcomes and exactly reproduced
the historical ARC-007 31-cell subset.

- Boundary-displacement caliper: standardized absolute difference <=0.50
- Log-norm ratio caliper: absolute value <=`log(1.25)`
- Absolute-cosine difference caliper: <=0.10
- Coverage: 31/103 = 30.10%
- Run coverage: 9, 6, 7, 4, 5 cells
- Checkpoint coverage: 13, 12, 6 cells
- Support gate: PASS

Corrected matched-subset result:

- residual: `-0.0243634`
- 90% CI: `[-0.0294922, -0.0194227]`
- 95% CI: `[-0.0300637, -0.0181858]`
- 5/5 run medians negative

Matching did not attenuate the family residual; it selected a subset with a
larger negative estimate. This is strong evidence against the tested simple
output-geometry explanation. Because matching may change the cell population,
the increase itself is descriptive rather than a causal amplification claim.
