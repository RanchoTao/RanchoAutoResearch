# ARC-21 research log

## Iteration 0

Hypothesis: The exact formulation remains unoccupied despite adjacent work on
process supervision and critical-step optimization.

Cheapest falsification: Primary-source collision audit before training.

Expected if true: Existing work selects critical LLM/RL steps but does not hold
the number of exact intermediate-state labels fixed while evaluating OOD
composition depth.

Expected if false: A prior study already compares top-k, random-k, uniform-k,
early/late-k under a matched intermediate-label budget on controlled trajectories.

Observed: Twelve close works were audited. GPO and CSO directly select critical
steps, but neither performs the exact fixed intermediate-state-label budget plus
OOD composition-depth comparison. Dense process supervision, partial rationales,
and waypoint targets cover the surrounding space.

Confounds: Terminology differs across supervised auxiliary targets, process
rewards, rationale selection, and RL critical-step resets.

Decision: GO

Next: Run one-seed fixed-budget chain MVP; no DAG or mechanistic analysis.

## Iteration 1

Hypothesis: With one intermediate-state label per example, midpoint placement
improves OOD depth generalization relative to random/uniform placement.

Cheapest falsification: One seed across outcome-only, full-process, random-1,
uniform-1, midpoint-1, early-1, and late-1; identical initialization, examples,
training steps, and normalized auxiliary loss.

Expected if true: Midpoint-1 exceeds random/uniform by a practically meaningful
margin and approaches full-process performance.

Expected if false: Fixed-budget conditions are tied, or any separation is a
simple early/late positional effect.

Observed: All conditions reached 100% mean ID accuracy. OOD depth-5–8 means were:
outcome 0.0906, full 0.0966, random 0.0984, uniform 0.0951, midpoint 0.0923,
early 0.0805, late 0.1080. Midpoint did not beat random. The largest placement
gap was late minus early = 0.0275.

Confounds: Single training seed; OOD accuracy is low; late supervision may be
easier because it is closest to the already-supervised outcome.

Decision: MODIFY

Next: Replicate exactly at seeds 23 and 37. Continue only if the late-step
asymmetry survives; do not build a DAG.

## Iteration 2

Hypothesis: Late-state supervision has a reproducible OOD advantage that could
justify a single pivot to temporal asymmetry.

Cheapest falsification: Exact replication at seeds 23 and 37, followed by
paired three-seed comparisons. No new task, hyperparameter search, or metric
selection.

Expected if true: Late-1 consistently and materially exceeds both Early-1 and
Random-1 across seeds and unseen depths, rather than only at the first unseen
depth.

Expected if false: The late advantage is small relative to Random-1, changes
sign, or is concentrated at depth 5 while deeper performance remains near
chance.

Observed: Across seeds 11/23/37, OOD means (SD) were outcome-only 0.0887
(0.0078), full-process 0.0947 (0.0038), random-1 0.0984 (0.0060), uniform-1
0.0907 (0.0044), midpoint-1 0.0929 (0.0014), early-1 0.0860 (0.0049), and
late-1 0.1035 (0.0046). Midpoint-minus-random was negative in all seeds, mean
-0.00546. Late-minus-early was positive in all seeds, mean +0.0175 (paired
two-sided t-test p=0.074, n=3), but late-minus-random averaged only +0.00513,
reversed sign in seed 37, and was concentrated at depth 5. At depths 6–8, all
strategies remained near the 1/32 chance baseline.

Confounds: Late supervision is closest to the final-answer loss and therefore
easier; no position-matched non-chain bottleneck exists in this MVP. The apparent
late advantage does not establish computational importance and fails to transfer
cleanly beyond the first unseen depth.

Decision: KILL

Next: Stop ARC-21. Preserve the late-versus-early observation as a negative-
result lead, but do not promote or build the DAG without independent evidence.
