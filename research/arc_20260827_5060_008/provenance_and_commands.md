# Provenance and commands

Valid sources:

- `research/arc_20260827_5060_006R/corrected_results.csv`
- `research/arc_20260827_5060_006R/final_integrity.sha256`
- `research/arc_20260827_5060_007R/processed/geometry_pairs_corrected.csv`
- `research/arc_20260827_5060_007R/final_integrity.sha256`
- cached Pythia-160M seed2/3/5/6/8 checkpoints at 14k/72k/143k
- frozen WikiText assay corpus from META-ARC-05

All model commands inherited:

```powershell
$env:HF_HUB_OFFLINE='1'
$env:TRANSFORMERS_OFFLINE='1'
$env:HF_DATASETS_OFFLINE='1'
$env:WANDB_MODE='offline'
```

Execution sequence:

```powershell
2,3,5,6,8 | % { .venv\Scripts\python.exe research/arc_20260827_5060_008/src/run_stage_a.py --config research/arc_20260827_5060_008/config.yaml --run-id $_ }
python research/arc_20260827_5060_008/src/analyze_stage_a1.py
2,3,5,6,8 | % { .venv\Scripts\python.exe research/arc_20260827_5060_008/src/run_counterfactual.py --config research/arc_20260827_5060_008/config.yaml --run-id $_ --phase calibrate }
python research/arc_20260827_5060_008/src/freeze_calibration.py
python research/arc_20260827_5060_008/src/analyze_results.py
```

The confirm phase was intentionally not run after the frozen support gate
failed. `posthoc_notes.md` records three implementation-only repairs made
before relevant results existed.
