# Provenance and commands

## Frozen history

- ARC-006 source commit: `21d361a24c6bb391e29be87b834b39e6b6235fc9`
- ARC-007 preregistration commit:
  `d005fbec01f0d35b8902d8467fe68062282abb80`
- Corrected preregistration-record commit:
  `1264cbf2eac24968212351d3c7946c52fb852f6e`
- Historical `topk` raw seal: `1a6892b`
- ARC-007 extractor correction: `1c166b6`
- Current `argmax` raw seal: `4fd4d3e`

## Source evidence for the mismatch

- `meta_arc05/ARC-20260825-5060-002/src/run_stability.py:80-81` uses
  `probs.topk(2)` for intact top-1.
- `research/arc_20260826_5060_004/src/run_mechanism.py:244-245` uses the same.
- `research/arc_20260826_5060_005/src/run_activation_noise.py:234-235` uses the
  same for the prior family assay.
- `research/arc_20260826_5060_006/src/run_reveal.py:81` uses
  `logits.argmax(-1)` for the new noise reveal.

## Reproduction commands

Run from the repository root with Python 3.13.9:

```powershell
python research/arc_20260826_5060_007/src/build_cell_manifest.py
2,3,5,6,8 | ForEach-Object {
  python research/arc_20260826_5060_007/src/run_geometry.py --run-id $_
}
python research/arc_20260826_5060_007/src/freeze_geometry_matches.py
python research/arc_20260826_5060_007/src/analyze_geometry.py
```

The last command intentionally stops at the `D_S` reproduction gate. The
minimal post-stop diagnostic is:

```powershell
python research/arc_20260826_5060_007/src/diagnose_top1_inconsistency.py
```

It reads the historical `topk` raw data directly from git commit `1a6892b`,
the current `argmax` raw data, and ARC-006's frozen source table. It writes the
diagnostic CSV, JSON, and single invalidation figure without fitting an ARC-007
geometry model.
