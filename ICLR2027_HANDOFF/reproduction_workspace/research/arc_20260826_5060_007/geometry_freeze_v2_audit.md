# Geometry pre-analysis freeze audit v2

After correcting the frozen-argmax anchoring bug documented in
`technical_failure_log.md`, all five runs and 15 checkpoints were regenerated.
All harnesses and per-example hashes pass.

The unchanged, outcome-blind calipers select 31/103 Class A cells (30.10%).
The prespecified support gate still passes. No `D_S` or geometry-conditioned
residual was read by the matcher or inspected before this second seal. This v2
seal supersedes the historical faulty-extractor seal for scientific analysis.

