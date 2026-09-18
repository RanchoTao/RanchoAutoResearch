# Stage A analysis

## Outcome-blind characterization

All 103 frozen Class A cells were extracted at the original block-output
residual-stream site. Every token-direction comparison passed the nonzero-norm
gate.

- Mean block-noise cosine: `-0.0000431`
- Mean directional disagreement: `1.0000431`
- Run-bootstrap 95% CI for run-median disagreement:
  `[0.9999838, 1.0000875]`
- Runs above the 0.75 distinctness threshold: 5/5
- Cross-cell disagreement SD: `0.0002897`
- Frozen usable-variation threshold: `0.002`

The directions are therefore robustly distinct—essentially orthogonal—but
directional disagreement is almost constant across cells. This is expected for
a high-dimensional frozen Gaussian direction compared with a learned block
update. Distinctness supports attempting a controlled intervention; it does not
by itself explain Candidate A.

## Outcome-linked Stage A2

Adding hidden disagreement and hidden norm ratio to the frozen output-geometry
baseline reduced leave-one-run-out RMSE from `0.0133294` to `0.0120453`, a
`9.63%` reduction, just below the preregistered 10% materiality threshold.
Directional disagreement alone correlated only `0.183` with the corrected
cell residual; hidden norm ratio correlated `0.470`.

The observational signal is consequently dominated by relative magnitude, not
by variation in direction angle. It is not causal evidence.
