# ARC-010 resource usage

| Resource | Observed use |
|---|---:|
| GPU-active time | 0 seconds |
| New model inference | 0 |
| Model downloads | 0 bytes |
| Dataset downloads | 0 bytes |
| External network | 0 bytes by ARC-010 scripts |
| API cost | USD 0 |
| External compute cost | USD 0 |
| AutoDL | Not used; not justified |

ARC-010 uses CPU-only local file parsing and hashing. The final validation record
captures the elapsed artifact-construction interval and exact package hashes.
