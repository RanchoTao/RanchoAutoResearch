# ARC-21 novelty matrix

Audit date: 2026-08-24. “Fixed budget” requires equal numbers of supervised
intermediate states/tokens across placement strategies; merely using fewer
rollouts or a sparse reward does not qualify.

| Work | Intermediate supervision? | Selective steps? | Fixed budget? | Ground-truth reasoning states? | OOD depth? | Collision |
|---|---|---|---|---|---|---|
| [Let's Verify Step by Step / process supervision](https://openai.com/index/improving-mathematical-reasoning-with-process-supervision/) (2023) | Yes, step correctness | No, dense labels | No | Human-labeled MATH steps | No controlled depth extrapolation | Medium: establishes full process supervision only |
| [GPO: Learning from Critical Steps](https://arxiv.org/abs/2509.16456) (NeurIPS 2025) | Yes, via focused post-training rollouts | Yes, maximum estimated advantage | No matched state-label budget | No; model trajectories and outcome rollouts | Reasoning benchmarks, not controlled unseen depth | **Very high**: owns broad “learn from critical steps” framing |
| [Verified Critical Step Optimization](https://arxiv.org/abs/2602.03412) (2026) | Yes, verified alternatives at decision points | Yes, outcome-flipping failed steps | Sparse (16%) but not top-k placement matched to random/uniform | Verification from rollout outcomes, not exact latent states | Long-horizon agent tasks, not synthetic depth | **Very high** |
| [Verifiable Process Rewards](https://arxiv.org/abs/2605.10325) (2026) | Dense step rewards | No placement study | No | Symbolic/algorithmic oracle | Transfer benchmarks, not length sweep | High on exact process labels; low on placement |
| [Correct Answers from Sound Reasoning / VPS](https://arxiv.org/abs/2605.12519) (2026) | Yes | Adaptive component weighting by remaining error | No top-k matched budget | Engine-verifiable chess signals | No compositional-depth test | High adjacent adaptive weighting |
| [Better Process Supervision with Bi-directional Rewarding Signals](https://arxiv.org/abs/2503.04618) (2025) | Yes, PRM | Scores every step using past/future success | No | Rollout-derived | No controlled depth | Medium |
| [Math-Shepherd](https://arxiv.org/abs/2312.08935) (2023) | Automated step scores | Scores partial rationales | No placement comparison | Monte-Carlo outcome estimates | No | Medium |
| [SSPO](https://arxiv.org/abs/2508.12604) (2025) | Step-wise preference optimization | Fine-grained across steps, not top-k state labels | No | Self-traced preferences | No controlled depth | Medium |
| [COALITION / Selective Rationale Optimisation](https://openreview.net/forum?id=NHxwxc3ql6) (ICLR 2025) | Rationale-level training | Selects whole rationale candidates, not steps within one trajectory | No | No task-ground-truth intermediate states | No | Low-medium terminology collision |
| [Waypoint Transformer](https://arxiv.org/abs/2306.14069) (NeurIPS 2023) | Intermediate goal targets | Selects useful waypoints | Not reasoning-state top-k | Environment states | Spatial compositionality, not reasoning depth | Medium cross-domain conceptual collision |
| [Knowledge Matters: intermediate targets](https://jmlr.csail.mit.edu/papers/v17/gulchere16a.html) (JMLR 2016) | Yes, supervised hints | No budgeted placement study | No | Synthetic intermediate concepts | Generalization but not length depth | Medium historical prior |
| [Learning from Partial Chain-of-Thought via Truncated-Reasoning Self-Distillation](https://arxiv.org/abs/2603.13274) (2026) | Partial rationale distillation | Truncates rationale | Compression budget, not state-placement top-k | Teacher/self trace | Multiple reasoning tasks, no exact depth-state protocol located | High adjacent partial supervision |

## Collision assessment

GPO and CSO prevent any broad novelty claim that “critical reasoning steps should
receive more training attention.” ARC-21 survives only as a narrower measurement
question:

> With exactly one exact intermediate-state label per example, does choosing its
> position improve extrapolation to unseen composition lengths relative to
> position-balanced and random placement?

No audited work jointly provides exact program states, fixed state-label budget,
random/uniform/early/late controls, and unseen-depth evaluation. That is a narrow
protocol gap, not a new general theory of critical-step learning.
