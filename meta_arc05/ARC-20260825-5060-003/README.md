# ARC-20260825-5060-003 — Cross-family external validity

Prospective test of the ARC-002 broad early-to-late layer-deletion robustness
decline on one independent non-Pythia training trajectory. This ARC does not
test mechanism or universal monotonicity.

Final verdict: **MIXED**. SmolLM2-360M reproduces the negative endpoint
direction, but the preregistered `-0.05` magnitude gate fails and the sparse
trajectory cannot separate continued training from the final WSD decay phase.

Start with `reports/final_arc_report.md`; exact provenance and commands are in
`reports/cross_family_provenance.md`.
