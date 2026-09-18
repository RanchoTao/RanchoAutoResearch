# ARC-20260827-5060-008 executive summary

## Verdict

`DIRECTION-NONIDENTIFIABLE`

## Result

All 103 internal perturbation vectors were recovered locally. Block-deletion
and Gaussian-noise directions are almost exactly orthogonal across 5/5 runs,
but disagreement varies too little across cells to explain Candidate A.

Adding hidden disagreement and norm ratio to the ARC-007R output-geometry
baseline improves held-out residual RMSE by 9.63%, below the frozen 10% gate,
and improves reversal AUC by only 0.0026. Layer heterogeneity shrinks 46.4%
observationally, but this is mostly compatible with hidden magnitude structure.

The causal experiment stopped at its outcome-blind calibration gate. Only
15/103 cells jointly matched KL, NLL, hidden norm, output norm, and alignment;
run and checkpoint support requirements failed. Held-out top-1 damage was not
revealed, so there is no direction-swap effect to report.

## Direct answers

1. Families differ in direction: yes, they are nearly orthogonal.
2. More explanation than output geometry: no material held-out improvement.
3. Sign reversals explained: no incremental discrimination.
4. Layer heterogeneity: observationally reduced, not causally identified.
5. Independent manipulation feasible: not with the frozen calibration design.
6. Direction-swap effect: not measured after the support failure.
7. Effect relative to `-0.016833`: undefined.
8. Unexplained: aggregate residual, reversals, and causal layer structure.
9. Safe claim: the assay exposes distinct directions but cannot isolate their
   effect from functional damage.
10. Overclaim: that internal direction causes Candidate A.
11. Next experiment: blinded continuous alpha root-finding feasibility only.

No subsequent ARC was started.
