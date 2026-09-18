# Environment audit

Recorded 2026-08-25 before anchor selection.

- Repository: `AutoResearchClaw`
- Branch: `main`
- Commit: `e2e23c93b4943fd21cc531deb09850d8fda55357`
- Worktree: pre-existing local modifications and untracked research artifacts;
  this run does not overwrite them and is isolated under `meta_arc05/`.
- Python: 3.13.9
- PyTorch: 2.11.0+cu128
- CUDA runtime reported by PyTorch: 12.8
- GPU: NVIDIA GeForce RTX 5060 Laptop GPU
- VRAM: 8,151 MiB reported by `nvidia-smi` (8,546,484,224 bytes via PyTorch)
- NVIDIA driver: 610.74
- Transformers: 4.56.2
- Free space on C: approximately 152.3 GB
- Experiment environment: existing isolated venv
  `gap_mining/claim_evidence_execconfig_20260824/.venv`

No paid API or large model download is authorized.
