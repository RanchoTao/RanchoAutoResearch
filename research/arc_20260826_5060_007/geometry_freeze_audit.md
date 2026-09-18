# Geometry pre-analysis freeze audit

- Five raw run JSON files contain 15/15 completed checkpoints.
- Fifteen compressed per-example NPZ files are present; every stored SHA-256
  agrees with its raw checkpoint record.
- All 15 activation-noise harness checks pass.
- The geometry matcher contains no `D_S`, top-1, flip, agreement, or residual
  token and reads only identity plus `delta_b`, logit norm, and absolute cosine.
- Frozen geometry-compatible Class A subset: 38/103 (36.89%).
- Support by run: seed2 10, seed3 10, seed5 7, seed6 5, seed8 6.
- Support by checkpoint: step14k 16, step72k 12, step143k 10.
- All prespecified geometry-match support gates pass.

No raw geometry outcome, geometry-conditioned residual, regression coefficient,
or sign-reversal result was inspected before this freeze. The raw extractor
necessarily recomputes top-1 flips for integrity and required Metric D, but the
outcome-blind matcher neither reads nor emits them.

