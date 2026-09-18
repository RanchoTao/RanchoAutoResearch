# AutoResearchClaw — Agent Configuration

## Overview

ResearchClaw is an autonomous research pipeline that takes a research topic and produces a complete academic paper through 23 automated stages. This file defines how AI agents should bootstrap and interact with the system.

## Agent Role: Research Orchestrator

You are an AI research assistant operating ResearchClaw. Your job is to:

1. **Understand the user's research interest** — clarify the topic, scope, and constraints
2. **Configure the pipeline** — set up `config.yaml` with appropriate LLM settings and experiment mode
3. **Execute the pipeline** — run the 23-stage pipeline via CLI or Python API
4. **Monitor and intervene** — handle gate stages (5, 9, 20), review intermediate outputs
5. **Deliver results** — present the final paper, charts, and experiment data to the user

## Quick Setup

```bash
# Install
pip install -e .

# Configure (copy and edit)
cp config.researchclaw.example.yaml config.yaml
# Set llm.base_url, llm.api_key, experiment.mode

# Run
researchclaw run --topic "Your topic" --auto-approve
```

## Pipeline Stages (23 stages, 8 phases)

| Phase | Stages | Description |
|-------|--------|-------------|
| A: Research Scoping | 1-2 | Define topic, decompose into sub-problems |
| B: Literature Discovery | 3-6 | Search strategy, collect papers, screen [GATE@5], extract knowledge |
| C: Knowledge Synthesis | 7-8 | Cluster topics, generate hypotheses |
| D: Experiment Design | 9-11 | Design experiments [GATE@9], generate code, plan resources |
| E: Experiment Execution | 12-13 | Run experiments, iterative refinement |
| F: Analysis & Decision | 14-15 | Analyze results, decide proceed/pivot/iterate |
| G: Paper Writing | 16-19 | Outline, draft, peer review, revision |
| H: Finalization | 20-23 | Quality gate [GATE@20], archive, export with charts, citation verification |

## Gate Stages

Three stages require approval (use `--auto-approve` for fully autonomous mode):
- **Stage 5** (Literature Screen): Validates collected literature quality
- **Stage 9** (Experiment Design): Validates experiment protocol before code generation
- **Stage 20** (Quality Gate): Validates overall paper quality before export

## Experiment Modes

- `simulated`: LLM generates synthetic results (fast, no code execution)
- `sandbox`: Execute generated code locally (requires Python environment)
- `ssh_remote`: Execute on remote GPU server (requires SSH configuration)

## Key Files

| File | Purpose |
|------|---------|
| `config.yaml` | Pipeline configuration (LLM, experiment mode, etc.) |
| `config.researchclaw.example.yaml` | Configuration template |
| `researchclaw/cli.py` | CLI entry point |
| `researchclaw/pipeline/executor.py` | Stage execution logic |
| `researchclaw/pipeline/runner.py` | Pipeline orchestration |
| `researchclaw/experiment/validator.py` | Code validation (AST, security, imports) |
| `researchclaw/experiment/visualize.py` | Chart generation |

## Decision Guide

| Situation | Action |
|-----------|--------|
| User provides a clear topic | Run full pipeline with `--auto-approve` |
| User wants to review stages | Run without `--auto-approve`, pause at gates |
| Pipeline fails at a stage | Check error, fix config or retry from that stage with `--from-stage` |
| User wants iteration | Use `execute_iterative_pipeline()` with `max_iterations` |
| Experiment code fails | Validator auto-retries up to 3 times; if still failing, pause/fix or use the existing Codex fallback — never present `simulated` output as research evidence |

## DeepSeek-assisted experiment strategy

When `DEEPSEEK_API_KEY` is set, Stage 13 uses a DeepSeek-first refinement loop:

1. Build a bounded state from the research goal, best/current metric, recent
   experiments, failed proposals, code summary, evaluator, allowed files,
   hardware, and time budget.
2. Ask DeepSeek for exactly one schema-validated experiment proposal.
3. Give Codex the validated proposal plus current experiment files. Codex does
   a quick sanity check and implements it without repeating the strategy work.
4. Run the existing real sandbox/Docker evaluator and append the actual metric.
5. Ask DeepSeek to analyze that result before the next round.

DeepSeek has no shell or file access. Codex retains edits, execution, git,
metric verification, repairs, and supervision. If DeepSeek is missing or fails,
the loop emits an explicit warning and uses the original Codex-only prompt.

Configuration is environment-only; copy `.env.example` entries into the ignored
`.env` file or export them in the launching shell. Calls are recorded locally in
`logs/deepseek_calls.jsonl`, with raw API envelopes under
`logs/deepseek_responses/`. No API key is logged.

## Integration Platforms

ResearchClaw works with:
- **Claude Code**: Load via `.claude/skills/researchclaw/SKILL.md`
- **OpenClaw**: Read this `AGENTS.md` + `README.md` for bootstrapping
- **OpenCode**: Compatible skill format in `.claude/skills/`
- **Standalone**: Direct CLI or Python API usage
