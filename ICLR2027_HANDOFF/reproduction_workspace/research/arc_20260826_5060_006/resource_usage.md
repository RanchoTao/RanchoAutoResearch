# Resource usage

Measurement window: 2026-08-26 16:25:19 to approximately 17:23 Asia/Shanghai.

| Resource | Measured use |
| --- | ---: |
| GPU-stage/checkpoint runtime | 2,244.98 s (0.624 h) |
| Pilot targeting | 151.15 s |
| Refined pilot targeting | 102.96 s |
| Confirmatory targeting | 1,911.65 s |
| Reveal | 79.22 s |
| End-to-end wall time through final analysis/docs | approximately 58 min |
| Peak allocated CUDA memory | 1,062,199,808 bytes (1.06 GB decimal) |
| Peak process RAM | not instrumented |
| Initial ARC bytes | 78,550 |
| Added bytes before integrity manifest, excluding `__pycache__` | 3,458,351 (3.30 MiB) |
| Model downloads | 0 |
| API cost | USD 0 |
| External compute cost | USD 0 |

GPU-stage runtime is the sum of checkpoint runtimes recorded by the four frozen
execution stages. It is a conservative wall-clock proxy for GPU-active work,
not a hardware-counter utilization integral. RAM was not instrumented, so no
retrospective value is invented.
