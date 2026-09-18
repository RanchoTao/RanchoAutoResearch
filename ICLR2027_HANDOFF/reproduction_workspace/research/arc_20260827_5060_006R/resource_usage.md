# Resource usage

- Start: 2026-08-27T17:52:59+08:00.
- Final resource checkpoint: 2026-08-27T18:00:19+08:00.
- Wall time to final resource checkpoint: 440.2 seconds (7.34 minutes).
- Repair analysis runtime: 0.507 seconds.
- Execution level: Level 2, pure local derived-quantity reanalysis.
- GPU-active time: 0 seconds; peak ARC VRAM: 0 bytes.
- RAM peak: not instrumented; no memory pressure or OOM was observed.
- ARC artifact bytes at checkpoint, excluding `__pycache__`: 406,585 bytes.
- System free-disk decline during the window: 125,792,256 bytes. This is a
  machine-wide counter and is not attributable wholly to ARC-006R; the ARC
  artifacts themselves account for about 0.41 MB.
- Model downloads: 0; dataset downloads: 0; package installs/upgrades: 0.
- External API cost: USD 0; external compute cost: USD 0.

## Network counter incident

The machine-wide WLAN counter increased by 218,421,573 received bytes
(208.30 MiB) and 15,277,060 sent bytes (14.57 MiB), exceeding the prompt's
100 MB accidental-usage warning threshold. This counter includes every process
on the host and cannot attribute historical bytes to ARC-006R.

ARC-006R made no web/tool request, `git fetch`, package operation, model load,
or remote API call. Every execution command set `HF_HUB_OFFLINE=1`,
`TRANSFORMERS_OFFLINE=1`, `HF_DATASETS_OFFLINE=1`, and `WANDB_MODE=offline`.
The analysis used only local CSV/JSON files and local `git show`; no Python
connection was present in the connection audit. Concurrent established
connections belonged to the Codex/ChatGPT client, Chrome/Edge, OneDrive,
WeChat/Android services, and the local Clash/Mihomo proxy. These are the most
likely sources of the machine-wide increase.

Per the network-stop rule, no further scientific experiment was started after
the anomaly was measured. Only reporting, integrity hashing, and the scoped
local git commit remain.
