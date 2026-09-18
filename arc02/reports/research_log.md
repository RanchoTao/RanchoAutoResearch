# ARC-02 research log

## Iteration 0

Hypothesis: Existing literature has not already tested whether a causally defined
reasoning circuit changes smoothly or reorganizes abruptly across a controlled
reasoning-depth sweep.

Experiment: Primary-source novelty audit emphasizing work that varies hop count,
tracks circuit formation, or compares circuits across task complexity.

Expected if true: Adjacent work studies fixed tasks, training-time emergence, or at
most one-versus-two-hop comparisons without a depth-indexed causal circuit curve and
formal change-point test.

Expected if false: A prior work reports causal circuit size/topology and cross-depth
overlap over multiple depths with accuracy controls and change-point inference.

Observed: Sixteen relevant primary works were audited. The nearest work either
tracks circuit emergence over training, analyzes a fixed reasoning task, or
compares only one versus two hops. No audited paper combines a four-level depth
sweep, causally sufficient circuits, method agreement, and formal change-point
testing. However, two 2025–2026 papers create substantial collision risk.

Interpretation: The broad claim is crowded; the tightly controlled depth-indexed
causal-circuit question remains open but is only YELLOW novelty.

Decision: GO

Next: Run exactly one seed of the smallest discriminating experiment.

## Iteration 1

Hypothesis: A five-layer, 0.83M-parameter Transformer trained on 40,000 fixed
examples can generalize across the jointly trained depth-1–5 relation task.

Experiment: Train seed 11 on the fixed balanced dataset with identical graph
statistics at every depth.

Expected if true: Validation accuracy exceeds 95% for each depth before circuit
analysis.

Expected if false: Training loss falls while held-out accuracy remains low,
indicating memorization or insufficient computational depth.

Observed: After 42 epochs, training loss fell from 2.33 to 0.216 while held-out
macro accuracy remained 0.235 (per-depth range 0.208–0.299). The run was stopped
before any circuit measurement.

Interpretation: This is an accuracy-control failure, not evidence about circuit
transitions. The fixed finite dataset allowed memorization, and five network
layers may be insufficient for five-hop traversal.

Decision: MODIFY

Next: Regenerate 100,000 procedural examples every epoch and use ten layers,
while keeping all semantic controls unchanged.

## Iteration 2

Hypothesis: Fresh procedural sampling plus ten layers is sufficient when each
edge is serialized as separate source and target tokens.

Experiment: Train a 1.66M-parameter ten-layer model for 39 epochs, drawing
100,000 new graphs per epoch.

Expected if true: Held-out accuracy rises toward the 95% floor without a
train/validation memorization gap.

Expected if false: Loss and accuracy plateau near a shortcut baseline.

Observed: Best held-out macro accuracy was 0.261; the final per-depth accuracies
were {1: 0.222, 2: 0.238, 3: 0.233, 4: 0.241, 5: 0.370}. The formal accuracy
gate aborted circuit analysis.

Interpretation: More data/depth alone does not fix the serialization. A pair of
source/target positions makes each graph edge require an additional binding
step and is harder than the concatenated edge-token representation used in the
closest controlled backward-chaining work.

Decision: MODIFY

Next: Use one discrete token per directed edge while preserving the exact same
graphs, query depths, edge count, distractor count, and labels.

## Iteration 3

Hypothesis: Under accuracy matching, circuit size will show a method-robust
structural change as reasoning depth increases.

Experiment: Seed 11; 1.69M parameters; depths 1–5; 256 correct clean/corrupt
pairs per depth; activation-patching and zero-ablation rankings; 90% retained
accuracy criterion; 50 matched random-circuit controls.

Expected if true: Both discovery methods favor a similar breakpoint and select
overlapping circuits, with a causal ablation effect beyond random controls.

Expected if false: The apparent breakpoint is method-specific or the circuit
sets disagree despite matched accuracy.

Observed: Validation accuracy was 0.995–1.000. Patching circuit sizes were
17/35/38/37/46; ablation sizes were 31/35/38/36/41. Patching BIC favored a
piecewise fit with breakpoint 2 (13.06 vs 18.06 linear), whereas ablation BIC
favored linear (7.02 vs 8.91 piecewise). Cross-method Jaccard was only 0.50 at
depth 1 and 0.75–0.87 later. Identified-circuit ablation reduced accuracy to
0.09–0.21, but matched random ablations were also often destructive at these
large circuit sizes.

Interpretation: The seed contains a strong attribution-method artifact candidate,
not method-robust evidence of a phase transition.

Decision: MODIFY

Next: Replicate the exact protocol at seeds 23 and 37; do not expand scale.

## Iteration 4

Hypothesis: A change point that survives three seeds and two causal discovery
methods should outperform smooth alternatives and coincide with a reproducible
drop in adjacent circuit overlap.

Experiment: Aggregate seeds 11/23/37 using seed fixed effects; compare linear,
quadratic, and continuous piecewise models; summarize adjacent Jaccard,
layer-distribution entropy, retained performance, and matched random controls.

Expected if true: Piecewise BIC wins clearly (roughly delta BIC > 6), the same
breakpoint appears across methods/seeds, and adjacent overlap drops at that point.

Expected if false: Model preference is weak/method-specific, inferred breakpoints
vary, and circuits expand or fluctuate without topological discontinuity.

Observed: All 15 depth-by-seed validation accuracies were 0.987–1.000. Patching
size means were 24.0/32.3/41.3/42.0/46.7; ablation means were
26.3/32.3/40.0/35.0/39.7. Seed-adjusted patching BIC favored linear (58.36) over
quadratic (58.67) and piecewise (60.63). Ablation BICs were effectively tied:
piecewise 50.81, quadratic 50.84, linear 51.83. Individually, only seed 23
preferred a piecewise ablation fit; seeds 11 and 37 preferred linear. Adjacent
Jaccard increased from 0.47 to 0.86 (patching) and 0.53 to 0.78 (ablation).
Normalized layer entropy was 0.95–0.99, with no monotonic layer-centroid shift.

Interpretation: There is evidence that deeper composition recruits more of the
network, but no method- and seed-robust phase transition. The strongest apparent
breaks are attribution/threshold artifacts. The one-hop to multi-hop boundary
is an expansion regime, not demonstrated circuit replacement.

Decision: KILL

Next: Preserve the negative-control assets. Do not scale ARC-02 without a new
pre-registered claim centered on circuit-method robustness rather than phase
transition discovery.
