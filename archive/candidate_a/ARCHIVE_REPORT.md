# Candidate A archive report

## Freeze

- Freeze tag: `Candidate-A-Paper-Freeze-v1`
- Freeze commit: `5ba0df6518e6d1782ae46001150e6df0dda684a0`
- Branch at freeze: `main`
- Tag timestamp: `2026-08-28T23:26:58+08:00`
- Research state: `PAPER FREEZE`

The annotated tag resolves exactly to the validated Draft 2 commit. The
archive/index commit is later and does not move the scientific freeze point.

## Archived files

`archive/candidate_a/manuscript/` preserves:

- `candidate_a_iclr2027_draft2.pdf`;
- `candidate_a_iclr2027_draft2_overleaf.zip`;
- `main.tex`, `references.bib`, and `numerical_provenance.csv`;
- all ten section files and the appendix;
- the result table and nine empirical figure panels;
- the locally supplied official ICLR 2027 support files;
- compact snapshots of the major JSON/CSV evidence artifacts used by the
  manuscript, organized under `evidence/`;
- Draft 2 changelog, build instructions, frozen/prohibited claims, evidence
  status, reviewer surface, prior-work table, and format audits.

No model weight, dataset, environment, raw cache, or unrelated ARC directory is
duplicated into the archive.

## Integrity

- `SHA256SUMS.txt` contains 17 SHA256 entries: the final PDF, Overleaf ZIP,
  central manuscript sources, numerical ledger, and major JSON/CSV artifacts
  used by the paper.
- All listed hashes were regenerated and verified after the archival copy.
- The archived PDF has 11 pages; the source ZIP passed its prior clean extracted
  pdfLaTeX/BibTeX build.
- The validity map covers ARC-003 through ARC-012, including separate rows for
  mixed-validity analyses.

## Mandatory validity rule

```text
ARC-006 original results -> INVALIDATED
ARC-006R -> canonical corrected evidence
```

This rule is recorded in the freeze manifest, validity map, and frozen result
table. No invalid ARC-006 outcome estimate is presented as valid evidence.

## Open paper issues

The unresolved revision issues are novelty/significance relative to *No Free
Swap*, the meaning and completeness of KL/NLL matching, justification of the
equivalence threshold, five-run cross-family precision, unmatched-cell support,
small-Pythia scope, and incomplete mechanism identification. They are writing
or review issues, not authorization for autonomous experiments.

## Reopen policy

Candidate A research remains closed unless a human high/fatal review gap, an
ICLR or external-review request, a reproducibility failure, or explicit user
authorization triggers `REOPEN_POLICY.md`. Paper editing remains allowed within
the frozen evidence and claim boundaries.

## Candidate B

`research/candidate_b/` exists with only the five requested discovery-control
files. Its scientific question is `TBD`, its GO/KILL loop is `NOT STARTED`, and
no experiment or literature search has begun.

## Execution boundary

This archival task ran no scientific experiment, model inference, literature
search, dataset operation, package installation, API call, or paid service.
