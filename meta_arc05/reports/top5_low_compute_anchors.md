# TOP-5 low-compute anchors

Ranking dimensions (1–5): reproducibility, surprise, boundary potential, compute
efficiency, unresolvedness, realistic relevance. Scores are judgment aids rather
than a claim of novelty.

| Rank | Anchor | Repro | Surprise | Boundary | Compute | Unresolved | Realism |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | ANCHOR-01 layer deletion | 5 | 5 | 5 | 5 | 4 | 5 |
| 2 | ANCHOR-02 NODE symmetry breaking | 3 | 5 | 4 | 5 | 3 | 3 |
| 3 | ANCHOR-14 TTA collapse | 4 | 4 | 4 | 4 | 3 | 5 |
| 4 | ANCHOR-04 weak-to-strong random features | 4 | 5 | 3 | 5 | 2 | 3 |
| 5 | ANCHOR-24 quantization dynamics | 4 | 4 | 3 | 4 | 2 | 5 |

## 1. ANCHOR-01 — layer-deletion robustness

- **Original result:** deleting/swapping a Transformer layer retains 72–95% of
  the unmodified LM’s top-1 predictions; deeper models are more robust.
- **Source:** [Lad, Gurnee & Tegmark, NeurIPS 2025](https://proceedings.neurips.cc/paper_files/paper/2025/hash/bcad07d4bfab51243efaa08b8ed475b3-Abstract-Conference.html),
  with [official code](https://github.com/vdlad/Remarkable-Robustness-of-LLMs).
- **Why unresolved:** final-checkpoint depth profiles do not determine whether
  redundancy is architectural, acquired continuously, or appears only after LM
  competence.
- **Replication cost:** 10–25 GPU min with the paper’s Pythia-410M model.
- **Potential boundary variable:** pretraining checkpoint age.
- **Competing predictions:** residual architecture predicts high robustness at
  initialization; learned distributed computation predicts robustness rises with
  training; specialization predicts it falls as blocks become necessary.
- **Scientific interest:** distinguishes built-in residual tolerance from learned
  redundancy and tells pruning work when robustness develops.
- **KILL:** failure to reproduce ≥72% middle-layer top-1 agreement, or checkpoint
  effects fully explained by baseline token confidence/NLL.

## 2. ANCHOR-02 — zero-shot broken-symmetry recovery

- **Original result:** context-conditioned NODEs trained only pre-bifurcation
  recover post-bifurcation dynamics without physics priors.
- **Source:** [Huh, Jeong & Alam, ICML 2025](https://proceedings.mlr.press/v267/huh25a.html).
- **Why unresolved:** the minimum pre-bifurcation context span needed for recovery
  is not summarized as an empirical boundary.
- **Replication cost:** 10–40 GPU min.
- **Potential boundary variable:** span/density of pre-bifurcation environments.
- **Competing predictions:** coefficient identifiability predicts a sharp failure
  when span is narrow; topology-based invariance predicts robust recovery.
- **Scientific interest:** separates interpolation of parameterized vector fields
  from genuine topological extrapolation.
- **KILL:** direct polynomial/regression baseline matches NODE, or the proposed
  boundary is already a corollary of the paper’s recovery conditions.

## 3. ANCHOR-14 — entropy-minimization collapse in continual TTA

- **Original result:** standard entropy minimization may collapse to a single
  predicted class on continual corruption streams.
- **Source:** [Han, Na & Hwang, ICML 2025](https://proceedings.mlr.press/v267/han25e.html).
- **Why unresolved:** it is unclear whether collapse is controlled by shift
  severity or by temporal class-mixing rate.
- **Replication cost:** 20–60 GPU min with CIFAR-C/small ResNet.
- **Potential boundary variable:** class mixing window of the test stream.
- **Competing predictions:** entropy severity predicts corruption strength;
  feedback-loop theory predicts low class diversity even at matched corruption.
- **Scientific interest:** a deployment-relevant stability law for online TTA.
- **KILL:** trivial batch-class imbalance directly explains everything or a
  competent public checkpoint cannot reproduce collapse.

## 4. ANCHOR-04 — weak-to-strong random-feature learning

- **Original result:** an early-stopped larger random-feature student can
  outperform the weak teacher that supplies every training label.
- **Source:** [Medvedev et al., ICML 2025](https://proceedings.mlr.press/v267/medvedev25a.html).
- **Why unresolved:** scalar teacher error does not describe whether errors align
  with directions visible to the student.
- **Replication cost:** <5 min, mostly CPU.
- **Potential boundary variable:** spectral alignment of teacher error.
- **Competing predictions:** kernel filtering predicts a smooth spectral law;
  label-noise intuition predicts only error magnitude matters.
- **Scientific interest:** tells when weak supervision is correctable.
- **KILL:** boundary follows directly from the paper’s arbitrary-feature theorem
  or fails under a second activation/input generator.

## 5. ANCHOR-24 — quantization robustness over pretraining

- **Original result:** quantization degradation is governed jointly by validation
  loss and learning-rate decay, so better/later checkpoints need not quantize better.
- **Source:** [Training Dynamics Impact Quantization Degradation, NeurIPS 2025](https://neurips.cc/virtual/2025/126559).
- **Why unresolved:** public trajectories permit a cheap independent test, but
  the source already explains much of the interaction.
- **Replication cost:** 15–45 GPU min with Pythia-160M checkpoints.
- **Potential boundary variable:** schedule phase at matched full-precision NLL.
- **Competing predictions:** weight-range statistics versus optimization-noise phase.
- **Scientific interest:** checkpoint selection rule for low-bit deployment.
- **KILL:** effect vanishes under per-channel quantization or is just calibration
  sample noise.

## Selection

**ANCHOR-01** is selected. It uses an archival result, official code, the exact
paper model below 1B parameters, a realistic language-model behavior, and a
three-way boundary prediction whose outcomes are all informative. It is not
selected merely for ease: ANCHOR-04 is cheaper, but has much less unresolved space.

