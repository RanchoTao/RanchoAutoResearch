# Handoff completeness audit

Audit date: 2026-08-31 (Asia/Shanghai).

## Checks passed

- Canonical paper source, sections, appendix, bibliography, template, tables, figures, Overleaf ZIP, and PDF are present.
- The user-supplied PDF, frozen archive PDF, and repository Draft 2 PDF are byte-identical: SHA-256 `C4157787DE4BE436E94AE66888135C862C1AAD93987C7D86655BE86CD7999421`.
- A clean build from `paper/current/main.tex` completed with 11 pages, no undefined citation/reference lines, and no overfull boxes. The rebuild PDF differs in byte hash because regenerated PDF metadata is not bitwise deterministic; the frozen canonical PDF remains unchanged.
- All 22 rows in `paper/current/numerical_provenance.csv` resolve to a present source artifact in `reproduction_workspace/`.
- All 296 JSON files present at audit time parsed successfully.
- Required core code, config, result, figure, and data entry points are present.
- ARC-006 invalid outcomes are visibly segregated and superseded by ARC-006R.
- Failed/inconclusive branches and technical failures are retained.
- Exact relative source layout is preserved under `reproduction_workspace/`.
- No scientific inference, model download, dataset download, API call, or training run was performed during migration.

## Traceability outcome

- Every paper headline number is mapped through `paper/current/numerical_provenance.csv` to package-local JSON/CSV/Markdown evidence.
- Paper panels are mapped to their ARC, source summary, and generation code in `figures/README.md` and `FILE_INDEX.md`.
- Frozen configs, seeds, checkpoints, layers, strengths, matching calipers, and statistical units are recorded in `configs/`, `EXPERIMENTS.md`, and ARC preregistrations.

## Known missing information

1. Verified non-anonymous author names, affiliations, email, author order, submission ID, and conflict metadata.
2. Original HellaSwag validation JSONL; only its expected hash and the complete derived evaluation artifacts remain.
3. Hugging Face model weights/cache and a complete tested fresh-machine downloader for every 70M/160M revision.
4. One clean-room-validated unified Python lock; historical GPU and CPU analysis environments were split.
5. Modern billion-scale/cross-architecture experiments, semantic downstream endpoints, and a main overview figure—these were never completed and are not silently represented as packaged.

## Readiness judgment

The package is sufficient for a new agent to understand the scientific state, audit every current claim, rebuild the paper, regenerate analyses/figures from preserved outputs, and plan revisions. Fresh end-to-end GPU inference is partially blocked until public checkpoints are cached and the environment is cleanly reconstructed. This is a migration-ready research package with explicitly documented external dependencies, not a fully offline reproduction capsule.
