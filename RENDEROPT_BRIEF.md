# RenderOpt Research Brief

## Objective

Develop a scientifically serious project aimed at a competitive ICLR 2027 submission, provisionally titled:

**RenderOpt: Optimizing Semantically Equivalent Visual Representations for Multimodal Reasoning**

Central question: for identical underlying semantic information, can we characterize machine-specific visual preferences in multimodal large language models (MLLMs) and automatically optimize visual representations for machine reasoning?

## Core Hypothesis

MLLMs have stable but non-human-equivalent preferences over visual encoding and rendering choices. Semantically equivalent visualizations may produce substantial differences in reasoning accuracy, calibration, robustness, consistency, latency, and token cost. Some preferences may transfer across model families, enabling machine-oriented visualization principles and automatic rendering optimization.

Treat this as a falsifiable hypothesis, not an assumed fact.

## Research Questions

1. **Rendering sensitivity:** How much does MLLM performance vary across semantically equivalent visual representations of identical data?
2. **Machine visual encoding preferences:** Are there stable rankings or response surfaces for position, length, area, color, shape, ordering, aspect ratio, resolution, labeling, redundancy, and layout?
3. **Cross-model transfer:** Do renderings optimized for one MLLM improve other MLLMs, or are optima model-specific?
4. **Automatic rendering optimization:** Can black-box optimization over rendering parameters improve held-out multimodal reasoning performance?

## Initial Experimental System

Start with controlled chart and data-visualization reasoning because semantic instances, renderings, questions, and exact answers can be generated programmatically.

The system should:

- generate underlying datasets and exact programmatic ground-truth answers;
- render each semantic instance through multiple controlled visual encodings;
- enforce semantic equivalence and document invariants across compared renderings;
- evaluate multiple vision-language models only where computationally and financially feasible;
- measure accuracy, calibration, robustness, consistency, and, when observable, latency and token cost;
- compare within-model, cross-model, and universal visual preferences;
- use paired statistical tests, hierarchical or mixed-effects analysis where appropriate, confidence intervals, and multiple-comparison controls;
- include random search and human-standard visualization choices as baselines;
- investigate black-box optimization of rendering parameters;
- test held-out data distributions, question types, semantic instances, and rendering configurations.

## Immediate Literature and Novelty Audit

Do not claim novelty until primary sources have been retrieved and verified. Explicitly investigate at minimum:

- *Toward a Machine Bertin: Why Visualization Needs Design Principles for Machine Cognition*
- *EncQA: Benchmarking Vision-Language Models on Visual Encodings for Charts*
- CharXiv
- ChartQA, PlotQA, and FigureQA
- *Benchmarking Multimodal Large Language Models for Scientific Visualization Literacy*
- *Chart Deception in Vision-Language Models*
- GraphVerse
- relevant 2025-2026 primary work on chart understanding, visualization literacy, visual prompting, chart robustness, and machine-oriented visualization.

The audit must identify the strongest nearest-neighbor papers and create an explicit comparison table covering their task, semantic-equivalence controls, rendering search space, models, evaluation protocol, transfer analysis, optimization method, and released artifacts. Clearly state what RenderOpt would contribute beyond each neighbor. If active rendering optimization, held-out transfer, or another claimed component already exists, narrow or change the contribution rather than overstating novelty.

## Required Contribution Structure

The intended contribution is not merely another visualization-literacy benchmark. It should move from passive evaluation toward active representation optimization:

1. empirical phenomenon: equivalent representations cause large and systematic MLLM performance differences;
2. characterization: machine-oriented visual encoding preferences;
3. transfer analysis: universal versus model-specific preferences;
4. method: automatic optimization of rendering parameters for multimodal reasoning;
5. benchmark/protocol: reproducible semantic-instance generation, rendering, evaluation, and optimization framework.

## Pre-Experiment Decision Rule

Before any expensive experiment:

1. complete a thorough literature and novelty audit using verified citations;
2. identify and compare the strongest nearest neighbors;
3. state precise contribution deltas and risks;
4. design the smallest inexpensive pilot capable of falsifying the central hypothesis;
5. predefine success, null, and stop/redirect criteria.

The pilot must use real executable evaluation, exact ground truth, paired semantic instances, controlled equivalent renderings, and enough repetitions for uncertainty estimates. It must not use simulated model answers, fabricated metrics, fabricated citations, or graceful fallback. Scale model count, task breadth, rendering search, or API spend only after the pilot shows a credible and reproducible signal.

## Quality Bar

Optimize for scientific significance, falsifiability, experimental rigor, tractable compute, reproducibility, and completion before the ICLR 2027 submission deadline. Avoid benchmark sprawl, uncontrolled prompt changes, post-hoc metric selection, leakage between optimization and evaluation instances, and conclusions that conflate a single model's preference with a universal principle.
