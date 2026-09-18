# Provenance and commands

## Frozen commits

- Initial preregistration: `5ec475a87cf322248114ce61cc89ed8a70598e1c`
- Calibration-token correction before new data: `93b75ecc267b0c784a705cf0ebd71b360c18d740`
- Calibration harness: `2d56f2918fbfc0efb9f8f7f0e0c0271bea66f3ed`
- Confirmatory protocol: `0b84552b09a036a40069c242d142f87c81d1df28`
- Anchor schema clarification: `2c3822e2de4d54541d17eef739ba66c093a740e5`
- Confirmatory analysis freeze: `4f167c2465cdedcf9d25fc9303164d279695af01`

File hashes frozen before confirmation are in `analysis_freeze.sha256`. Raw
confirmatory SHA-256 hashes are embedded in
`results/family_robustness_summary.json`.

## Confirmatory execution

From the repository root, using only cached Hugging Face revisions:

```powershell
$arcPython='.\.venv\Scripts\python.exe'
$runner='research/arc_20260826_5060_005/src/run_activation_noise.py'
$config='research/arc_20260826_5060_005/configs/confirmatory.yaml'
foreach($runId in @(2,3,5,6,8)){
  & $arcPython $runner --config $config --run-id $runId
}
```

## Analysis and figure regeneration

```powershell
python research/arc_20260826_5060_005/src/analyze_confirmatory.py --mode final
```

The first analysis invocation failed only at JSON serialization on a NumPy
`int64`; `posthoc_notes.md` records the scalar-adapter repair. Re-running the
same command generated the processed tables, matching diagnostics, summary,
and five figures. No paid API, external communication, model download, or
external compute was used.
