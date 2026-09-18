# Pivot brief: Test-Time Adaptation of World Models under Observation-Process Shift

## Status and hard constraints

- This is a pivot inside the existing run `world-models-spo-iclr2027-20260823`.
- The old Stage 9 factorial pilot was explicitly rejected and aborted. Never execute it.
- Preserve and reuse the parent run's 20 knowledge cards, 143 targeted novelty records, five-neighbor audit, Flow Equivariant analysis, Dreamer/RSSM baselines, and partial-observability taxonomy.
- Do not run an experiment, generate code, simulate results, approve a gate, or proceed past Stage 9.
- The final recommendation must be exactly one of `GO`, `PIVOT`, or `KILL`.

## Central question

Can a pretrained predictive world model detect and adapt to a change in the observation process using only recent unlabeled action-observation history, without full retraining or destructive drift?

For the primary setting, latent environment dynamics are fixed while the observation process changes:

`P_train(s_{t+1}|s_t,a_t) = P_test(s_{t+1}|s_t,a_t)` but
`P_train(o_t|s_t) != P_test(o_t|s_t)`.

Examples: sensor corruption or dropout, occlusion, viewpoint shift, missing frames, altered observation rate, structured feature loss, and delayed observations.

This is not a proposal for another memory architecture. The object of study is deployment-time adaptation of an already trained world model.

## Required analysis

1. Use `TARGETED_NOVELTY_AUDIT.md` as verified pivot evidence and use the copied parent-run knowledge cards as prior evidence.
2. Treat RePo as a decisive novelty constraint: reward-free test-time encoder alignment while dynamics and policy remain frozen is already published.
3. Treat WorldAgen and AdaWM as constraints on broad claims about world-model test-time training and mismatch-guided selective updates.
4. Treat ReOI, Time-Aware World Models, adaptive neural processes, robust filtering, and the Observer Effect paper as adjacent constraints and failure-mode evidence.
5. Analyze observation-only, dynamics-only, and combined shifts separately. Rank novelty, tractability, ICLR relevance, experimental clarity, 8 GB feasibility, and overlap risk.
6. Identify a concrete failure mode before proposing any method: encoder mismatch, posterior/belief drift, temporal inconsistency, error accumulation, miscalibration, context contamination, or destructive updates.
7. Aggressively reject the bare decomposition claim "adapt the observation module and freeze dynamics" as already substantially covered by RePo.
8. Generate no more than three candidates. Each requires a one-sentence claim, mechanism, nearest threat, exact difference, and cheapest falsification.
9. Design exactly one smallest valid experiment; do not execute it. It must compare exactly these four primary conditions:
   - frozen pretrained world model;
   - naive full-model test-time fine-tuning;
   - strongest faithful literature baseline;
   - one selective candidate method.
10. Measure pre-shift error, immediate post-shift error, recovery curve, optional control/planning, adaptation compute, return-to-source forgetting, and uncertainty/calibration where meaningful, using five paired seeds and confidence intervals.
11. Runtime must be credible on one RTX 5060 Laptop 8 GB or RTX 3070 8 GB. Prefer a small, properly trained predictive world model over an invalid 60-second Dreamer proxy.
12. Conduct an eight-point skeptical ICLR review covering field saturation, artificial shift, encoder-repair reduction, adaptive filtering/system identification overlap, missing planning gain, triviality, benchmark scale, and extra-compute confounding. State evidence needed for each rebuttal.
13. Score novelty, importance, technical depth, experimental feasibility, compute feasibility, ICLR fit, and probability that a meaningful contribution remains from 0 to 10.

## Current evidence-led boundary

The broad project is already too crowded. The only plausible residual question is whether recent unlabeled transitions can *localize* an observation-process shift versus a dynamics shift and safely route adaptation to an observation interface while empirically preserving the latent transition model. This is not assumed novel: it must be distinguished from RePo's encoder alignment, AdaWM's mismatch-guided updates, WorldAgen's test-time world-model training, and classical adaptive filtering/system identification.

The bare claim that selective observation adaptation beats full fine-tuning is insufficient. A surviving claim must include a nontrivial discriminator, a preservation test, and a setting where the discriminator can fail.

## Gate behavior

Produce synthesis, at most three hypotheses, exactly one experiment design, reviewer stress test, scores, and the single recommendation. Then stop at the Stage 9 human gate. Do not auto-approve.
