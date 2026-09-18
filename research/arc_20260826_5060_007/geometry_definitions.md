# Geometry definitions

For every token, let intact logits be `z`, intact top-1 and runner-up classes be
`c1` and `c2`, and intervened logits be `z'`.

## Primary

- `intact_margin = z[c1]-z[c2]`.
- `perturbed_anchored_margin = z'[c1]-z'[c2]`.
- `delta_margin = perturbed_anchored_margin-intact_margin`.
- `delta_b = (z'[c1]-z[c1])-(z'[c2]-z[c2])`.
- `flipped = argmax(z') != c1`.
- `flip_to_intact_top2 = argmax(z') == c2`.
- `other_flip = flipped and not flip_to_intact_top2`.

`delta_margin` and `delta_b` must agree numerically and are one scientific
quantity, not two degrees of freedom. Total flip rate equals frozen `D_S` and
is not an explanatory covariate.

## Secondary

- `logit_delta_norm = ||z'-z||_2`.
- `cosine_alignment = delta_b/(sqrt(2)*logit_delta_norm)`.
- `projection_fraction = abs(cosine_alignment)`.
- `top1_to_top2_rate = mean(flip_to_intact_top2)`.

All margins use logits, not probabilities. No metric is normalized by `D_S`.
Noise values average directions 101, 202, and 303 after token-level
calculation. Block deletion uses the same original-token anchors.

