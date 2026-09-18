# Resource usage

- Start: 2026-08-26T20:14:34+08:00.
- Local GPU only: NVIDIA GeForce RTX 5060 Laptop GPU.
- GPU-stage wall time: 242.50 seconds total across the invalidated and corrected
  extractions. This is an upper bound on GPU-active time because wall timing
  includes CPU/tokenization and I/O.
- Peak allocated CUDA memory: 1,165,256,192 bytes (about 1.09 GiB).
- Current ARC artifact size excluding `__pycache__`: 32,930,872 bytes at the
  final pre-commit checkpoint.
- Observed system free-disk decline during the run: 377,098,240 bytes; this is
  not attributed wholly to ARC-007 because repository objects and unrelated
  processes share the volume.
- RAM peak: not instrumented; no system-memory pressure or OOM occurred.
- Downloads: none; all model checkpoints and corpus data were cached.
- API cost: USD 0.
- External compute cost: USD 0.
- Wall time at final pre-commit checkpoint: 1,613 seconds (26.9 minutes).
