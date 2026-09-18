# Prospective held-out pretraining-run prediction

Frozen: 2026-08-26T02:18:06+08:00, after seeds 1-8 were analyzed and before
any seed9 model-weight download, deletion inference, or raw result existed.

- **Held-out model:** `EleutherAI/pythia-160m-seed9`.
- **Predicted endpoint sign:** negative.
- **Expected late-minus-early delta range:** `[-0.134625, -0.063661]`.
- **Range rule:** Tukey inner fence from the eight discovery-run deltas:
  `Q1 - 1.5 * IQR` through `Q3 + 1.5 * IQR`; `Q1 = -0.108013`,
  `Q3 = -0.090272`, and `IQR = 0.017741`.
- **Discovery mean:** `-0.101600`; discovery median: `-0.100239`.
- **Discovery run-level bootstrap 95% interval:** `[-0.109928, -0.094084]`.
- **Discovery sign count:** 8 / 8 independent training runs negative.
- **Expected trajectory:** broad decline across normalized progress, without
  requiring strict checkpoint-by-checkpoint monotonicity.
- **Held-out primary PASS:** `S(step143000) - S(step14000) < 0`.
- **Range diagnostic:** report separately whether the held-out point falls
  inside the frozen numeric range; the sign, not the Tukey fence, is primary.

The held-out repository contained only `main` and `config.json` in the local
cache at the time this prediction was written. No model weights or run9 result
were present.

