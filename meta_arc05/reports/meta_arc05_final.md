# META-ARC-05 — RTX5060 final report

## Search

- Anchors screened: **25**.
- Minimally viable after archival/compute/competence screening: **7**.
- Top five: layer deletion; NODE zero-shot symmetry breaking; continual-TTA
  collapse; random-feature weak-to-strong; quantization training dynamics.
- Selected: **single-layer deletion robustness**.

## Source anchor

[Lad, Gurnee & Tegmark, “The Remarkable Robustness of LLMs: Stages of
Inference?”, NeurIPS 2025](https://proceedings.neurips.cc/paper_files/paper/2025/hash/bcad07d4bfab51243efaa08b8ed475b3-Abstract-Conference.html).
The paper reports 72–95% intact top-1 retention after deleting/swapping layers.

## Competence and replication

**PASS / PASS.** On Pythia-410M, intact WikiText perplexity is 28.7–30.1 across
three shards. Middle-layer deletion retains 0.759–0.764 top-1 agreement, versus
0.589–0.600 for early/final boundary layers. All preregistered gates pass on
20,736 scored positions.

## Boundary result

Selected variable: **pretraining progress**. On Pythia-160M, after competence
begins, mean middle-layer top-1 agreement declines monotonically:

| Checkpoint | 1k | 10k | 50k | 143k |
|---|---:|---:|---:|---:|
| Agreement | 0.694 | 0.665 | 0.651 | 0.568 |
| Intact NLL | 5.214 | 3.900 | 3.752 | 3.782 |

The direction holds strictly in all three text shards (Spearman step/agreement
rho = -1.0). Step0 is not included in that law: random logits have low top-1
agreement (0.258) despite negligible excess NLL, because near-tied argmaxes are
unstable. The result is therefore an early peak followed by post-competence erosion,
not a monotone law from initialization and not a phase transition.

## Confound control

From step1k to step143k, agreement declines within every intact-confidence bin.
The first four bins decline by 0.233–0.290 with thousands of pooled layer-token
observations; the highest-confidence bin declines by 0.015. From 50k to 143k,
agreement drops another 0.082 while intact NLL is nearly flat/slightly worse
(3.752→3.782), so neither confidence nor simple competence explains the full effect.

## Held-out prediction

**PASS.** Before evaluation, Pythia-70M was predicted to show ≥0.05 lower
agreement at 143k than 1k in every shard. Observed declines were 0.131, 0.107,
and 0.131 (mean 0.397→0.274). Final intact NLL is 4.33–4.43, passing competence.
All five confidence bins decline; four decline by 0.110–0.213.

## Decision

**GO**, not STRONG-GO. Evidence supports a new, prospective, confidence-controlled
training-dynamics fact at two Pythia scales. It is not yet cross-architecture or
downstream validated, so the broader paper claim remains locked and provisional.

## Resources

- Paid API cost: **USD 0**.
- No model training; public checkpoint inference only.
- Conservative model-load plus inference timer upper bound, including the discarded
  undersized replication: **approximately 15.6 minutes**. Actual GPU-active time
  is lower because checkpoint downloads/model loading are included.
- Peak allocated CUDA memory: **1,541,403,648 bytes (~1.44 GiB)**.
- End-to-end wall time: **approximately 60 minutes**.

## Recommended next action

Stop this exploratory run. The single highest-value promotion experiment is a
preregistered early/final checkpoint comparison on a non-Pythia model family with
public trajectories, plus one competent downstream task. Failure there should be
`KILL-GENERALIZATION`; success would justify mechanism work on residual-update
norms and block substitutability.
