# Pilot diagnostics

The outcome-blind pilot reused the ARC-008 six-point calibration response
curves for 10 fixed cells spanning all five runs, all three checkpoints, and
multiple layers. It did not open any result or residual file.

All 20 block/noise curves were finite. KL was nondecreasing in alpha for 20/20
curves and NLL damage was nondecreasing for 20/20. Each frozen KL target and
each frozen NLL target was bracketed by the existing ARC-008 alpha range.
Neither metric showed multiple discrete target crossings.

This supports a bracketed bisection primary solver. Because the two damage
targets and the pairwise geometry conditions need not share the same alpha,
the frozen fallback is an exact, bounded high-resolution coordinate refinement
of the unchanged ARC-008 joint mismatch objective. Pilot results were used only
to select this solver family; no caliper or support threshold was changed.

Inspectable data: `pilot_curve_diagnostics.csv` and `pilot_summary.json`.

