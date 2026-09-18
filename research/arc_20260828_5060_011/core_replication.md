# Core ΔS replication

## Result

The cross-corpus core replication passes every preregistered criterion.
HellaSwag correct-continuation evaluation yields a mean ΔS of **-0.0792643**
with a run-bootstrap 95% CI of **[-0.0885091, -0.0676722]**. All six independent
Pythia-160M pretraining runs are negative, all 18 fixed evaluation-resample
contrasts are negative, and every leave-one-run-out mean is negative.

| Run | Stage | Early S | Late S | ΔS | Negative eval resamples |
|---:|---|---:|---:|---:|---:|
| 1 | pilot | 0.691406 | 0.638173 | -0.053234 | 3/3 |
| 4 | pilot | 0.721332 | 0.628971 | -0.092361 | 3/3 |
| 6 | confirmatory | 0.709484 | 0.630946 | -0.078537 | 3/3 |
| 7 | confirmatory | 0.715321 | 0.631076 | -0.084245 | 3/3 |
| 8 | confirmatory | 0.710417 | 0.618641 | -0.091775 | 3/3 |
| 9 | pilot | 0.712522 | 0.637088 | -0.075434 | 3/3 |

- Mean: -0.0792643
- Median: -0.0813911
- Standard deviation across runs: 0.0144614
- Leave-one-run-out mean range: [-0.0844705, -0.0766450]
- Weakest run: seed1, -0.0532335
- Most negative run: seed4, -0.0923611
- Exclusions: none
- Frozen competence gate: 6/6 pass

## Functional endpoint direction

Across runs, intact NLL improves while intervention damage increases:

- Mean intact NLL: 3.123598 early → 3.009253 late.
- Mean increase in block-bypass NLL damage: +0.249023; 6/6 positive.
- Mean increase in block-bypass KL: +0.249435; 6/6 positive.

This is consistent with Candidate A and inconsistent with declining intact
language-model fit as the explanation.

## Effect-size comparison

The absolute HellaSwag effect is 0.7656 times the stored nine-run WikiText-2
mean; independent-run bootstrap 95% CI [0.6449, 0.8801]. On the same six run IDs,
the descriptive ratio is 0.7337. The effect is therefore smaller on HellaSwag
but remains run-stable and well separated from zero. Two corpora do not support
a universal law.
