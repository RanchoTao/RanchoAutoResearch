# Provenance, integrity, and commands

## Public provenance

- PolyPythias paper: Oskar van der Wal et al., *Stability and Outliers across
  Fifty Language Model Pre-Training Runs*, ICLR 2025, arXiv:2503.09543.
- Paper: https://arxiv.org/abs/2503.09543
- Pythia repository: https://github.com/EleutherAI/pythia
- Model repositories: `EleutherAI/pythia-160m-seed1` through `seed9`, plus
  `pythia-70m-seed1` through `seed5` for reused confirmation.
- The model cards distinguish combined `seed1-9` replicas from controlled
  `data-seed` and `weight-seed` variants. Combined seeds are genuine separate
  pretraining runs varying initialization and data order, not evaluation
  resamples.

## Frozen definitions

The config, preregistration, runner, and analysis were hashed before any new
deletion result. See `preregistration_manifest.sha256`. The held-out seed9
prediction was hashed before any seed9 weight download or inference:

```text
24F87F513BFF980869FF9833788C1F0F508C74D114522CE0FE357F0822E28869  reports/heldout_run_prediction.md
```

Existing 160M seeds1-5 and 70M seeds1-5 are loaded directly from
`ARC-20260825-5060-002/experiments/raw`; they were not rerun, edited, or copied.

## Main commands

```powershell
# New discovery runs (seed9 was not included at this stage)
.venv\Scripts\python.exe meta_arc05/ARC-20260826-5060-003/src/run_independent.py `
  --config meta_arc05/ARC-20260826-5060-003/configs/independent_runs.yaml `
  --scale 160 --run-id <6|7|8>

# Discovery aggregation before seed9
.venv\Scripts\python.exe meta_arc05/ARC-20260826-5060-003/src/analyze_independent.py `
  --mode discovery

# Held-out seed9 after reports/heldout_run_prediction.md was frozen
.venv\Scripts\python.exe meta_arc05/ARC-20260826-5060-003/src/run_independent.py `
  --config meta_arc05/ARC-20260826-5060-003/configs/independent_runs.yaml `
  --scale 160 --run-id 9

# Final deterministic aggregation and figures
.venv\Scripts\python.exe meta_arc05/ARC-20260826-5060-003/src/analyze_independent.py `
  --mode final
```

Network interruptions required resumable prefetching of the exact public
`pytorch_model.bin` blobs. `src/prefetch_weights.py` enforces HTTP Range
responses, flushes 8 MiB chunks, checks the exact expected file size, records
official commit/ETag metadata, and writes only into the Hugging Face cache.
Transformers then registered and loaded the exact blob from the immutable
checkpoint revision. Final checkpoint evaluation used `HF_HUB_OFFLINE=1` and
`TRANSFORMERS_OFFLINE=1`, preventing background conversion/network behavior.
Prefetching does not calculate or inspect experimental metrics.

## Integrity checks

- Nine 160M raw files, five checkpoints each: 45 checkpoint records.
- 45/45 distinct resolved immutable commit hashes.
- Identical parameter count at every point: 162,322,944.
- Identical candidate block set at every point: layers 1-10 of 12.
- All endpoint intact NLL values pass the frozen `<=5.5` competence threshold.
- Final aggregation is deterministic: rerunning it preserved summary SHA-256
  `A834F5662F2D9D5932880D027B488631FA49B702E308D213ED6A6B39F1C19ECA`.
- All three ARC source files compile under Python 3.13.9.
- Figures 1, 3, 5, and 6 were visually inspected after rendering; labels,
  legends, axes, held-out styling, and confidence-interval caveat are legible.

## New raw SHA-256

```text
pythia-160m-seed6.json 7A9699AAFAF93FEA78670D36E6F75382407B66E24E98B49817EDCA0D829E0ECC
pythia-160m-seed7.json 2DBA909A07121E5C413123F095B1168DF9034301BD44493C96B2389179722E5E
pythia-160m-seed8.json F6AA7F14ECFE5D1701DA07F6D3E1D81A44E99867BC36AF7B7AD4B4E94941EDB1
pythia-160m-seed9.json 78A2E5EC8A715FDE45391559A2D6AAD4906A78FF8115542C609A228DE3A9BF85
```

## Environment and resources

- GPU: NVIDIA GeForce RTX 5060 Laptop GPU, 8,151 MiB reported VRAM.
- Driver 610.74; PyTorch 2.11.0+cu128; CUDA runtime 12.8.
- Transformers 4.56.2; Python 3.13.9.
- New checkpoint-evaluation runtime recorded in raw files: 235.24 seconds.
- Peak allocated CUDA memory: 1,061,554,688 bytes (0.99 GiB).
- Gross elapsed clock from frozen baseline to final output: approximately
  13 h 55 min, including about 10 h of explicit task interruptions and long
  pauses. Active execution/download wall time was approximately 3 h 45 min.
- Added model-cache plus ARC artifact bytes: approximately 7,815,013,368 bytes
  (7.28 GiB). Windows' no-symlink Hugging Face cache duplicates some files.
- Paid/API cost: USD 0.

