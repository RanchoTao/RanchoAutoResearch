# Resource usage

- ARC directory creation to final analysis checkpoint: approximately 741 s
  (12.35 min); final documentation remained within the 35-minute preference.
- Recorded GPU/checkpoint runtime: 104.27 s.
- Peak allocated CUDA memory: 1,268,250,624 bytes (1.18 GiB).
- ARC artifact size before final reports/seal: 795,879 bytes.
- GPU: local NVIDIA GeForce RTX 5060 Laptop GPU only.
- Model inference: local cached Pythia-160M checkpoints only; no training.
- Held-out Stage B outcome inference: not run after support failure.
- Network/download operations: none; offline environment variables enforced.
- Model downloads: none.
- Dataset downloads: none.
- Package installs/upgrades: none.
- API cost: USD 0.
- External compute cost: USD 0.

GPU runtime is the sum recorded inside Stage A and calibration checkpoint
artifacts. It includes model execution and local overhead, not a hardware
utilization integral.
