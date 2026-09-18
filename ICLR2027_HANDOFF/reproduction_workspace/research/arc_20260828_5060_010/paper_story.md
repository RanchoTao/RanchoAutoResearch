# Recommended paper story

## 1. Phenomenon: block substitutability changes during training

Define `S` as the mean token-level agreement between the intact model's top-1
prediction and the prediction after bypassing one interior block, averaged over
the frozen layers and evaluation selections. Establish the early-to-late decline
with nine independent Pythia-160M runs, the prospective seed-9 prediction, fixed
intact-confidence bins, all tested interior locations, and the reused Pythia-70M
replication. Say “two-small-scale replication,” not “scaling law.”

## 2. Simple assay explanations are insufficient

Show that intact NLL improves while intervention NLL damage and KL grow; the
endpoint direction holds in all 45 fixed-confidence run-bin comparisons and all
90 run-layer comparisons. This rejects a pure declining-competence, confidence-
mix, or single-layer sign artifact. It does not prove a semantic or mechanistic
interpretation of `S`.

## 3. Functional damage is more informative than raw size

Use ARC-004's frozen matched contrasts. At nearly equal raw displacement
(median ratio 1.0193), the higher-functional-damage intervention has a mean
run-median top-1-damage contrast of +0.042969, with 6/6 runs positive. After
functional-damage matching, the raw-magnitude contrast is +0.002459 with a CI
crossing zero. Describe this as controlled discrimination inside the residual-
attenuation family, not as evidence that KL or NLL causes the effect.

## 4. Qualitative robustness and quantitative family structure

Introduce norm-controlled additive activation noise only after the primary
phenomenon. It reproduces the endpoint direction in 5/5 runs, but its quantitative
mapping is not interchangeable with block intervention. Explain transparently
that ARC-006 exposed inconsistent top-1 tie handling, that the mixed-rule result
was withdrawn, and that a canonical lowest-token-index exact-maximum rule was
preregistered and resealed. The corrected residual is -0.016833044, with a 95%
CI of [-0.020044850, -0.012615741] and 5/5 negative run medians.

## 5. What the residual is not yet explained by

The preregistered output-geometry block reduces the family residual by 20.18%
but leaves an adjusted residual of -0.013436. A geometry-matched subset also
retains a residual, and sign reversals remain poorly explained. ARC-008 and
ARC-009 then provide a disciplined negative ending: internal perturbation
directions could be extracted, but their causal contribution was not identifiable
under the assay, and the outcome remained blinded.

## 6. Discussion: bounded empirical contribution

The paper's contribution is a reproducible training-associated loss of
operational block substitutability, together with falsification of several
simple explanations and a corrected demonstration that equal KL/NLL damage is
not sufficient to equate intervention families. The paper does not identify the
latent causal variable. The immediate boundary conditions are WikiText-2,
small Pythia models, next-token top-1 agreement, and two interventions.
