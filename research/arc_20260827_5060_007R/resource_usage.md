# Resource usage

- ARC wall interval: 2026-08-27 20:32:21 to 20:45:32 Asia/Shanghai
  (`790.78 s`, including audit, preregistration, analysis, figure QA, and reports).
- Outcome-blind computation: `0.84 s` wall.
- Final measured validation run: `2.96 s` wall, `2.69 s` CPU.
- GPU-active time: `0 s`; analysis used NumPy/pandas/scikit-learn on CPU.
- Observed system GPU memory during validation: `83 MiB`; this was ambient
  display/system allocation, not ARC tensors. No CUDA context was opened.
- Peak Python working set during monitored validation: `239,046,656 bytes`
  (`228.0 MiB`).
- ARC directory size at reporting: `1,080,738 bytes` (`1.03 MiB`).
- System free-disk counter changed by `6,082,560 bytes` over the full interval;
  this background-inclusive value exceeds the ARC directory itself.
- ARC-caused network operations: none. No web/network tool, model hub, package
  manager, git remote, API, or remote artifact command was invoked.
- WLAN adapter counter delta during the wall interval: 12,042,566 bytes RX and
  7,901,937 bytes TX. This host-wide background traffic is not attributable to
  the ARC; the ARC's configured and observed public retrieval was `0 bytes`.
- API cost: `USD 0`.
- External compute cost: `USD 0`.
- Model downloads: none.
- Dataset downloads: none.
- Package installs/upgrades: none.
- Model inference/training: none.

All Python runs used `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`,
`HF_DATASETS_OFFLINE=1`, and `WANDB_MODE=offline`.
