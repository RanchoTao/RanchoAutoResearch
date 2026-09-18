# Resource usage

Measured locally for ARC-20260828-5060-011. No values below are estimates of
paid remote activity; none occurred.

| Resource | Recorded use |
| --- | ---: |
| GPU | NVIDIA GeForce RTX 5060 Laptop GPU, 8,151 MiB |
| Recorded checkpoint-processing elapsed time | 138.184 s |
| Peak CUDA memory allocated by runner | 1,062,869,504 bytes (0.990 GiB) |
| End-to-end ARC wall time through final sealing | 20.4 min |
| Host RAM | 15.730 GiB total; peak process RAM not instrumented |
| Observed free host RAM | 3.913 GiB baseline; 3.853 GiB at final capture |
| Final ARC directory size at seal refresh | 9,613,877 bytes |
| Increase from post-preparation baseline | 5,100,221 bytes |
| C: free space | 108.686 GiB baseline; 108.631 GiB at final capture |
| Network requests by ARC | 0 |
| Downloads | 0 bytes |
| API cost | USD 0.00 |
| External compute / AutoDL | USD 0.00 |

The 138.184 seconds is the sum of the runner's checkpoint elapsed-time field
across all six raw runs. CUDA kernel-active time was not separately profiled,
so it is reported as recorded GPU-inference elapsed time rather than a precise
hardware-utilization integral. The ARC directory measurement excludes Git
object-store overhead; the drive-free-space difference also includes unrelated
system activity and is therefore not presented as ARC disk usage.

All models and tokenizer assets were reused from the existing local cache.
There were no OOMs, corrupted runs, discarded seeds, or retry-only results.
