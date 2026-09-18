# Outcome-blind family comparison

This comparison was computed and sealed before corrected residuals or reversal
labels were joined. Differences are noise minus block. Uncertainty resamples
the five independent pretraining-run medians 100,000 times.

| Geometry quantity | Mean run median | 95% CI | Same-sign runs | Same-sign layers | Systematic? |
| --- | ---: | --- | ---: | ---: | --- |
| Boundary displacement | 0.011418 | [-0.003449, 0.022638] | 4/5 | 7/10 | No |
| Logit-norm difference | 12.535414 | [8.381783, 17.517886] | 5/5 | 7/10 | Yes |
| Absolute-cosine difference | -0.0001786 | [-0.0002075, -0.0001571] | 5/5 | 8/10 | Yes |

Thus the families do differ in output-logit geometry after KL/NLL matching,
but not consistently in the preregistered boundary-displacement quantity most
directly tied to the intact top1-vs-runner-up boundary. The systematic norm and
alignment differences justify testing the full geometry block, not a causal
claim.

Total flip rate was not included here: it is exactly the outcome `D_S`, so
using it as an explanatory predictor would be target leakage.
