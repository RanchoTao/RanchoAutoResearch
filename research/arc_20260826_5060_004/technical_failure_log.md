# Technical failure log

## Pre-formal harness attempt 1

- Stage: wrapper equivalence gate, before any formal ARC-004 result was saved.
- Model/run/checkpoint: Pythia-160M seed1, step14000.
- Observation: `alpha=0` exactly reproduced intact logits and the state-leakage
  repeat check passed. `alpha=1` preserved every tested top-1 prediction but
  had maximum absolute logit difference `0.0234375` versus direct module-list
  deletion, exceeding the frozen `1e-4` tolerance.
- Cause: the initial implementation reconstructed block input as
  `b(x) - (b(x)-x)` in FP16. Algebraic cancellation is not bitwise exact.
- Resolution: the `alpha=1` endpoint now directly returns the original
  `hidden_states` tensor; `alpha=0` directly returns the block output. Interior
  strengths retain the preregistered formula.
- Scientific status: this is a rejected new-wrapper implementation, not an
  error in the frozen ARC-003 module-list deletion assay. No raw/formal result
  file existed, and no hypothesis, matching rule, threshold, model, checkpoint,
  or evaluation selection was changed.

