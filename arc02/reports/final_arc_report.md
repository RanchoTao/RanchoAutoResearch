# ARC-02 final report

## A. Question

Does a small Transformer’s causally sufficient reasoning circuit reorganize
abruptly, rather than expand smoothly, as controlled relational reasoning depth
increases from one to five hops?

## B. Novelty

**Novelty status: YELLOW.** The nearest literature leaves a narrow opening but
creates substantial collision and validity risk:

1. [Progress measures for grokking](https://arxiv.org/abs/2301.05217) explains
   an apparently abrupt behavioral transition through continuous circuit
   formation over training. It varies training time, not inference-task depth.
2. [Backward Chaining Circuits](https://openreview.net/forum?id=WELOe7SPHK)
   causally identifies a depth-bounded recurrent mechanism in a small Transformer,
   but does not estimate a depth-indexed circuit-size/overlap curve or change point.
3. [Grokking of Implicit Reasoning](https://arxiv.org/abs/2405.15071) studies
   generalizing circuits for relation composition, but again follows their
   formation over training rather than circuit topology across matched depths.
4. [Towards Understanding Fine-Tuning Mechanisms via Circuit Analysis](https://proceedings.mlr.press/v267/wang25ak.html)
   compares circuits across task complexities/checkpoints and shows stable nodes
   with changing edges, but not a controlled hop-depth phase-transition test.
5. [A Implies B](https://papers.neurips.cc/paper_files/paper/2025/file/2c4477572f06102b2ae3bd2b2ffcebf9-Paper-Conference.pdf)
   finds analogous sparse causal logic circuits across Mistral/Gemma models and
   explicitly leaves longer chains open.
6. [Towards a Mechanistic Understanding of Propositional Logical Reasoning](https://arxiv.org/abs/2601.04260)
   compares one- and two-hop Qwen3 mechanisms, finding similar staged computation
   but lower patching magnitude at two hops; it does not test circuit size,
   overlap, or a change point over four or more depths.
7. [Towards Best Practices of Activation Patching](https://arxiv.org/abs/2309.16042)
   shows that patching metric/corruption choices can produce disparate
   localization results. This is a direct threat to ARC-02’s measurement claim.
8. [Hypothesis Testing the Circuit Hypothesis](https://arxiv.org/abs/2410.13032)
   shows that discovered circuits satisfy faithfulness, localization, and
   minimality criteria only to varying degrees.
9. [ACDC](https://arxiv.org/abs/2304.14997) automates circuit extraction but
   demonstrates that a circuit is conditional on task metric, corruption, and
   graph granularity.
10. [Transformers Learn Shortcuts to Automata](https://arxiv.org/abs/2210.10749)
    supplies an alternative mechanism: shallow Transformers can learn parallel
    shortcuts rather than literal one-layer-per-step computation.

The unoccupied narrow question was a 4+ level, accuracy/length-matched depth
sweep with two causal methods and explicit smooth-versus-piecewise comparison.
The experiment below fills that protocol gap but does not find the proposed
phase transition.

## C. Experiment

### Task and controls

- Synthetic directed relation chain with seven graph edges: six chain edges and
  one disconnected distractor.
- Query depths 1–5, jointly trained in one model.
- Identical vocabulary, 10-token sequence length, edge count, distractor count,
  and depth frequency across conditions.
- Each edge is one directed-pair token, matching the controlled representation
  used in the closest backward-chaining work.
- Clean/corrupt activation-patching pairs use the exact same graph and differ
  only in query start entity; both answers are programmatically exact.
- Circuit analyses use only pairs that the full model answers correctly in both
  clean and corrupt conditions.

### Model and training

- Custom, fully intervenable encoder Transformer.
- 10 layers, 4 independent attention heads/layer, one MLP/layer.
- 1,688,208 parameters; 50 intervenable components total.
- 100,000 newly generated training examples per epoch to prevent finite-set
  memorization; 5,000 fixed validation examples.
- Seeds 11, 23, and 37.
- NVIDIA RTX 5060 Laptop GPU; successful runs used 414.6 seconds total and at
  most 802,075,648 CUDA-allocated bytes. Two earlier accuracy-gated designs were
  rejected before circuit analysis.

### Circuit definition

For each depth and discovery method, components were greedily added in score
order until the retained subnetwork reached at least 90% of full-model accuracy.
Components were attention-head outputs and MLP outputs. Two independent rankings
were used:

1. activation patching from clean into corrupt runs;
2. single-component zero ablation on clean runs.

The selected set was then removed jointly to test causal necessity. Fifty
size-matched random retained/ablated sets were evaluated per depth and method.

### Phase-transition test

Circuit size was modeled using linear, quadratic, and continuous piecewise-linear
fits. Three-seed aggregation used seed fixed effects. BIC counts selection of the
piecewise breakpoint as a parameter. Adjacent circuit Jaccard, layer entropy,
layer centroid, and linear CKA were supporting diagnostics.

## D. Main results

### Accuracy control

All 15 seed-by-depth validation accuracies were between **0.987 and 1.000**.
Mean accuracies at depths 1–5 were **0.9987, 0.9987, 0.9997, 0.9937, 0.9923**.
The result therefore cannot be attributed to an accuracy cliff.

### Circuit size (mean ± seed SD, out of 50 components)

| Depth | Activation patching | Zero ablation | Ablation-defined sparsity |
|---:|---:|---:|---:|
| 1 | 24.0 ± 6.6 | 26.3 ± 4.5 | 47.3% |
| 2 | 32.3 ± 10.3 | 32.3 ± 2.3 | 35.3% |
| 3 | 41.3 ± 4.2 | 40.0 ± 2.0 | 20.0% |
| 4 | 42.0 ± 4.6 | 35.0 ± 5.6 | 30.0% |
| 5 | 46.7 ± 3.1 | 39.7 ± 1.5 | 20.7% |

Deeper tasks generally required more of the model, but the causal-ablation curve
was non-monotonic at depth 4 and no common discontinuity appeared.

### Model comparison

| Discovery method | Linear BIC | Quadratic BIC | Piecewise BIC | Interpretation |
|---|---:|---:|---:|---|
| Activation patching | **58.36** | 58.67 | 60.63 | Linear is preferred; no breakpoint evidence. |
| Zero ablation | 51.83 | 50.84 | **50.81** | Delta BIC < 1.1: models are indistinguishable. |

Per-seed fits were inconsistent. For zero ablation, seed 23 preferred a
piecewise breakpoint at depth 3, while seeds 11 and 37 preferred linear fits.
For patching, seeds 11 and 23 preferred breakpoint 2 but seed 37 preferred
linear; its depth-2 circuit was smaller than depth 1.

### Topology, localization, and causal necessity

- Mean adjacent Jaccard increased from **0.466 to 0.860** under patching and
  from **0.528 to 0.777** under zero ablation as depth increased. A deeper
  transition should instead produce a reproducible overlap collapse.
- Cross-method Jaccard increased from **0.578 at depth 1** to **0.812 at depth
  5**; the strongest apparent early breakpoint is precisely where the two
  methods agree least.
- Normalized layer-distribution entropy was **0.945–0.991**, so the circuits
  were distributed rather than localized. Layer centroid moved
  3.96→5.05→4.62→4.90→4.78, with no monotonic migration to later layers.
- Retaining the ablation-ranked circuits preserved mean accuracy
  **0.907–0.932**. Removing them reduced accuracy to **0.110–0.165**, confirming
  necessity of the large selected sets.
- However, matched random ablations also reduced accuracy to **0.139–0.236**.
  Once 60–80% of all components are removed, destruction is not specific
  evidence for a localized reasoning circuit.
- Final-layer adjacent-depth CKA was low (mean 0.11–0.25), showing that outputs
  are depth-specific, but this representational difference did not align with a
  reproducible causal-circuit change point.

## E. Figures

1. `figures/aggregate_circuit_size_3seeds.png`
2. `figures/aggregate_adjacent_overlap_3seeds.png`
3. `figures/aggregate_layer_depth_heatmap_3seeds.png`
4. `figures/aggregate_causal_performance_3seeds.png`
5. `figures/figure5_representation_cka.png` (last-seed diagnostic; aggregate
   numbers are in `results/aggregate_results.json`)

## F. Negative evidence

1. A visually sharp seed-11 patching jump at depth 2 disappeared as a robust
   model-selection result after changing method and adding seeds.
2. Patching and zero-ablation circuit sets showed low agreement in the regime
   that looked most transition-like.
3. Breakpoints were neither method-consistent nor seed-consistent.
4. Adjacent overlap rose with depth, supporting nested expansion/reuse rather
   than circuit replacement.
5. Layer localization did not shift abruptly and remained high-entropy.
6. The operational circuits became very large (often 35–47 of 50 components),
   weakening the claim that a sparse, localized reasoning circuit was found.
7. Matched random ablations became almost as destructive as targeted ablations
   at large circuit sizes.
8. Two initial serializations failed the >95% accuracy gate. They were recorded,
   not analyzed as circuit evidence.

## G. Current verdict

```text
KILL
```

This kills the current claim that controlled reasoning depth produces a
reproducible causal-circuit phase transition in this small-Transformer regime.
It does not claim that no architecture, training regime, or task can ever show
such a transition.

## H. Why

1. No clear seed-adjusted BIC support for a piecewise size curve.
2. Breakpoint identity and model preference change across seeds and methods.
3. Topological overlap increases rather than collapses at deeper depths.
4. Accuracy, sequence length, vocabulary, edge count, and distractors were
   controlled, removing the easiest confounds.
5. Apparent positive evidence is strongest under the more corruption-sensitive
   activation-patching definition.
6. The selected subnetworks are too distributed and large to substantiate a
   sparse localized-circuit transition.
7. Scaling the same design would have low expected information gain relative to
   the compute and analysis cost.

## I. Next experiments (only if a new ARC is opened)

Ranked by expected information gain per GPU-hour:

1. **Method-robustness study (highest):** pre-register a fixed circuit target and
   compare activation patching, causal scrubbing, edge attribution/IG, and
   deletion-based pruning on the same matched graphs. The claim would be about
   false change points caused by circuit definitions, not about discovering a
   phase transition.
2. **Second task family:** repeat the frozen protocol on non-commutative function
   composition. This tests whether the one-hop/multi-hop expansion is relation-
   graph specific.
3. **Architecture replication:** use the published six-layer backward-chaining
   checkpoint and a width-matched independently trained model, with depth held
   below each model’s accuracy ceiling.

These are not authorized continuations of the killed ARC and were not run.

## J. Paper potential

```text
workshop
```

As a phase-transition paper, the current result has no main-conference case. A
larger, pre-registered study showing that popular circuit discovery methods
systematically manufacture incompatible change points could become a useful
mechanistic-interpretability methods paper, but that is a different claim.

## Reproducibility map

- Environment: `reports/environment_audit.md`
- Novelty matrix: `literature/novelty_matrix.md`
- Full iteration log: `reports/research_log.md`
- Source: `src/`
- Frozen configs: `configs/`
- Per-seed metrics/checkpoints: `experiments/`
- Aggregate table/JSON: `results/`
- Figures: `figures/`

