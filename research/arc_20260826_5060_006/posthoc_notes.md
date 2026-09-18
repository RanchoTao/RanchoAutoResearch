# Post-hoc notes

No scientific definition, target, strength, match class, threshold, exclusion,
equivalence bound, analysis rule, or verdict rule was changed after reveal.

After reveal, only the preregistered analysis was executed and the required
reports/figures were generated. Visual QA found no misleading scale, clipping,
or hidden data issue. A Matplotlib warning about an edge color on an unfilled
`x` marker in Figure 1 was cosmetic and was not patched because the marker is
clearly visible and changing the plotting code was unnecessary.

The shared-logit decision-boundary explanation discussed in the reports is a
post-result hypothesis for ARC-007, not a tested ARC-006 conclusion.

During final reproducibility verification, `build_target_manifest.py` was first
invoked with the inference virtual environment, which intentionally lacks
Pandas, and exited before reading or writing results. It was immediately rerun
with the documented system-Python analysis environment. The target-manifest
SHA-256 was identical before and after successful regeneration. This was a
verification-command environment error, not an experimental run failure.
