# ARC-20260828-5060-010 — Executive summary

## Final verdict: PAPER-BORDERLINE

A coherent empirical paper core exists, but **cross-corpus robustness is the one
major scientific gap that must be resolved before serious manuscript drafting**.
All headline evidence uses the same frozen WikiText-2 source. The exact next
experiment is a preregistered, frozen-contract Pythia-160M replication on one
distinct evaluation corpus. It was selected but not executed.

`AUTODL NOT JUSTIFIED YET`

## What is already defensible

- Nine independent Pythia-160M runs show an early-to-late decline in block-bypass
  top-1 substitutability: mean ΔS -0.103528, 95% CI
  [-0.111495, -0.095848], 9/9 negative.
- A prospectively held-out run passed its frozen prediction; all 45 fixed-
  confidence run-bin and all 90 run-layer endpoint comparisons are negative.
- Five Pythia-70M runs reproduce the direction. This is two-small-scale
  replication, not a scaling law.
- Under residual attenuation, magnitude-matched interventions retain a strong
  functional-damage contrast, while the damage-matched raw-magnitude contrast is
  near zero. This supports discrimination, not KL/NLL causality.
- Norm-controlled activation noise reproduces the qualitative direction in 5/5
  runs. With canonical tie handling, a KL/NLL-matched family residual remains
  (-0.016833; 95% CI [-0.020045, -0.012616]; 5/5 negative).
- Simple output geometry removes only 20.18% of that residual. Internal-direction
  causality remains unidentified because the preregistered support gate failed
  and D_S was never revealed.

## What changed during evidence audit

ARC-006's mixed `topk`/`argmax` estimate is invalid and must never be reused.
ARC-006R's deterministic lowest-token-index exact-maximum rule is canonical.
The offline audit recomputed the paper-critical summaries, verified every
available integrity seal, and produced 18 ledger rows: 8 `VALID`, 5
`INVALIDATED`, 3 `INCONCLUSIVE`, and 2 `EXPLORATORY`.

## Recommended thesis

> During small-Pythia pretraining, interior-block top-1 substitutability declines
> reproducibly even as intact language-model fit improves. Predictive damage
> discriminates this decline better than raw perturbation size within the
> original intervention family, yet matching KL and NLL leaves stable
> intervention-family structure that simple output geometry does not explain.

This must be scoped to the frozen assay, WikiText-2, small Pythia models, and two
intervention families. It does not establish universal layer specialization,
downstream fragility, KL/NLL causality, or an internal mechanism.

## Paper-readiness blockers

1. **Scientific experiment:** cross-corpus robustness is absent and is the one
   selected next ARC.
2. **Nonexperimental gate:** local literature coverage is insufficient for a
   defensible novelty claim; execute `literature_search_needed.md` later with
   primary sources.
3. **Submission engineering:** add alternative-metric construct triangulation
   and a unified environment/reproduction entry point after the corpus gate.

## Stop decision

Do not scale, start a third intervention family, or reopen internal-direction
calibration. Await explicit approval for the cross-corpus ARC. If that experiment
fails, narrow or stop the current paper rather than adding mechanisms.
