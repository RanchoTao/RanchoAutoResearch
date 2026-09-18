# Provenance and commands

## Policy-required offline environment

```powershell
$env:HF_HUB_OFFLINE = "1"
$env:TRANSFORMERS_OFFLINE = "1"
$env:HF_DATASETS_OFFLINE = "1"
$env:WANDB_MODE = "offline"
```

No DeepSeek or other API proposal was requested because the ARC contract
forbids external APIs and network access. This is a policy-required
`codex-only-fallback`, not a missing or fabricated external response.

## Corpus preparation

```powershell
.venv\Scripts\python.exe `
  research\arc_20260828_5060_011\src\prepare_corpus.py
```

## Pre-outcome seal

```powershell
git commit -m "Preregister ARC-011 cross-corpus robustness"
git rev-parse HEAD
```

Commit: `f0f2a329caf6e1c113ef38e938cb69ffb6935dee`.

## Frozen inference

For pilot runs 1, 4, 9 and confirmatory runs 6, 7, 8:

```powershell
.venv\Scripts\python.exe `
  research\arc_20260828_5060_011\src\run_cross_corpus.py `
  --config research\arc_20260828_5060_011\configs\cross_corpus.yaml `
  --run-id <RUN_ID> `
  --stage <pilot|confirmatory>
```

## Analysis and independent validation

```powershell
gap_mining\claim_evidence_execconfig_20260824\.venv\Scripts\python.exe `
  research\arc_20260828_5060_011\src\analyze_cross_corpus.py

gap_mining\claim_evidence_execconfig_20260824\.venv\Scripts\python.exe `
  research\arc_20260828_5060_011\src\validate_results.py
```

All reported values trace to `raw/`, `processed/`, `matching_diagnostics/`, or
`results/`. Figure sources are the saved processed CSV/JSON outputs.
