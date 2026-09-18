# Frozen main claims

Draft 0 is limited to the following five claims.

## Claim 1 — independent-run reproducibility

On the frozen WikiText-2 block-bypass assay, later competent checkpoints retain
fewer intact next-token top-1 predictions than early checkpoints across nine
independent Pythia-160M pretraining runs, including a prospectively held-out
run.

## Claim 2 — bounded replication

The endpoint direction replicates across the tested Pythia 70M and 160M scales
and across WikiText-2 and a HellaSwag-derived English evaluation stream. This is
not cross-family or large-model generalization.

## Claim 3 — raw magnitude is insufficient in the frozen assay

Within the residual-attenuation intervention family, equalized raw activation
displacement can yield different top-1 damage when predictive damage differs;
after joint KL/NLL matching, the remaining raw-magnitude contrast is much
smaller.

## Claim 4 — functional damage is informative but insufficient

KL/NLL predictive damage is more informative than raw displacement for the
within-family response, but prospective joint KL/NLL matching does not eliminate
a seed-stable difference between block bypass and norm-controlled activation
noise.

## Claim 5 — simple output geometry is incomplete

A preregistered output-logit/decision-boundary feature block is associated with
part of the corrected intervention-family residual but leaves most of it and
substantial layer heterogeneity unexplained.

## Frozen thesis

Intervention-conditioned training robustness cannot be reduced to raw
perturbation magnitude or matched output-level predictive damage alone in the
tested small-Pythia assay. The block-bypass endpoint replicates across
independent runs and two evaluation corpora; on WikiText-2, prospective KL/NLL
matching leaves a reproducible family-specific residual between block bypass
and activation noise.
