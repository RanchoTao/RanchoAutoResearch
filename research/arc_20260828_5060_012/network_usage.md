# Network usage

## Baseline and policy

- Low-bandwidth literature browsing only.
- Paid APIs: prohibited and unused.
- PDF downloads to local disk: 0 at freeze time.
- Model/dataset/code/archive downloads: 0.
- GPU/model inference: 0.
- Network-byte attribution is not exposed by the browser/search tool; adapter
  counters are recorded as a conservative system-wide before/after bound and
  may include unrelated host traffic.

## Sealed counters

Counters were sampled at 2026-08-28 02:20:11+08:00 and again at 02:44:16.

| Adapter | Received before | Received after | Sent before | Sent after |
|---|---:|---:|---:|---:|
| WLAN | 3,267,446,363 | 3,828,596,327 | 821,925,488 | 863,323,488 |
| vEthernet (WSL) | 1,152 | 1,152 | 13,181 | 71,517 |
| Ethernet | 0 | 0 | 0 | 0 |

The conservative system-wide delta is about 602.6 MB decimal (574.7 MiB),
which exceeds the 500 MB target if all host traffic is attributed to this ARC.
These OS counters include unrelated traffic and cannot identify the browser
tool's share. Browsing stopped at this seal; no additional download was
attempted after the threshold was observed.

- Local PDF files downloaded: **0**.
- T3–T5 primary records deep-read: **10**.
- Candidate metadata records retained: **33**.
- Model weights, datasets, repositories, archives: **0**.
- Paid API cost: **USD 0**.
- GPU use: **0**.
- Package/environment changes: **0**.

`network_baseline.csv` preserves the raw starting counters. The values above are
a conservative upper bound, not a claim that the audit itself transferred that
entire amount.
