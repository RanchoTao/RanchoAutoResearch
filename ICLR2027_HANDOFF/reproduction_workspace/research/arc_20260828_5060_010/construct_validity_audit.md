# Construct-validity audit of ΔS

## 1. What `S` measures

For a frozen evaluation selection and an intervention at one interior block,
`S` is the empirical mean of a Bernoulli indicator:

```text
S = mean_t 1[argmax p_intact(y_t | x_<t) = argmax p_intervened(y_t | x_<t)]
```

The published assay averages this agreement over frozen interior layers and
evaluation shards. `ΔS` is the later-checkpoint minus earlier-checkpoint change
under the frozen aggregation. It is therefore an operational measure of
next-token top-1 prediction substitutability under a specified intervention.

## 2. Why a reader might care

`S` asks whether an interior computation can be bypassed or perturbed without
changing the model's discrete decision. Across training, it can reveal when
otherwise competent models become less functionally substitutable at the block
level. This is relevant to robustness and modularity questions, but it is not
itself downstream accuracy, semantic equivalence, causal specialization, or a
safe-pruning criterion.

## 3. Mathematical motivation and limitation

The indicator is simple, reproducible, bounded, and directly interpretable as a
probability over sampled token positions. It also matches a metric used by the
locally stored layer-robustness reference. Its weakness is discontinuity: an
arbitrarily small logit change near a decision tie can flip the indicator,
whereas a large logit change can leave the top-1 label unchanged. The ARC-006
tie-breaking bug demonstrates that this boundary behavior is scientifically
material, not cosmetic.

## 4. Could the training trend arise mechanically?

Yes. Later checkpoints could have different logit margins, entropy, token mix,
or calibration, making the same perturbation more likely to cross an argmax
boundary. Intervention magnitude and layer mix could also change. Therefore the
assay alone cannot distinguish “more indispensable computation” from a changing
decision-boundary susceptibility.

## 5. Controls already addressing this risk

- Intact NLL improves while block-intervention NLL damage and KL increase.
- All 45 fixed intact-confidence run-bin endpoint comparisons are negative.
- All 90 run-layer endpoint contrasts are negative, ruling out one-location sign dominance.
- ARC-004 matches raw intervention magnitude and separately matches KL/NLL damage.
- ARC-005 uses a norm-controlled activation-noise family.
- ARC-006R canonicalizes exact top-1 ties and reports all corrected reversals.
- ARC-007R measures boundary displacement and broader output geometry; these
  explain only a minority of the corrected family residual.

These controls weaken several mechanical explanations but do not make `S`
semantic or causal.

## 6. Most threatening null/control metric

The strongest threat is a preregistered continuous or rank-based substitutability
metric—computed on the same intervention outputs—that shows the same apparent
training trend solely as a deterministic consequence of margin/entropy changes,
including under a semantically unstructured or random-direction perturbation.
If that null reproduced the full trajectory and family residual after damage
matching, the “block substitutability” interpretation would collapse toward a
generic output-boundary artifact.

## 7. Does the paper need stronger validation?

Yes. The manuscript must label `S` operationally and eventually triangulate it
with an alternative metric or downstream consequence. However, the immediate
highest-information experiment is cross-corpus replication: if the phenomenon
does not survive a distinct token distribution, further construct engineering
has low value. If it does, alternative-metric validation becomes a MUST-HAVE
submission step.
