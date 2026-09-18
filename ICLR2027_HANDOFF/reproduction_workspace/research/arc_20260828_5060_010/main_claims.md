# Paper-ready main claims

## Claim 1 — replicated training-associated decline

Across nine independent Pythia-160M pretraining runs on the frozen WikiText-2
assay, later checkpoints preserve fewer intact top-1 predictions after one
interior-block bypass (mean ΔS -0.103528; run-bootstrap 95% CI
[-0.111495, -0.095848]; 9/9 negative). A prospectively held-out run reproduced
the sign and its magnitude fell inside the frozen prediction interval.

## Claim 2 — bounded robustness

The endpoint direction holds across every tested run-layer pair, all eligible
fixed intact-confidence bins, and five independent Pythia-70M runs. This is
two-small-scale replication inside one architecture family and one corpus, not
a universal scaling law.

## Claim 3 — functional damage versus raw magnitude

Within residual attenuation, predictive-distribution damage separates top-1
damage under magnitude matching more strongly than raw displacement separates
it under KL/NLL matching. This is controlled discrimination and does not
establish KL/NLL causality.

## Claim 4 — cross-intervention result with a corrected assay

Norm-controlled additive activation noise reproduces the qualitative early-to-
late decline in 5/5 runs. Under a corrected deterministic top-1 rule, matching
KL and NLL does not eliminate a seed-stable family residual (-0.016833; 95% CI
[-0.020045, -0.012616]).

## Claim 5 — simple geometry is insufficient; mechanism remains open

A preregistered output-geometry block explains a modest fraction (20.18%) of the
corrected family residual, while the adjusted residual remains. The causal
contribution of internal perturbation direction is not identifiable under the
current assay.
