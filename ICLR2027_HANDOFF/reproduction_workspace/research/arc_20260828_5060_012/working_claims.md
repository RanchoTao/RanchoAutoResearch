# Frozen working claims

Frozen before external literature search on 2026-08-28. These are claims to
test adversarially, not assumed novelty statements.

## Operational definition

For fixed evaluation token positions `t` and an intervention `I` at one frozen
interior Transformer block,

```text
S(I, checkpoint) = mean_t 1[
  argmax p_intact(y_t | x_<t) = argmax p_I(y_t | x_<t)
]
```

The assay aggregates this top-1 agreement across the frozen interior layers and
evaluation shards. `Delta S = S(late checkpoint) - S(early checkpoint)` under
the same aggregation. It is an operational next-token block-substitutability
statistic, not downstream accuracy, semantic equivalence, safe prunability, or
a direct measure of causal specialization.

## Claim 1 — training-associated block-substitutability decline

Across nine independent Pythia-160M pretraining runs, later competent
checkpoints preserve fewer intact top-1 predictions after one interior-block
bypass than earlier competent checkpoints. A prospectively held-out run and
fixed confidence/layer controls preserve the direction.

## Claim 2 — bounded replication scope

The endpoint direction replicates at Pythia 70M and 160M and on frozen
WikiText-2 and HellaSwag-derived English evaluation streams. This is bounded
cross-scale and cross-corpus evidence inside one architecture family, not a
scaling law or universal cross-model claim.

## Claim 3 — functional damage discriminates better than raw magnitude

Within the residual-attenuation intervention family, KL/NLL predictive damage
separates top-1 damage under raw-magnitude matching more strongly than raw
perturbation magnitude separates it after KL/NLL matching. This is controlled
discrimination, not KL/NLL causality or mediation.

## Claim 4 — functionally matched interventions retain family structure

Norm-controlled activation noise reproduces the qualitative endpoint direction.
Under the canonical deterministic top-1 rule, prospective KL/NLL matching leaves
a seed-stable difference between the two tested intervention families. This
does not establish intervention-family invariance or identify its cause.

## Claim 5 — simple output geometry is incomplete

A preregistered output-logit/decision-boundary feature block explains only a
minority of the corrected family difference; an adjusted residual remains. The
internal perturbation-direction causal effect is explicitly unidentified.

## Prohibited extensions

No claim of universality, large-model scaling, KL/NLL causality, full causal
mechanism, family invariance, downstream capability loss, or internal-direction
causality is included in this audit.
