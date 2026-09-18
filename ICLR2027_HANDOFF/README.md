# ICLR 2027 Candidate A handoff

This package freezes and migrates the Candidate A project without adding experiments or changing manuscript content.

## Canonical entry points

- Project state: `PROJECT_STATE.md`
- Latest manuscript source: `paper/current/main.tex`
- Latest compiled paper: `paper/current/candidate_a_iclr2027_draft2.pdf`
- Reproduction: `REPRODUCTION.md`
- Numerical ledger: `paper/current/numerical_provenance.csv`
- Experiment ledger: `EXPERIMENTS.md` and `EXPERIMENT_INDEX.csv`
- Frozen validity rules: `logs/EVIDENCE_VALIDITY_MAP.md`

## Freeze identity

- Project: Candidate A
- Paper title: *Intervention-Conditioned Layer Fragility Across Language-Model Pretraining*
- Scientific state: `PAPER FREEZE`
- Freeze tag: `Candidate-A-Paper-Freeze-v1`
- Frozen manuscript commit: `5ba0df6518e6d1782ae46001150e6df0dda684a0`
- Repository HEAD observed during migration: `252ab4b1c87b09dc4908dda91c57810343ddc069`
- Migration date: 2026-08-31 (Asia/Shanghai)

The supplied `Shengye_Tao_ICLR2027_draft.pdf`, repository `paper/main.pdf`, and frozen archive PDF are byte-identical (SHA-256 `C4157787DE4BE436E94AE66888135C862C1AAD93987C7D86655BE86CD7999421`). The manuscript is anonymous; the filename is not treated as verified author metadata.

## Non-negotiable evidence rule

`ARC-006 original outcome analysis -> INVALIDATED`  
`ARC-006R deterministic-top-1 repair -> canonical corrected evidence`

Never recover ARC-006 outcome estimates as evidence merely because the files are preserved. They remain only as an audit trail.

## Package organization

- `paper/`: latest source/PDF/Overleaf bundle and Draft 0/1 history.
- `code/`: runnable ARC scripts copied by ARC.
- `configs/`: frozen YAML configurations.
- `results/`: raw, processed, matching, and summary outputs by ARC.
- `figures/`, `tables/`: paper panels plus regenerable ARC visualizations.
- `logs/arc_records/`: complete research records, including preregistrations, commands, reports, failures, hashes, code, results, and figures.
- `data/`: locally preserved WikiText-2 text and HellaSwag-derived evaluation artifacts. The original HellaSwag validation JSONL is no longer present; see `data/README.md`.

This package does not include model weights or Hugging Face caches. Public immutable model identifiers and revisions are recorded in the ARC provenance files.
