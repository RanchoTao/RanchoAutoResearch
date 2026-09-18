# Multicollinearity audit

The M2 primary design is identifiable: pooled rank/columns = `20/20`, condition
number = `13.52`, and maximum VIF = `2.81`.

| M2 predictor | VIF |
| --- | ---: |
| damage composite | 2.807 |
| intact margin | 1.033 |
| boundary displacement | 2.813 |
| family | 1.003 |

Separate KL and NLL are not identifiable as distinct effects: their correlation
is `0.997675`, with VIFs `232.87` and `239.44`. This validates the frozen
composite and prevents individual KL/NLL mechanism claims.

Important geometry correlations include:

- damage vs boundary displacement: about `-0.80`;
- logit norm vs absolute cosine: `-0.83472`;
- damage vs logit norm: about `0.56`.

Consequently, the M3 block can be assessed jointly, but individual norm versus
alignment coefficients are unstable as mechanistic explanations. M2 remains
well below the preregistered VIF 25 and condition-number 250 failure gates.
