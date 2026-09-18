# Full project promotion

## Candidate

Layer Substitutability Dynamics

## Published anchor

The project began from published work on layer deletion/redundancy and then
moved to a narrower training-dynamics claim. This ARC did not redo the novelty
audit or claim a new mechanism.

## Pythia evidence

- 160M primary: 9 genuine combined-seed pretraining runs, five normalized
  checkpoints per run, 9/9 negative endpoint changes.
- Primary median `Delta S = -0.104102`; mean `-0.103528`; run-bootstrap 95%
  interval `[-0.111495, -0.095848]`.
- 70M confirmation reused from the prior ARC: 5/5 negative; median
  `Delta S = -0.143338`; mean-bootstrap interval
  `[-0.153852, -0.110297]`.

## SmolLM2 evidence

Prior cross-family work found a competent SmolLM2-360M trajectory with a
negative pre-WSD change and a further negative WSD-window change. The supported
cross-family claim is temporal and observational: the effect was present before
the final decay window and later decay may amplify it. This ARC does not claim
that WSD causes the change.

## Independent-run dataset

PolyPythias combined seeds1-9. These are separate pretraining runs varying
initialization and data order under a shared architecture/training recipe.

## Independent runs tested

- Primary scale: 9 at 160M.
- Confirmatory second scale: 5 at 70M, reused without rerunning.
- Total genuine training runs represented here: 14.

## Primary scale

Pythia/PolyPythias 160M, 162,322,944 parameters, 12 Transformer blocks,
interior block bypasses 1-10.

## Runs with negative Delta

9/9 primary runs; 5/5 second-scale runs.

## Median Delta

`-0.104102` at 160M.

## Aggregate CI

Run-level nonparametric bootstrap 95% interval for the mean:
`[-0.111495, -0.095848]`.

## Confidence-matched Delta

Mean across 45 eligible fixed run-bin endpoint comparisons: `-0.113884`;
45/45 negative. Highest-confidence pooled bin, the weakest bin, remains
negative at `-0.097044`.

## Functional metric summary

- Mean NLL damage rises from 0.434315 to 0.773157; late-minus-early change is
  positive in 9/9 runs.
- Mean KL rises from 0.402381 to 0.746438; late-minus-early change is positive
  in 9/9 runs.
- Margin damage: not evaluated under the frozen comparable assay.

## Strongest counterexample

No sign reversal. Seed3 is the weakest run decline (`-0.089106`). Seed7 layer1
is the weakest run-layer decline (`-0.026042`). Layer-wise magnitude is
heterogeneous, so equal specialization across layers is unsupported.

## Cross-family status

PASS, based on the earlier SmolLM2-360M trajectory and pre-WSD analysis.

## Independent-run status

PASS, including a prospectively frozen held-out run. Seed9 has
`Delta S = -0.118945`, within the predicted range
`[-0.134625, -0.063661]`.

## Current exact supported claim

Across nine independent PolyPythias-160M pretraining runs, single-interior-block
top-1 substitutability on the frozen WikiText-2 assay decreases from early to
late training; the direction survives fixed-confidence stratification, appears
at every tested interior layer/run pair, is accompanied by larger NLL damage
and KL, and points in the same direction at 70M and in prior SmolLM2 evidence.

## Unsupported claims

- All model families or scales obey a universal numeric law.
- Every layer changes equally or becomes specialized by the same mechanism.
- Learning-rate decay causes the decline.
- Confidence, NLL, optimizer geometry, or representation topology causes it.
- Block-bypass substitutability is equivalent to general model fragility.
- The phenomenon generalizes to every corpus, task, or fine-tuning regime.

## Novelty status

Not reassessed in this validation ARC. The previously locked novelty claim must
remain tied to the exact training-dynamics object and rechecked before paper
positioning.

## Largest remaining scientific question

WHY DOES SUBSTITUTABILITY DECLINE?

## Recommended next stage

MECHANISM DISCRIMINATION. Start with one preregistered experiment separating
whether the decline reflects representation drift, residual-path compensation,
or growing unique functional contribution. Do not scale model families before
a causal discriminator is designed.

