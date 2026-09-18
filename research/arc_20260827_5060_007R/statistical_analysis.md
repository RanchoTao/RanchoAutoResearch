# Statistical analysis

## Design

The unit is a family observation nested in one of 103 Class A cells. Models
were fitted separately in each of five independent pretraining runs with
checkpoint and layer fixed effects. The reported family coefficient is the
mean of five run coefficients; uncertainty is a 100,000-draw run bootstrap.
KL and NLL enter as their frozen standardized composite because their observed
correlation is 0.997675.

`delta_margin` equals `delta_boundary` algebraically and is not duplicated in
the design. Flip rate equals `D_S` and is not used as a predictor.

## Nested model result

| Model | Family coefficient | 95% run-bootstrap CI | Shrinkage vs corrected R0 |
| --- | ---: | --- | ---: |
| M0 damage | -0.0170012 | [-0.0195379, -0.0141933] | -1.00% |
| M1 + intact margin | -0.0170012 | [-0.0195379, -0.0141933] | -1.00% |
| M2 + boundary displacement | -0.0170836 | [-0.0204761, -0.0138518] | -1.49% |
| M3 + logit norm + absolute alignment | -0.0134364 | [-0.0176410, -0.0092317] | 20.18% |

M2 moved only 3/5 run coefficients toward zero. Its 90% interval was
`[-0.0170257, -0.0099110]` for M3 and
`[-0.0199444, -0.0143741]` for M2; neither adjusted result has both its point
and 90% interval inside the frozen `+/-0.0107421875` band. M2 leave-one-run-out
estimates ranged from `-0.018353` to `-0.015630`.

The M3 geometry block crosses the preregistered 20% partial threshold by a
narrow margin, but its residual remains scientifically substantial. Since
logit norm and absolute alignment correlate at `-0.83472`, this result supports
only a block-level association; it does not identify either quantity as the
mechanism.

## Near-boundary stratification

Extraction-time intact-margin tertiles were retained without changing cutoffs.

| Stratum | Residual | 95% CI |
| --- | ---: | --- |
| Near / low | -0.0204864 | [-0.0237793, -0.0165805] |
| Medium | -0.0335573 | [-0.0421718, -0.0263848] |
| Far / high | 0.0001491 | [-0.0015725, 0.0018707] |

The residual is concentrated away from high-margin predictions, but it is not
monotone in distance to the boundary: the medium stratum is stronger than the
near stratum. This is evidence for a fragile-boundary regime, not for a simple
"closer is always worse" law.

## Verdict logic

Identification passed. M2 did not explain the residual; M3 supplied 20.18%
block-level shrinkage while leaving a material adjusted coefficient. The
prespecified result is therefore `GEOMETRY-PARTIAL`.
