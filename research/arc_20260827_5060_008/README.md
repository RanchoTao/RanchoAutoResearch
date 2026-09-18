# ARC-20260827-5060-008

Internal perturbation-direction counterfactual for corrected Candidate A.

## Status

Complete. Final verdict: `DIRECTION-NONIDENTIFIABLE`.

Stage A extracted all 103 hidden-direction cells successfully. Block-deletion
and Gaussian-noise directions are nearly orthogonal, but disagreement has too
little cross-cell variation for a useful explanatory law. Outcome-blind Stage
B calibration retained only 15/103 cells and failed frozen run/checkpoint
support gates, so held-out `D_S` was never revealed and no causal direction
claim was made.

Execution was local and offline. No downloads, APIs, package changes, external
compute, retraining, model-family expansion, or corpus change occurred.

Read `EXECUTIVE_SUMMARY.md` first; `results.json`, `direction_metrics.csv`, and
`calibration_manifest.csv` contain the machine-readable evidence.
