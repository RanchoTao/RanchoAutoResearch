# Recommended next ARC

## ARC-005 — Intervention-family robustness

Run exactly one prospective reviewer-control ARC asking:

> Does the magnitude-matched functional-damage discrimination transfer from
> whole-block residual attenuation to attention-only, MLP-only, and equal-local-
> magnitude random residual interventions?

Use Pythia-160M, three independent runs, the same early/middle/final
checkpoints, frozen corpus, metrics, and matching logic. Calibrate a small dose
grid for overlap, then freeze it before confirmatory contrasts. No new model
family, larger scale, or paid GPU is justified yet.

This has the highest expected information gain because failure would expose the
remaining fatal intervention-family/metric-geometry risk; success would make
the mechanism-discrimination result substantially harder to dismiss.

Do not start corpus expansion, downstream evaluation, or larger-scale
confirmation before this control.

