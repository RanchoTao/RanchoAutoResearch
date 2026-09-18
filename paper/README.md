# Candidate A — ICLR 2027 Draft 2

This directory contains the conservative Candidate A manuscript migrated to
the locally supplied official ICLR 2027 anonymous-submission format. It uses
only validated local ARC evidence and does not contain new scientific
experiments.

## Entry points

- Manuscript source: `main.tex`
- Official template files: `iclr2027/`
- Compiled review copy: `output/candidate_a_iclr2027_draft2.pdf`
- Self-contained Overleaf source: `output/candidate_a_iclr2027_draft2_overleaf.zip`
- Reproducible build instructions: `BUILD.md`
- Format audits: `format_audit/`
- Frozen claims: `main_claims.md`
- Prohibited claims: `prohibited_claims.md`
- Evidence reconciliation: `evidence_status.md`
- Numerical traceability: `numerical_provenance.csv`
- Prior-work collision: `prior_work_collision_table.md`
- Reviewer risks: `reviewer_attack_surface.md`
- Historical Draft 0 gate: `DRAFT0_STATUS.md`

## Build

From `paper/`:

```powershell
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

The official style files are preserved unmodified. Draft 2 compiles cleanly
from the self-contained Overleaf package. Its scientific main text ends on
page 8, references begin on page 9, and the complete document has 11 pages.
See `format_audit/page_budget_draft2.md` and
`format_audit/overleaf_package_audit.md` for the frozen checks.
