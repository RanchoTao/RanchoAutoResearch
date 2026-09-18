# Provenance and commands

## Frozen sources

- ARC-006R corrected source SHA-256:
  `322296700df8b6ee2a24bc03c9d30727446c34dcf85c8a9fbfa46925b2c52ce7`.
- ARC-009 sanitized target SHA-256:
  `802bb7a9624e528bdad57f8ea48357afdf0c623e12d3e828cde43ae6c57ad67f`.
- Preregistration commit:
  `c2e2ff2d3478a24b0c21cf9e6f886f9db33bc634`.
- Local Pythia-160M seed2/3/5/6/8 checkpoints at steps
  14k/72k/143k and the frozen local WikiText assay.

## Commands

```powershell
python research\arc_20260828_5060_009\src\sanitize_targets.py
python research\arc_20260828_5060_009\src\pilot_diagnostics.py

$env:HF_HUB_OFFLINE='1'
$env:TRANSFORMERS_OFFLINE='1'
$env:HF_DATASETS_OFFLINE='1'
$env:WANDB_MODE='offline'
foreach ($run in 2,3,5,6,8) {
  .\.venv\Scripts\python.exe research\arc_20260828_5060_009\src\run_calibration.py `
    --config research\arc_20260828_5060_009\config.yaml --run-id $run
}

python research\arc_20260828_5060_009\src\analyze_calibration.py `
  --orchestration-wall-seconds 256.0082008
```

No package install, model/data download, web access, API, or external compute
was used. The model runner contains no confirm/reveal mode.

