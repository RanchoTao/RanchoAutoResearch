# ARC-20260828-5060-010

Paper consolidation, claim audit, and reviewer stress test for Candidate A.

This ARC uses only sealed local evidence from ARC-003 through ARC-009. It runs
no model inference and introduces no new scientific result. Its purpose is to
separate defensible paper claims from invalidated, exploratory, and unresolved
evidence, then choose one highest-information next experiment.

Final verdict and reading entry point: `EXECUTIVE_SUMMARY.md`.

## Scope and resource contract

- Evidence window: sealed local artifacts from ARC-003 through ARC-009.
- Supersession rule: ARC-006 exact estimates are withdrawn; ARC-006R is canonical.
- New model inference, downloads, web/API calls, and GPU work: none.
- Scientific output: synthesis and audit only; the recommended experiment is not run.

## Reproduce this audit

From the repository root, with the existing Python environment:

```powershell
$env:HF_HUB_OFFLINE = "1"
$env:TRANSFORMERS_OFFLINE = "1"
$env:HF_DATASETS_OFFLINE = "1"
$env:WANDB_MODE = "offline"
python research/arc_20260828_5060_010/src/audit_evidence.py
python research/arc_20260828_5060_010/src/finalize_integrity.py
```

The first command recomputes paper-critical summaries and writes the evidence
ledger. The second verifies the required package and seals its final files.
