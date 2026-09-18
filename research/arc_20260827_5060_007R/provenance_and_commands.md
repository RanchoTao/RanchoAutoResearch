# Provenance and commands

## Sources

- Corrected outcomes:
  `research/arc_20260827_5060_006R/corrected_results.csv`
- Corrected seal and summary:
  `research/arc_20260827_5060_006R/final_integrity.sha256` and
  `results/corrected_summary.json`
- Saved logits geometry:
  `research/arc_20260826_5060_007/raw/geometry/*.json`
- Saved intact margins:
  `research/arc_20260826_5060_007/raw/per_example/*.npz`
- Historical outcome-blind match seal:
  `research/arc_20260826_5060_007/geometry_match_manifest.csv`

All commands inherited these variables:

```powershell
$env:HF_HUB_OFFLINE='1'
$env:TRANSFORMERS_OFFLINE='1'
$env:HF_DATASETS_OFFLINE='1'
$env:WANDB_MODE='offline'
```

Execution:

```powershell
python research/arc_20260827_5060_007R/src/prepare_geometry_blind.py
python research/arc_20260827_5060_007R/src/analyze_geometry.py
```

The first corrected analysis stopped before model fitting due to a documented
pandas dtype issue. `posthoc_notes.md` records the mechanical repair and later
presentation-only figure correction. Logs preserve the attempts.
