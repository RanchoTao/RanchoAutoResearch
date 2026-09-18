# World Models under Structured Partial Observability

## Purpose and decision standard

This is a new, independent pre-experiment research run aimed at deciding whether a credible ICLR 2027 project exists. Optimize for discovering whether the project deserves to exist, not for continuing it. The final pre-experiment recommendation must be exactly one of **GO**, **PIVOT**, or **KILL**.

Novelty must be demonstrated by verified literature comparison. Do not invent novelty through terminology changes or present minor implementation differences as scientific contributions. Do not fabricate citations, results, benchmark facts, or performance claims.

## Central question

How and why do learned world models fail when observations are systematically incomplete, occluded, delayed, corrupted, or otherwise partially observable, and can a simple mechanism preserve or recover useful latent dynamics under these conditions?

This is not a generic robust-world-model project. Select the smallest useful subset of structured partial observability, such as spatial occlusion, temporally missing observations, observation delay, sensor dropout, structured feature masking, changing visibility, partial state observability, or train-test changes in the observation process.

## Phase 1: precise candidate questions

Refine the broad idea into two to four narrow, falsifiable candidates. For every candidate state:

- input and observation setting;
- source and structure of partial observability;
- prediction, planning, or control task;
- expected failure of existing models;
- precise hypothesis;
- falsifying observation;
- why the result matters beyond one toy environment.

Rank the candidates. Prefer a general learning principle over an environment-specific trick.

## Phase 2: literature and novelty audit

Before proposing experiments, search foundational and recent primary work on world models, latent dynamics, POMDPs, masked or missing observations, robust state representation, recurrent state-space models, hidden-state inference, observation-model distribution shift, visual world models, model-based reinforcement learning, predictive state representations, and belief-state learning. Prioritize ICLR, NeurIPS, ICML, and relevant arXiv work.

Required outputs across the literature stages:

1. A literature map containing 15 to 30 genuinely relevant, retrievable papers.
2. The five closest papers to the leading candidate. For each give the exact problem, method, evaluation, what it already solves, what remains unsolved, and whether it threatens novelty.
3. A claim-comparison table contrasting candidate claims with those five nearest neighbors.
4. A clear stop or pivot if the only apparent gap is superficial.

Only cite papers actually present in retrieved records or verified primary sources. Separate confirmed facts from inference.

## Phase 3: candidate contribution

Only after the literature audit, propose at most three simple candidate contributions. Possible shapes include a representation objective, latent-state consistency mechanism, uncertainty-aware memory update, observation-process-aware latent inference, lightweight temporal reconstruction, or robust belief-state adaptation, but do not force these if the literature points elsewhere.

For every contribution provide:

- one-sentence scientific claim;
- mechanism and why it should work;
- strongest alternative explanation;
- easiest decisive experiment that could disprove it.

## Phase 4: minimal experiment design

Design exactly one smallest decisive experiment that answers one scientific question. It must specify:

- one small environment or dataset;
- one standard world-model baseline;
- at least two strong, literature-supported comparison baselines;
- one proposed method;
- one primary and one secondary metric;
- at least three structured observability conditions when scientifically justified;
- exact train/test observation-process shifts;
- paired seeds or matched episodes and statistical analysis;
- estimated runtime and VRAM;
- exact success threshold and exact kill criterion.

The experiment must be real and executable, but it must not be executed in this run. Do not build a large benchmark.

## Skeptical reviewer simulation

Before recommending the experiment, give the five strongest ICLR rejection arguments. Cover novelty, importance, realism of corruptions, baseline strength, method complexity, evaluation leakage, planning/control relevance, and toy-only evidence as applicable. For each objection specify the evidence required to neutralize it.

## ICLR feasibility decision

Score 0 to 10 for novelty, importance, technical depth, experimental feasibility, compute feasibility, clarity of claim, and ICLR fit. Give a calibrated overall **GO**, **PIVOT**, or **KILL** recommendation. A GO recommendation requires a real gap and a decisive experiment that fits the compute constraint; uncertainty or a threatened novelty claim should produce PIVOT rather than optimistic language.

## Compute constraints

- Initially one NVIDIA GPU with 8 GB VRAM (RTX 5060 Laptop or RTX 3070 class).
- Prefer small world models, frozen or pretrained encoders where useful, lightweight adapters, latent-space methods, and small dynamical or control environments.
- First meaningful experiment should run in hours, not days.
- No foundation-model training, large-scale video generation, multi-node training, hundreds of GPU-hours, or expensive proprietary data.

## Mandatory stop

This run must stop after problem decomposition, literature audit, nearest-neighbor analysis, candidate claim, minimal experiment design, reviewer attack, and GO/PIVOT/KILL decision. Do not generate experiment code, download large models or datasets, or run training. Human approval is required before any experiment work.

## Stage-specific output requirements

- `topic_init` and `problem_decompose`: produce and rank two to four precise candidates with falsifiers.
- `search_strategy`, `literature_collect`, `literature_screen`, and `knowledge_extract`: build the 15-30 paper map and five-paper nearest-neighbor evidence base.
- `synthesis`: include the five-neighbor comparison and explicit novelty threats; do not assert novelty without evidence.
- `hypothesis_gen`: retain at most three candidate contributions and include the five skeptical reviewer objections with neutralizing evidence.
- `experiment_design`: output valid YAML with the normal required keys plus `selected_scientific_question`, `falsification_test`, `success_threshold`, `kill_criterion`, `estimated_runtime`, `estimated_vram`, `reviewer_risks`, `iclr_scores`, `recommendation`, and `recommendation_rationale`. The plan must describe one minimal experiment only and must not claim that it has run.
