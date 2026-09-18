# Skeptical ICLR reviewer stress test

## Reviewer 1 — empirical rigor

| Criticism | Severity | Answered? | Cheapest answer | Information gain | Cost |
|---|---|---|---|---|---|
| Nine 160M and five 70M runs may still share generator/training-pipeline dependence, so “independent” is narrower than it sounds. | MEDIUM | PARTIAL | State the pretraining-run unit explicitly; later add one genuinely independent training family only after corpus validation. | Medium | High; likely downloads/inference. |
| The same WikiText-2 evaluation source is used throughout, so the apparent run replication may be corpus-specific. | HIGH | NO | Frozen cross-corpus endpoint replication on one distinct corpus, same models, layers, seeds, confidence/KL/NLL controls. | Very high | ~1–2 local GPU-hours; modest download if not cached. |
| Matching analyses can hide poor overlap and researcher degrees of freedom. | MEDIUM | YES | Publish calipers, balance tables, all cells, run-level summaries, and preregistrations already stored. | Medium | 2–4 human-hours, no GPU. |
| The invalid ARC-006 assay undermines confidence in every later result. | HIGH | PARTIAL | Put the bug and withdrawal in the main methods, show canonical tie rule, exact rerun agreement, reversals, seals, and supersession chain. | High | 2–3 human-hours, no GPU. |
| Bootstrap CIs may overstate independence if token/cell observations are treated as runs. | HIGH | YES | Lead with run-level bootstrap and show the experimental unit in every table; retain token/cell uncertainty only as secondary. | High | 1–2 human-hours, no GPU. |
| Five checkpoints are insufficient for a continuous training law. | MEDIUM | YES | Restrict the claim to early-to-late change; do not claim monotonicity or phase transition. | Medium | No experiment needed. |

## Reviewer 2 — novelty and significance

| Criticism | Severity | Answered? | Cheapest answer | Information gain | Cost |
|---|---|---|---|---|---|
| This may be a small extension of prior layer-deletion robustness work, measured across checkpoints. | FATAL | NO | A primary-source novelty audit of training-time layer substitutability, ablation robustness, progressive specialization, and matched-damage intervention studies. | Very high | 12–20 human-hours; web needed later, no GPU. |
| ΔS is an arbitrary discontinuous top-1 metric with unclear scientific relevance. | HIGH | PARTIAL | Triangulate with one preregistered continuous/rank-based substitutability metric on the same stored logits or a compact rerun. | Very high | 4–8 human-hours; 0–1 GPU-hour. |
| Tiny Pythia models do not support an LLM-level claim. | HIGH | PARTIAL | Keep the title and claim at “small language models”; compare scale-up value only after corpus/construct gates. | Medium now | No compute for claim narrowing; 410M/1B later is expensive. |
| One architecture family cannot establish generality. | HIGH | PARTIAL | Treat SmolLM2 as exploratory and defer a properly replicated non-Pythia family until the core assay survives a new corpus. | High later | Several GPU-hours and model storage. |
| The paper does not show practical pruning or downstream consequences. | HIGH | NO | Add one bounded downstream or pruning-predictivity endpoint only after construct validation. | High | 2–6 GPU-hours. |

## Reviewer 3 — mechanism and interpretation

| Criticism | Severity | Answered? | Cheapest answer | Information gain | Cost |
|---|---|---|---|---|---|
| ΔS, KL, and NLL are functions of the same output distribution, so “functional damage” alignment may be partly mechanical. | HIGH | PARTIAL | Use matched contrasts as discrimination only; add a rank/margin-null metric and report shared-output dependence explicitly. | High | 0–1 GPU-hour plus analysis. |
| The family residual could be an intervention-implementation artifact rather than internal structure. | HIGH | PARTIAL | A third, preregistered intervention with matched support would be decisive but is not the highest-value next test. | High | 2–4 GPU-hours, substantial engineering. |
| Geometry selection and regression may be underpowered or specification-dependent. | MEDIUM | PARTIAL | Publish the frozen sequence, all coefficients, matching diagnostics, and adjusted residuals; do not promote a geometry mechanism. | Medium | 2–4 human-hours. |
| Failed internal-direction identification means the paper has no mechanism. | MEDIUM | YES | Frame the contribution as an empirical phenomenon plus falsification of simple explanations; explicitly close the branch. | Medium | No new experiment. |
| Layer heterogeneity could explain the aggregate family residual. | MEDIUM | PARTIAL | Show run/layer residual distributions and ARC-007R's failure to remove heterogeneity; do not average it away. | Medium | 1–2 human-hours. |

## Reviewer consensus

The coherent empirical core would survive a “no complete mechanism” objection if
the paper is framed conservatively. It would not currently survive both the
single-corpus objection and an aggressive novelty challenge. The former is the
highest-information experimental gap; the latter requires a future web-enabled
literature audit, not more model runs.
