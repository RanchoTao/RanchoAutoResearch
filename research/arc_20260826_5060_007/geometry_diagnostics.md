# Geometry diagnostics

## Extraction integrity

- 150 unique target cells and 300 family observations were extracted.
- Five runs and three checkpoints per run completed; all 15 intervention
  harness checks passed.
- The preregistered identity `delta_margin == delta_b` passed.
- The outcome-blind geometry calipers selected 31/103 Class A cells and passed
  the frozen support gate.

## Fatal quality-gate result

The required reproduction condition was not satisfied. The historical `topk`
extraction reproduces block `D_S` but not noise `D_S`; the `argmax` extraction
reproduces noise `D_S` but not block `D_S`. KL and NLL reproduce because they
do not depend on the top-1 anchor.

The full forensic result is in `prior_assay_invalidation.md`. Geometry values
are retained as raw provenance but were not joined to outcomes for inference.
