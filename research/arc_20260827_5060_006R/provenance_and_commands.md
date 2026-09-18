# Provenance and commands

## Freeze chain

- Invalid ARC-006 source commit: `21d361a24c6bb391e29be87b834b39e6b6235fc9`.
- ARC-007 invalidation commit: `be6cf30715093a677a1786bc230217adfa5e9db0`.
- Historical globally consistent `topk` seal: `1a6892b`.
- Canonical lowest-index/`argmax` seal: `4fd4d3e`.
- ARC-006R preregistration commit:
  `a364476`.
- Frozen target-manifest SHA-256:
  `19DF473393F82DC2E2D1E531B6F8DF7C9DBF10590C74DE0CE9FFE39DF003DCD0`.

All exact source paths, hashes, roles, and record counts are in
`reanalysis_manifest.csv`.

## Execution command

Run from the repository root:

```powershell
$env:HF_HUB_OFFLINE='1'
$env:TRANSFORMERS_OFFLINE='1'
$env:HF_DATASETS_OFFLINE='1'
$env:WANDB_MODE='offline'
python research/arc_20260827_5060_006R/src/reseal_arc006.py
```

The script uses only local ARC-006/007 artifacts and local git objects. It
regenerates all CSV, JSON, Markdown reports, and figures; no model is loaded.
