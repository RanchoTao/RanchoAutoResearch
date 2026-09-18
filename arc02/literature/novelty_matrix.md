# ARC-02 novelty matrix

Audit date: 2026-08-24. “Depth” means semantic derivation/composition depth, not
network depth or training time. This distinction is central to the collision test.

| Paper | Year | Model | Task | Circuit Method | Vary Reasoning Depth? | Causal Intervention? | Relevant Finding | Collision Risk |
|---|---:|---|---|---|---|---|---|---|
| [Progress measures for grokking via mechanistic interpretability](https://arxiv.org/abs/2301.05217) | 2023 | tiny Transformer | modular addition | Fourier reverse engineering, ablation | No; varies training time | Yes | Apparent abrupt grokking is explained by smooth circuit formation and cleanup. Strong warning against calling a behavioral kink a structural transition. | High conceptual, low task-depth collision |
| [Interpretability in the Wild: IOI circuit](https://arxiv.org/abs/2211.00593) | 2022 | GPT-2 small | indirect-object identification | path patching, head ablation | No | Yes | Defines a sparse head circuit and evaluates faithfulness/completeness/minimality. | Medium method collision |
| [Towards Automated Circuit Discovery (ACDC)](https://arxiv.org/abs/2304.14997) | 2023 | GPT-2-scale | IOI, greater-than, docstring | activation patching, edge pruning | No | Yes | Automated task-specific circuit extraction; circuit depends on metric, corruption, and granularity. | Medium method collision |
| [Towards Best Practices of Activation Patching](https://arxiv.org/abs/2309.16042) | 2023 | multiple LMs | localization tasks | activation patching variants | No | Yes | Metrics and corruption choices can yield disparate localization results. | High validity threat |
| [Does Circuit Analysis Interpretability Scale?](https://arxiv.org/abs/2307.09458) | 2023 | Chinchilla family | multiple-choice tasks | direct/total effects, patching | No | Yes | Patching can induce downstream compensation and returns a cut through, not necessarily the full causal computation. | High validity threat |
| [Backward Chaining Circuits in a Transformer](https://openreview.net/forum?id=WELOe7SPHK) | 2024 | small trained Transformer | tree path finding | manual circuit analysis, activation/weight analysis, ablation | Task contains bounded multi-step paths, but no depth-indexed circuit curve | Yes | Identifies a depth-bounded recurrent/backward-chaining mechanism. | High nearest-neighbor |
| [Grokking of Implicit Reasoning in Transformers](https://arxiv.org/abs/2405.15071) | 2024 | small Transformers | relation composition and comparison | training dynamics, head/component ablation | Compositional reasoning is studied, but circuit change is over training | Yes | Generalizing circuits form during grokking; systematicity depends on their configuration. | High conceptual |
| [How Capable Can a Transformer Become?](https://openreview.net/forum?id=KIhFggzePM) | 2023 | small Transformers | composed synthetic functions | layer/head importance analyses | Yes, behaviorally | Limited | Later attention layers are important for compositionality; not a causal minimal-circuit transition study. | Medium-high |
| [Towards Understanding Fine-Tuning Mechanisms via Circuit Analysis](https://proceedings.mlr.press/v267/wang25ak.html) | 2025 | fine-tuned LLMs | mathematical tasks and compositions | circuit extraction at checkpoints | Varies task complexity, not a controlled hop sweep | Yes | Nodes remain similar while edges change during fine-tuning; combines subtask circuits for composition. | High nearest-neighbor |
| [A Implies B: Circuit Analysis in LLMs](https://papers.neurips.cc/paper_files/paper/2025/file/2c4477572f06102b2ae3bd2b2ffcebf9-Paper-Conference.pdf) | 2025 | Mistral-7B, Gemma-2 9B/27B | minimal propositional reasoning | causal mediation, head analysis/ablation | No long-chain sweep; explicitly leaves longer chains open | Yes | Finds analogous sparse modular circuits across three pretrained models. | Very high nearest-neighbor |
| [Towards a Mechanistic Understanding of Propositional Logical Reasoning](https://arxiv.org/abs/2601.04260) | 2026 | Qwen3 8B/14B | 11 rule categories, one- and two-hop | activation patching, zero ablation, head pattern classification | One vs two hops only | Yes | Similar staged information flow across the two depths, but two-hop patching magnitudes are substantially lower. No size/overlap/change-point test. | Very high nearest-neighbor |
| [Mechanistic Unveiling of Transformer Circuits](https://arxiv.org/abs/2502.09022) | 2025 | GPT-2 | IOI framed as multi-step reasoning | circuit analysis, self-influence | No controlled depth sweep | Partial | Maps token influence through layers but does not establish a depth-conditioned minimal causal circuit. | Medium |
| [Hypothesis Testing the Circuit Hypothesis](https://arxiv.org/abs/2410.13032) | 2024 | published and synthetic circuits | six circuit case studies | formal faithfulness/localization/minimality tests | No | Yes | Real discovered circuits satisfy idealized circuit properties only to varying degrees. | High validity threat |
| [Transformers Learn Shortcuts to Automata](https://arxiv.org/abs/2210.10749) | 2022 | small Transformers | finite-state automata | theoretical construction, behavioral probes | Sequence/computation length | Not component-causal | Transformers can learn logarithmic- or constant-depth shortcut solutions rather than literal recurrent steps. | High alternative mechanism |
| [Is Grokking Worthwhile?](https://arxiv.org/abs/2601.09049) | 2026 | small Transformers | compositional factual reasoning | functional circuit analysis | Varies training regime, not systematic inference depth | Yes | Grokked and non-grokked models can share inference paths; circuit appearance and generalization need not coincide. | High falsification prior |
| [The Computational Complexity of Circuit Discovery](https://arxiv.org/abs/2410.08025) | 2024 | formal neural networks | circuit discovery queries | theoretical | No | N/A | Many exact minimal-circuit queries are intractable; any empirical “minimal circuit” is method-relative. | Medium validity threat |

## Direct collision assessment

The closest papers cover three neighboring axes separately:

1. **Training-time phase changes:** Nanda et al., Wang et al. (2024), and He et
   al. track how circuits form or compete over optimization time.
2. **Reasoning mechanisms at fixed or shallow depth:** Brinkmann et al. and Hong
   et al. recover causal reasoning circuits, while Chen et al. compare one- and
   two-hop patterns.
3. **Circuit-method reliability:** Zhang & Nanda and Shi et al. show that a
   circuit is conditional on the patching design and may fail minimality or
   localization tests.

No audited paper jointly reports a controlled depth sweep of at least four
levels, accuracy/length matching, two intervention methods, cross-depth circuit
overlap, and formal smooth-versus-change-point model comparison. This is a
narrow gap, not evidence that a phase transition exists.

