# Environment record

Observed during migration on 2026-08-31; historical experiment values are from frozen ARC provenance.

## Host

- OS: Windows 10 Home China as reported by PowerShell; build `26200` (the marketing label may not reflect the underlying preview/newer build accurately).
- GPU: NVIDIA GeForce RTX 5060 Laptop GPU.
- VRAM: 8,151 MiB.
- Driver: 610.74.
- Disk free at migration: C approximately 99.60 GiB; D approximately 446.58 GiB.

## Historical GPU inference environment

- Python 3.13.9.
- PyTorch 2.11.0+cu128.
- CUDA runtime reported by PyTorch: 12.8.
- transformers 4.56.2.
- huggingface-hub 0.36.2.
- safetensors 0.8.0.
- NumPy 2.5.2.
- matplotlib 3.11.1 observed at migration (historical ARC reports used 3.10.7 for CPU plots).
- PyYAML 6.0.3.
- The project `.venv` did not contain `datasets`, `scipy`, or `pandas` at migration.

## Historical CPU analysis environments

System Python:

- Python 3.13.9; NumPy 2.2.6; SciPy 1.16.3; pandas 2.3.3; matplotlib 3.10.7; datasets 4.8.5; PyYAML 6.0.3.

Separate analysis venv used by ARC-011:

- Python 3.13.9; NumPy 2.5.2; SciPy 1.16.2; pandas 2.3.2; matplotlib 3.10.6; PyYAML 6.0.3.

This split is a reproducibility smell. The reconstructed `requirements.txt` aims to unify the dependencies but has not been validated by rerunning scientific inference in this migration.

## Resource observations

- Primary ARC-003 new checkpoint inference: 235.24 seconds recorded GPU runtime; peak allocated CUDA memory 1,061,554,688 bytes (0.99 GiB).
- ARC-004/005/011 similarly report approximately 0.99 GiB peak allocated VRAM for their frozen batches.
- ARC-011 six-run recorded checkpoint runtime: 138.18 seconds.
- API/external compute cost across the validated chain: USD 0.
- Model cache addition during ARC-003: approximately 7.28 GiB; model caches are intentionally not duplicated here.
- Handoff package disk usage is recorded in `AUDIT_REPORT.md` and may differ after future edits.

## Precision and GPU settings

- Historical checkpoints were loaded from immutable Hugging Face revisions, generally in FP16 CUDA inference.
- Batch size 2; sequence length 256; offline variables used after cache population: `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, `HF_DATASETS_OFFLINE=1`, `WANDB_MODE=offline`.
- Exact config values are in `configs/` and `reproduction_workspace/`.

## Dependency files

- `requirements.txt`: practical unified reconstruction; not yet clean-room validated.
- `requirements-gpu.txt`: observed GPU environment core.
- `requirements-analysis.txt`: observed CPU analysis core.
