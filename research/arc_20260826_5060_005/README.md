# ARC-20260826-5060-005

Intervention-family robustness test for Candidate A.

Final status: `FAMILY-PARTIAL` (confidence: MEDIUM).

Norm-controlled additive activation noise reproduced Candidate A's sign in
5/5 independent runs, but the primary cross-family damage-matched analysis did
not establish equivalence. Only 26/150 block cells had a joint 10% KL/NLL
match, and the observed family residual was -0.01960, outside the frozen
±0.01074 equivalence band. See `family_robustness_report.md`.

The preregistration and confirmatory protocol remain frozen in git. A single
post-result repair for JSON scalar serialization is disclosed in
`posthoc_notes.md`; it did not alter any calculation or decision rule.
