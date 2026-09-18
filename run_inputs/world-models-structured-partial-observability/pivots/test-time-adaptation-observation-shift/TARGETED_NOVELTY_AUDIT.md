# Targeted novelty audit: world-model TTA under observation-process shift

Audit date: 2026-08-23. Venue/status statements below were checked against primary proceedings, OpenReview, PMLR, or arXiv records. This document adds pivot-specific evidence and does not replace the parent run's 20-paper shortlist or 143-record audit.

## Executive conclusion

The generic proposal is not novel. RePo already performs reward-free test-time adaptation of a visual world model's encoder under visual distribution shift while leaving dynamics and policy unchanged. WorldAgen directly trains a world-model head at deployment; AdaWM detects model-versus-policy mismatch and selectively fine-tunes the responsible component. ReOI intervenes on shifted observations without modifying the world model. Therefore, neither "world-model TTA", "encoder-only TTA", "freeze dynamics", nor "selective adaptation" can be the main claim.

A narrower gap may remain: identify whether prediction failure originates in the observation process or latent dynamics using only recent unlabeled transitions, route adaptation to a separately parameterized observation interface, and verify preservation/forgetting when the source sensor returns. This residual is plausible but unverified and faces identifiability objections from system identification and filtering.

## Five strongest new nearest neighbors

### 1. RePo: Resilient Model-Based Reinforcement Learning by Regularizing Posterior Predictability — NeurIPS 2023

1. **Shift:** Task-irrelevant visual changes, including backgrounds, lighting, and significant target-domain visual distribution shift.
2. **World-model adaptation:** Yes; its observation encoder is adapted at test time.
3. **Adaptation information:** Unlabeled target observations plus source-domain support/distribution constraints from the trained representation and saved source data.
4. **Labels/rewards:** The alignment procedure is explicitly reward-free; target labels are not required.
5. **Updated parameters:** Encoder/representation parameters; latent dynamics and policy are not relearned.
6. **Mechanism:** Gradient-based latent alignment using support constraints or distribution matching plus calibration.
7. **Observation-process shift:** Yes for visual distractors and appearance changes, though it does not systematically cover missing frames, delays, sensor dropout, or observation-operator identification.
8. **Evaluation:** Primarily control in visual model-based RL, with representation/predictive diagnostics.
9. **Unsolved:** Online discrimination between observation and dynamics shifts; structured temporal sensor failures; safe adaptation without source replay; recovery and forgetting when shifts reverse.
10. **Novelty threat:** **Critical (10/10)** to the proposed decomposition and encoder-only adaptation claim.

### 2. WorldAgen: Unified State-Action Prediction with Test-Time World Model Training — AAAI 2026

1. **Shift:** New object configurations, environments, and physical/world dynamics in embodied manipulation; lighting is mentioned as a deployment variation.
2. **World-model adaptation:** Yes; a world-model prediction head and shared backbone are trained at test time.
3. **Adaptation information:** Recent exploratory action trajectories and observed ground-truth state transitions.
4. **Labels/rewards:** No task labels are needed for the predictive update, but realized next states serve as self-supervised targets and online interaction is available.
5. **Updated parameters:** The world-model pathway/shared Transformer representation via lightweight TTT; the architecture shares features with the policy head.
6. **Mechanism:** Gradient-based self-supervised future-state prediction during test-time exploration.
7. **Observation-process shift:** Not isolated; its main framing is novel environments and dynamics, with mixed shifts possible.
8. **Evaluation:** Both world prediction and embodied action success on CALVIN and LIBERO.
9. **Unsolved:** Factor localization, frozen-dynamics preservation, observation-only controlled shifts, forgetting, and protection against destructive shared-backbone drift.
10. **Novelty threat:** **Very high (9/10)** to broad test-time world-model training claims; moderate to a rigorously isolated observation-only factorization.

### 3. AdaWM: Adaptive World Model based Planning for Autonomous Driving — ICLR 2025

1. **Shift:** New autonomous-driving tasks causing policy mismatch or learned dynamics-model mismatch.
2. **World-model adaptation:** Yes when model mismatch dominates; otherwise the policy is adapted.
3. **Adaptation information:** Online interactions, predicted and realized trajectories, and task feedback in CARLA.
4. **Labels/rewards:** Online RL/task signals are available; this is not an unlabeled observation-only protocol.
5. **Updated parameters:** Either low-rank world-model parameters or selected policy sub-units.
6. **Mechanism:** Mismatch identification followed by alignment-driven, component-selective fine-tuning.
7. **Observation-process shift:** No clean isolation of `P(o|s)` shift from `P(s'|s,a)` shift.
8. **Evaluation:** Downstream autonomous-driving planning/control.
9. **Unsolved:** Unsupervised localization between observation and dynamics mismatch, encoder-versus-transition routing, source-return forgetting, and precise sensor-shift protocols.
10. **Novelty threat:** **Very high (9/10)** to mismatch detection plus selective adaptation as a generic contribution.

### 4. Reimagination with Test-time Observation Interventions (ReOI) — arXiv 2025 / RSS OOD Workshop 2025, subsequently ICRA 2026

1. **Shift:** Novel visual distractors, objects, and backgrounds that corrupt visual world-model predictions.
2. **World-model adaptation:** No; the pretrained world model remains frozen.
3. **Adaptation information:** Current observation, imagined future frames under a safety-check action, VLM analysis, segmentation, and inpainting.
4. **Labels/rewards:** No target labels; planning/task scoring is used downstream.
5. **Updated parameters:** None; the input observation is altered and distractors are reintroduced after prediction.
6. **Mechanism:** Detection and input-space intervention rather than gradients or latent adaptation.
7. **Observation-process shift:** Yes, specifically open-world visual distractors, but not temporal dropout/delay or an explicit changing sensor operator.
8. **Evaluation:** World-model prediction quality and visual MPC/action verification success.
9. **Unsolved:** General observation-operator shifts, quantitative shift localization, latent belief recovery, and adaptation when affected content is task-relevant rather than removable.
10. **Novelty threat:** **High (8/10)** to claims that test-time observation repair for frozen world models is new.

### 5. The Observer Effect in World Models: Invasive Adaptation Corrupts Latent Physics — arXiv 2026

1. **Shift:** OOD physical regimes and narrow downstream adaptation distributions in fluid and orbital dynamics.
2. **World-model adaptation:** The paper evaluates adaptation as a potentially destructive intervention rather than proposing deployment TTA.
3. **Adaptation information:** Supervised physical targets for probes/fine-tuning and OOD trajectories.
4. **Labels/rewards:** Physical target labels are available; unlike the proposed unlabeled deployment setting.
5. **Updated parameters:** Full-model or last-layer fine-tuning is contrasted with frozen low-capacity probes.
6. **Mechanism:** Mechanistic evaluation using linear probes, representational similarity, parameter-change analysis, and symbolic validation.
7. **Observation-process shift:** No; the shift is in physical regimes/evaluation data.
8. **Evaluation:** Prediction and latent physical-law decodability, not control.
9. **Unsolved:** How to adapt safely under sensor shift; whether restricted adapters preserve control-relevant dynamics; online shift localization.
10. **Novelty threat:** **High (8/10)** to "full adaptation causes destructive latent drift" as a new empirical phenomenon, but it positively motivates a preservation test.

## Additional adjacent constraints

- **Time-Aware World Model for Adaptive Prediction and Control (ICML 2025):** trains across observation intervals and conditions on `delta-t`; it covers robustness to varying observation rates by training-time design, not unlabeled test-time adaptation. Strong threat to any claim about rate shift alone.
- **Neural Processes with Event Triggers for Fast Adaptation to Changes (L4DC 2024):** adapts conditional dynamics models from recent observations, uses sliding context windows and statistically triggered resets, and documents context contamination across parameter regimes. Strong baseline for change detection and context reset under dynamics shift.
- **Outlier-robust Kalman Filtering through Generalised Bayes (ICML 2024):** gives efficient robust Bayesian updates under outliers and misspecified measurement models. Strong conceptual/methodological threat for low-dimensional or approximately Gaussian observation corruption.
- **Monitoring Risks in Test-Time Adaptation (NeurIPS 2025):** demonstrates that unlabeled TTA needs explicit sequential risk monitoring and stop/escalation rules. It raises the bar for safe online adaptation claims.
- **Sparse Diffusion Autoencoder for Test-time Adapting Prediction of Complex Systems (NeurIPS 2025):** adapts an encoding scheme at test time for emergent spatiotemporal structure. It threatens generic "adapt only the encoder for predictive dynamics" claims outside RL.

## Three-setting comparison

Scores use 10 = best for novelty/tractability/relevance/clarity/feasibility and 10 = worst for overlap risk.

| Setting | Novelty | Tractability | ICLR relevance | Clarity | 8 GB feasibility | Overlap risk | Audit judgment |
|---|---:|---:|---:|---:|---:|---:|---|
| Observation shift only | 6 | 9 | 8 | 9 | 9 | 8 | Best scientific isolation and cheapest falsification, but RePo/ReOI/TAWM make the bare method claim non-novel. |
| Dynamics shift only | 3 | 7 | 7 | 8 | 8 | 10 | Saturated by online system identification, context-conditioned dynamics, adaptive neural processes, AdaWM, and WorldAgen. |
| Combined shift | 7 | 3 | 8 | 3 | 5 | 8 | Potentially less covered but confounded and generally unidentifiable without assumptions; a poor first experiment. |

**Ranking:** observation-only first; combined second only as a later stress test; dynamics-only last as a primary contribution. Combined shift is not automatically better.

## Concrete failure mechanisms

1. **Encoder/posterior mismatch:** A shifted observation maps to a latent point outside the transition prior's supported manifold. Supported directly by RePo's finding that significant visual shift defeats the learned encoder and can be repaired by reward-free alignment.
2. **Belief-state contamination:** Incorrect posteriors are recursively fed into the RSSM, so a transient sensor fault produces persistent latent drift and compounding prediction error. Delayed-observation results and event-triggered neural processes motivate measuring a recovery curve and context reset.
3. **Observation-versus-dynamics ambiguity:** A one-step prediction residual can be explained by an incorrect observation map, transition model, or both. Without structural assumptions or controlled interventions, routing updates is not identifiable.
4. **Destructive adaptation:** Narrow, unlabeled online updates can overwrite reusable latent structure, improve current reconstruction while harming dynamics and source-return performance. The Observer Effect gives direct evidence that invasive fine-tuning can destroy latent physical structure; general continual-TTA work identifies weight degradation and collapse risks.
5. **Miscalibrated confidence:** A world model may remain confident while its posterior is off-manifold. Prediction error alone is delayed and can trigger adaptation after belief corruption has propagated.

The most decision-relevant failure is not simply encoder error; it is **mislocalized adaptation**: reconstruction/prediction gradients update latent dynamics when the shift is confined to observations, causing slower recovery and forgetting.

## Candidate contributions (maximum three)

### Candidate 1 — factor-localized safe adaptation

**Claim:** Under controlled observation-only shifts, a residual-based shift localizer that routes updates to a small observation adapter while anchoring the frozen transition operator recovers prediction accuracy faster and forgets less than full fine-tuning and RePo-style encoder alignment.

**Mechanism:** Compare observation-space residuals after latent prediction with transition-consistency residuals over multi-step action-conditioned rollouts; open only an observation adapter when the evidence favors observation mismatch, and rollback when a sequential risk monitor worsens.

**Nearest threat:** RePo for encoder-only reward-free adaptation and AdaWM for mismatch-guided selective fine-tuning.

**Difference:** The claim is not selective adaptation itself; it is online factor localization between the observation map and latent transition, paired with an explicit transition-preservation and source-return criterion. RePo assumes an appearance shift and aligns the encoder; AdaWM chooses model versus policy rather than observation versus transition factors.

**Falsification:** On one small fixed-dynamics simulator, the localizer fails if it cannot distinguish held-out sensor transformations from held-out dynamics changes above 80% AUROC, or if its observation-only recovery/forgetting is within the paired 95% CI of faithful RePo adaptation.

### Candidate 2 — adaptation is unnecessary after a calibrated filter

**Claim:** For dropout, delay, and observation outliers with known masks/timestamps, robust filtering and mask/age conditioning explain most apparent world-model TTA gains, leaving learned parameter updates unnecessary.

**Mechanism:** A nonparametric/robust posterior update rejects unlikely measurements and resets contaminated context while preserving the pretrained model.

**Nearest threat:** Outlier-robust generalized-Bayes filtering, Time-Aware World Models, and event-triggered neural processes.

**Difference:** The contribution would be a negative result and controlled boundary map for when filtering suffices versus parameter adaptation, not a new filter.

**Falsification:** Reject if a learned TTA method improves five-step latent/state prediction error by at least 15% over the strongest tuned robust-filter baseline at equal test-time compute on two non-removable shifts.

### Candidate 3 — shift-localization impossibility/boundary result

**Claim:** Without interventions or structural restrictions, observation-process and latent-dynamics shifts are observationally indistinguishable from finite action-observation histories, but paired multi-view observations or known corruption metadata restore identifiability.

**Mechanism:** Construct equivalent latent-state-space parameterizations and characterize which auxiliary signals break the equivalence; validate the boundary empirically.

**Nearest threat:** Classical system identification under partial observations and robust/switching filters.

**Difference:** It would formalize the precise identifiability boundary for routing world-model TTA, not propose another adaptive estimator.

**Falsification:** A history-only classifier generalizes above 90% accuracy to held-out matched observation and dynamics shifts that are constructed to share one-step residual and marginal observation statistics.

## Decomposition verdict

The proposed decomposition is useful as an experimental control but **not novel as stated**. RePo already adapts the encoder reward-free while keeping dynamics and policy fixed. ReOI goes further by keeping the entire model frozen and repairing the observation. TAWM handles one observation-rate factor through conditioning learned during training. A publishable claim would need to explain when to select each strategy, how to identify the affected factor, and how to verify that adaptation did not damage latent dynamics.

## Exactly one smallest valid experiment — design only

### Purpose

Falsify Candidate 1 before any Dreamer-scale control study. The primary test is prediction and shift localization; control is an optional secondary readout.

### System and data

- Environment: programmatic continuous-control cart-pole with exact latent state and actions, rendered to 64x64 RGB. Use fixed physical dynamics for the primary observation-shift arm.
- Pretraining: one compact convolutional RSSM (about 2–5M parameters) per seed on 100k source-rendered transitions collected once by a fixed mixed random/scripted policy. Train to held-out source validation convergence, not a wall-clock toy cutoff.
- Target stream: the same simulator and action policy under three unseen, semantics-preserving observation operators: camera affine/view shift, burst frame dropout with masks, and spatial occlusion. Add one held-out dynamics-change stream (pole length or action gain) only to test localization specificity, not as a second research experiment.
- Recent history only: online minibatches from the latest 32–128 transitions; no latent state, target labels, reward, or source replay during adaptation. Ground-truth state is evaluation-only.

### Exactly four primary conditions

1. **Frozen world model.** No updates.
2. **Naive full fine-tuning.** Update encoder, posterior, transition, and decoder with the same self-supervised one-step and reconstruction objective and exactly matched update count.
3. **Faithful RePo-style adaptation.** Reward-free target encoder alignment with its published support/distribution constraint and calibration; keep transition and policy frozen.
4. **Factor-localized observation adapter.** Freeze the base RSSM; use the residual localizer and update only a small pre-encoder/observation adapter with transition-consistency anchoring and a rollback threshold.

No fifth condition and no simulated/fabricated results. Hyperparameters are fixed on a separate source-to-development shift, never the held-out test operators.

### Measurements and statistics

- primary: one- and five-step state prediction NRMSE using evaluation-only simulator state probes;
- observation/reconstruction NLL or calibrated pixel likelihood where valid;
- pre-shift, first post-shift window, and every 32 transitions through a 1,024-transition recovery curve;
- localization AUROC and detection delay for observation versus dynamics shift;
- expected calibration error or interval coverage for predictive uncertainty;
- source-return forgetting after switching back to the original renderer for 512 transitions;
- adaptation wall time, peak VRAM, gradient steps, and FLOPs/proxy compute;
- optional frozen MPC success/return, reported as secondary only if the small world model supports stable planning.

Use five paired seeds sharing simulator trajectories and corruption schedules across all conditions. Report paired bootstrap 95% confidence intervals for area under the recovery-error curve and forgetting; also report per-seed points. The decisive comparison is Condition 4 versus Condition 3, not versus the frozen straw man.

### Decision rule

Candidate 1 survives only if Condition 4 (a) localizes observation versus dynamics shift with AUROC >= 0.80, (b) reduces recovery-error AUC by at least 15% relative to faithful RePo with a paired 95% CI excluding zero on at least two observation operators, (c) does not improve by merely taking more gradient/FLOP budget, and (d) has at least 50% less source-return forgetting than full fine-tuning. Otherwise reject it.

### Compute estimate

On an RTX 5060 Laptop 8 GB or RTX 3070 8 GB: 1.0–2.5 hours to train each compact RSSM seed; 20–45 minutes for all four adaptation conditions and evaluation streams per seed; approximately 8–17 GPU-hours total for five paired seeds, plus 2–4 CPU-hours for data generation and statistics. Peak VRAM target is under 6 GB with mixed precision and batch size 32. This is a credible pilot, not a 60-second Dreamer substitute.

## Skeptical ICLR review

| Attack | Evidence required to answer it |
|---|---|
| TTA is saturated. | A paper-by-paper claim matrix showing that no prior method localizes observation versus transition factors under the same unlabeled world-model protocol; direct RePo/AdaWM/WorldAgen comparisons. |
| Observation shift is artificial. | At least one physically motivated sensor shift with measured statistics or a real logged sensor degradation, plus results showing the controlled operator predicts that failure. |
| This reduces to encoder adaptation. | A localization task containing both observation and dynamics shifts; show that always adapting the encoder fails on dynamics shift and that routing improves prediction/forgetting beyond RePo. |
| Filtering/system identification already solves it. | A tuned robust-filter/event-trigger/system-ID baseline, precise assumptions table, and a regime where nonlinear visual adaptation wins at equal compute. |
| No planning benefit. | Frozen-controller/MPC result or a causal link between recovery-error AUC and return; otherwise explicitly scope the paper to predictive world models and lower the claim. |
| Selective adaptation is trivial. | Evidence that the localizer, not parameter-count reduction, drives results: oracle routing upper bound, wrong-routing control, and capacity/update-matched adapters. |
| Benchmark is too small. | Use the small system only as falsification; a GO decision would require later validation on at least one accepted visual-control benchmark and one qualitatively different observation shift. |
| Gains are extra test-time compute. | Match update count, wall time, trainable parameters where possible, and report error versus cumulative FLOPs; include a compute-matched full/encoder baseline. |

## Scores and decision

| Criterion | Score / 10 |
|---|---:|
| Novelty | 5.5 |
| Importance | 8.0 |
| Technical depth | 6.5 |
| Experimental feasibility | 8.5 |
| Compute feasibility | 9.0 |
| ICLR fit | 7.5 |
| Probability a meaningful contribution remains | 5.5 |

# PIVOT

Change the project from "selectively adapt the observation component while freezing latent dynamics" to **unlabeled factor localization and safe routing between observation-interface adaptation and latent-dynamics adaptation, with an explicit preservation/rollback criterion**. Treat encoder-only adaptation as the strongest baseline, not the contribution. Run no experiment until a human approves the single pilot above.
