# Resource baseline

Captured 2026-08-26T00:20:42+08:00 before new model-weight downloads.

- GPU: NVIDIA GeForce RTX 5060 Laptop GPU, 8,151 MiB reported VRAM.
- Driver: 610.74.
- Python: 3.13.9.
- PyTorch: 2.11.0+cu128; CUDA available; runtime 12.8.
- Transformers: 4.56.2.
- Hugging Face cache: 26,797,496,157 bytes.
- Seed6-9 cache before weights: 2,552 bytes (config files only).
- Free C: drive: 120,874,360,832 bytes.
- Paid API cost: USD 0.

The project environment had drifted to CPU-only PyTorch 2.13 with Transformers
absent. It was restored inside the repository `.venv` to the versions used by
ARC-002 before this baseline was captured. No system Python was modified.

