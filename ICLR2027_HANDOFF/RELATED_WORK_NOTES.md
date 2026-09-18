# Related-work notes

This file only includes literature already verified and preserved by ARC-012 or already cited in the manuscript. The full collision matrix and search log are in `logs/arc_records/ARC-012/`.

## 1. Layer ablation, dropping, and redundancy

- **Gabriel Garcia (2026), “No Free Swap: Protocol-Dependent Layer Redundancy in Transformers,” arXiv:2605.16234v2.** https://arxiv.org/abs/2605.16234. Top novelty threat. It already shows output-grounded layer-equivalence/protocol gaps changing across Pythia checkpoints. Cited in Introduction. Candidate A adds independent-run/two-stream replication and prospective block/noise KL/NLL matching, not the broad phenomenon.
- **Vedang Lad, Jin Hwa Lee, Wes Gurnee, Max Tegmark (NeurIPS 2025), “The Remarkable Robustness of LLMs: Stages of Inference?”** https://proceedings.neurips.cc/paper_files/paper/2025/hash/bcad07d4bfab51243efaa08b8ed475b3-Abstract-Conference.html. Close static block deletion/swapping and relative-accuracy metric. Cited in Introduction.
- **Xin Men et al. (Findings ACL 2025), “ShortGPT: Layers in Large Language Models Are More Redundant Than You Expect.”** https://aclanthology.org/2025.findings-acl.1035/. Static block influence/depth pruning. Related Work; not a direct training/matching collision.

## 2. Prediction disagreement, pruning, and quantization

- **Bjorn Deiseroth et al. (NAACL 2024), “Divergent Token Metrics: Measuring Degradation to Prune Away LLM Components—and Optimize Quantization.”** https://aclanthology.org/2024.naacl-long.377/. Its divergent-token rate is mathematically equivalent to `1-S` on identical positions. Metric novelty threat; cited where `S` is defined.
- **Albert Catalan-Tatjer, Niccolo Ajroldi, Jonas Geiping (ICLR 2026), “Training Dynamics Impact Post-Training Quantization Robustness.”** https://arxiv.org/abs/2510.06213. Establishes training-dependent perturbation robustness in another intervention regime. Broad fragility novelty threat; cited.

## 3. Activation intervention and mechanistic interpretability

- **Fred Zhang and Neel Nanda (2023), “Towards Best Practices of Activation Patching in Language Models: Metrics and Methods.”** https://arxiv.org/abs/2309.16042. Shows metric/method dependence in activation patching; methodological background, cited.
- **Aleksandar Makelov, George Lange, Atticus Geiger, Neel Nanda (ICLR 2024), “Is This the Subspace You Are Looking For? An Interpretability Illusion for Subspace Activation Patching.”** https://openreview.net/forum?id=Ebt7Qd7Jwy. Intervention/subspace interpretability caution; cited.
- **Cody Rushing and Neel Nanda (ICML 2024), “Explorations of Self-Repair in Language Models.”** https://proceedings.mlr.press/v235/rushing24a.html. Relevant to architecture/prompt-specific response and self-repair; cited.
- **Tao Ren, Xiaoyu Luo, Qiongxiu Li (2026), “APEX: Probing Neural Networks via Activation Perturbation.”** https://arxiv.org/abs/2602.03586. Layer-specific activation sweeps and output transitions; adjacent, cited.

## 4. Matched intervention audits

- **Daming Luo, Christy Liang, Junyu Xuan (2026), “SteerCheck: Attribution Specificity and Alignment Leakage in Activation-Steering Audits.”** https://arxiv.org/abs/2608.24335. Strong methodological collision: prospective matched off-target KL and retained comparator/direction structure. Candidate A cannot claim matched-KL auditing as new. Cited in Introduction/Related Work.

## 5. Robustness, sensitivity, and perturbation magnitude

- **Orion Reblitz-Richardson (2026), “When Probing Accuracy Saturates, Fragility Resolves.”** https://arxiv.org/abs/2606.11375. Activation-noise fragility across pretraining checkpoints; training-fragility context, cited.
- **Taeyeong Kim, Ahhyun Kim, TaeHyeon Kim, Unggi Lee (2026), “Not the Dimension, the Norm.”** https://arxiv.org/abs/2608.01624. Norm-matched weight perturbations; forces Candidate A's magnitude conclusion to remain assay-bounded. Cited.
- **Hendrik Borras, Bernhard Klein, Holger Froning (2022), “Walking Noise.”** https://arxiv.org/abs/2212.10430. Layer-specific additive/multiplicative noise and learning dynamics. Adjacent antecedent, cited.

## 6. Model/provenance background

- **Stella Biderman et al. (ICML 2023), “Pythia: A Suite for Analyzing Large Language Models Across Training and Scaling.”** https://proceedings.mlr.press/v202/biderman23a.html. Model suite, cited.
- **Oskar van der Wal et al. (ICLR 2025), “Stability and Outliers across Fifty Language Model Pre-Training Runs.”** https://arxiv.org/abs/2503.09543. PolyPythias independent-run provenance; recorded in ARC-003 provenance and should be cited when describing replicas.

## Local-neighborhood conclusion

The broad phenomenon and metric are occupied. The paper's remaining novelty is a moderate controlled replication-and-qualification combination. ARC-012 rates novelty `BORDERLINE` with high audit confidence. No “first” claim should be introduced without a fresh targeted audit.
