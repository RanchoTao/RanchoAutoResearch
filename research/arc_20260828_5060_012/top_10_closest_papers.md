# Top 10 closest papers

Ranked by claim collision, not by general importance. Exactly ten papers met the
T3–T5 deep-read threshold.

## 1. TOP-1 CLOSEST PAPER — No Free Swap

**Gabriel Garcia.** “No Free Swap: Protocol-Dependent Layer Redundancy in
Transformers.” arXiv:2605.16234v2, 2026.
[Primary source](https://arxiv.org/abs/2605.16234)

- **Why close:** directly measures output-grounded layer equivalence across
  Pythia training checkpoints and compares replacement with interchange.
- **Exact overlap:** training changes a layer-intervention response; protocol
  differences grow; trajectory is heterogeneous rather than strictly monotone.
- **Exact difference:** no independent pretraining runs, exact block-bypass
  `S/Delta S`, dual-corpus replication, or prospective block/noise KL/NLL
  matching.
- **Threat:** T5. It subsumes the broad “training changes layer redundancy”
  framing.
- **Placement:** mandatory in the Introduction.
- **Deep-read anchors:** abstract and §1; protocol definitions in §3.1;
  checkpoint results in §4.4; scope/limitations in §6.

## 2. The Remarkable Robustness of LLMs: Stages of Inference?

**Vedang Lad, Jin Hwa Lee, Wes Gurnee, Max Tegmark.** NeurIPS 2025.
[Primary source](https://proceedings.neurips.cc/paper_files/paper/2025/hash/bcad07d4bfab51243efaa08b8ed475b3-Abstract-Conference.html)

- **Why close:** same interior-layer deletion/swapping setting and an intact
  versus intervened top-1 “relative accuracy” statistic.
- **Overlap:** block substitutability, KL/loss/entropy diagnostics, Pythia and
  other final pretrained LMs.
- **Difference:** static final checkpoints; no independent pretraining runs or
  prospective functional-damage matching.
- **Threat:** T4; destroys metric and static-phenomenon novelty.
- **Placement:** mandatory in the Introduction.
- **Deep-read anchors:** intervention definitions in §2; principal robustness
  results in §§3–4; limitations in §6.

## 3. SteerCheck

**Daming Luo, Christy Liang, Junyu Xuan.** “SteerCheck: Attribution Specificity
and Alignment Leakage in Activation-Steering Audits.” arXiv:2608.24335v1, 2026.
[Primary source](https://arxiv.org/abs/2608.24335)

- **Why close:** preregistered intervention audit with matched off-target KL and
  multiple null families.
- **Overlap:** prospective functional-budget matching and persistent
  family/alignment effects after KL control.
- **Difference:** activation steering specificity in Qwen3-14B, not block
  substitutability or pretraining trajectories.
- **Threat:** T4; weakens any methodological-first claim for matched KL or
  intervention-family residuals.
- **Placement:** mandatory in the Introduction.
- **Deep-read anchors:** audit design and matched budgets in §3; results in
  §§5–6; limitations in §8.

## 4. Divergent Token Metrics

**Bjorn Deiseroth, Max Meuer, Nikolas Gritsch, Constantin Eichenberg, Patrick
Schramowski, Matthias Assenmacher, Kristian Kersting.** NAACL 2024.
[Primary source](https://aclanthology.org/2024.naacl-long.377/)

- **Why close:** its divergent-token rate is the complement of `S` under the
  same teacher-forced positions.
- **Overlap:** next-token argmax disagreement as degradation from pruning or
  quantization.
- **Difference:** compression selection rather than checkpoint dynamics,
  independent runs, or family matching.
- **Threat:** T4; exact/equivalent metric collision.
- **Placement:** Introduction when defining the metric, plus Related Work.
- **Deep-read anchors:** metric definitions in §§3.3–3.5; evaluations in §4;
  conclusion/limitations.

## 5. Training Dynamics Impact Post-Training Quantization Robustness

**Albert Catalan-Tatjer, Niccolo Ajroldi, Jonas Geiping.** ICLR 2026.
[Primary source](https://arxiv.org/abs/2510.06213)

- **Why close:** dense checkpoint studies show that robustness to a model
  perturbation changes during pretraining.
- **Overlap:** small 70M/160M controlled models, many checkpoints, functional
  degradation under perturbation, and learning-rate-phase analysis.
- **Difference:** post-training quantization rather than block bypass or
  activation noise; no `Delta S` or family matching.
- **Threat:** T4; broad training-dependent fragility is not new.
- **Placement:** Introduction or central Related Work.
- **Deep-read anchors:** setup and robustness measures in §§3–4; trajectory
  results in §§5–6; schedule details in Appendix H.

## 6. When Probing Accuracy Saturates, Fragility Resolves

**Orion Reblitz-Richardson.** arXiv:2606.11375v2, 2026.
[Primary source](https://arxiv.org/abs/2606.11375)

- **Why close:** uses activation-noise fragility across 37 OLMo checkpoints as
  a pretraining-progress signal.
- **Overlap:** checkpoint trajectory, perturbation robustness, multiple split
  seeds, activation-scale confound, and a held-out larger model.
- **Difference:** probe fragility and one training trajectory, not block bypass,
  independent pretraining runs, or damage-matched families.
- **Threat:** T4; close training-fragility context.
- **Placement:** central Related Work; mention in Introduction if emphasizing
  checkpoint fragility.
- **Deep-read anchors:** metric and normalization in §§3.4–3.6; trajectories in
  §§4.2 and 4.4; cross-model scope in §5.3.

## 7. Not the Dimension, the Norm

**Taeyeong Kim, Ahhyun Kim, TaeHyeon Kim, Unggi Lee.** arXiv:2608.01624v1,
2026. [Primary source](https://arxiv.org/abs/2608.01624)

- **Why close:** directly studies norm-matched weight perturbations in language
  models and argues norm is the principal live factor in its adaptation regime.
- **Overlap:** raw perturbation magnitude, location, and functional outcomes.
- **Difference:** gradient-free adaptation objective, directions, models, and
  tasks differ; it does not study block deletion or matched KL/NLL.
- **Threat:** T4; forces Candidate A's raw-norm conclusion to remain assay-
  bounded rather than universal.
- **Placement:** central Related Work.
- **Deep-read anchors:** design in §3; norm/dimension/location results in §§4–6;
  limitations in §7.

## 8. Walking Noise

**Hendrik Borras, Bernhard Klein, Holger Froning.** arXiv:2212.10430, 2022.
[Primary source](https://arxiv.org/abs/2212.10430)

- **Why close:** compares additive and multiplicative, layer-specific noise and
  studies how noise robustness changes with learning.
- **Overlap:** activation/weight perturbation families, layer location, and
  training-dependent response.
- **Difference:** small classifiers and noisy-training adaptation rather than
  pretrained LMs or block-substitutability endpoints.
- **Threat:** T3; important antecedent, not a direct collision.
- **Placement:** Related Work.
- **Deep-read anchors:** perturbation protocol in §3; layer/training results in
  §§4–6.

## 9. ShortGPT

**Xin Men, Mingyu Xu, Qingyu Zhang, Qianhao Yuan, Bingning Wang, Hongyu Lin,
Yaojie Lu, Xianpei Han, Weipeng Chen.** Findings of ACL 2025.
[Primary source](https://aclanthology.org/2025.findings-acl.1035/)

- **Why close:** ranks Transformer blocks by input/output similarity and removes
  low-influence layers.
- **Overlap:** static layer redundancy and block removal in pretrained LMs.
- **Difference:** cosine Block Influence, final models, and pruning performance;
  no independent-run trajectory or intervention matching.
- **Threat:** T3; static redundancy background.
- **Placement:** Related Work.
- **Deep-read anchors:** Block Influence in §2; experiments in §§3–5.

## 10. APEX

**Tao Ren, Xiaoyu Luo, Qiongxiu Li.** “APEX: Probing Neural Networks via
Activation Perturbation.” arXiv:2602.03586, 2026.
[Primary source](https://arxiv.org/abs/2602.03586)

- **Why close:** activation perturbation sweeps characterize output transitions,
  layer dependence, and training biases.
- **Overlap:** layer-specific activation noise and output-distribution response.
- **Difference:** different models/endpoints; no Pythia checkpoint family
  matching or block bypass.
- **Threat:** T3; adjacent perturbation-measurement work.
- **Placement:** Related Work.
- **Deep-read anchors:** method in §3; results in §§4–6; stated limitations.
