# ARC-21 environment audit

Recorded 2026-08-24, Asia/Shanghai.

- Repository: AutoResearchClaw, branch `main`, commit
  `e2e23c93b4943fd21cc531deb09850d8fda55357`.
- Pre-existing dirty working tree left untouched; ARC-21 is isolated under
  `arc21/`.
- Python 3.13.9.
- PyTorch 2.11.0+cu128; CUDA runtime 12.8.
- GPU: NVIDIA GeForce RTX 5060 Laptop GPU, 8151 MiB VRAM.
- Transformers 4.56.2 (not required by the custom tiny model).
- Reused environment:
  `gap_mining/claim_evidence_execconfig_20260824/.venv`.

