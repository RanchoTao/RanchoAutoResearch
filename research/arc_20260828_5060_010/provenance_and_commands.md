# Provenance and commands

## Evidence roots

- Core validation: `meta_arc05/ARC-20260826-5060-003/`
- Mechanism discrimination: `research/arc_20260826_5060_004/`
- Second intervention family: `research/arc_20260826_5060_005/`
- Canonical assay repair: `research/arc_20260827_5060_006R/`
- Output geometry: `research/arc_20260827_5060_007R/`
- Internal-direction observational gate: `research/arc_20260827_5060_008/`
- Continuous-alpha feasibility gate: `research/arc_20260828_5060_009/`
- Local direct literature anchor: `meta_arc05/external/Remarkable-Robustness-of-LLMs/`

## ARC-010 execution

PowerShell environment was held offline:

```powershell
$env:HF_HUB_OFFLINE = "1"
$env:TRANSFORMERS_OFFLINE = "1"
$env:HF_DATASETS_OFFLINE = "1"
$env:WANDB_MODE = "offline"
& 'C:\Users\RanchoTao\AppData\Local\Programs\Python\Python313\python.exe' `
  research\arc_20260828_5060_010\src\audit_evidence.py
& 'C:\Users\RanchoTao\AppData\Local\Programs\Python\Python313\python.exe' `
  research\arc_20260828_5060_010\src\finalize_integrity.py
```

The first script reads stored JSON/CSV/Markdown/manifests, recomputes the core
aggregates and verifies available seals. It writes `artifact_audit.json` and
`evidence_ledger.csv`. The second validates required deliverables and writes the
final integrity records. Neither script imports model libraries, opens a network
connection, or invokes a GPU.

## Supersession rule

`research/arc_20260827_5060_006/` is provenance for an invalidated analysis only.
The canonical quantitative residual is under `006R`; later geometry/direction
analyses were checked against that corrected baseline.
