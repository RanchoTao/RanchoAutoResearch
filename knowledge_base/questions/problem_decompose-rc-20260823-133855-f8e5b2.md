---
created: '2026-08-23T13:47:23+00:00'
evidence:
- stage-02/problem_tree.md
id: problem_decompose-rc-20260823-133855-f8e5b2
run_id: rc-20260823-133855-f8e5b2
stage: 02-problem_decompose
tags:
- problem_decompose
- stage-02
- run-rc-20260
title: 'Stage 02: Problem Decompose'
---

# Stage 02: Problem Decompose

Warning: Skill descriptions were shortened to fit the skills context budget. Codex can still see every skill, but some descriptions are shorter. Disable unused skills or plugins to leave more room for the rest.


[thinking] **Planning prioritized subquestions in markdown**
## Source

- Topic: World models under structured partial observability.
- Leading candidate: observation-schedule shortcut learning in compact recurrent state-space models.
- Proposed mechanism: visibility-isolated latent updates, where observation masks or age gate posterior evidence but cannot enter the action-conditioned dynamics prior.
- Initial setting: pixel-based DeepMind Control Suite `cartpole/swingup`.
- Decision objective: determine whether the idea merits an ICLR 2027 project before any implementation.
- Evidence status: conceptual only. Novelty, baseline behavior, and performance claims remain unverified pending the literature audit.

## Sub-questions

### 1. Does a fixed observation schedule create a distinct and reproducible shortcut?

- **Setting:** Train an RSSM-style model with a fixed-phase periodic schedule containing two missing frames per eight steps.
- **Question:** Does the model encode schedule phase as if it were part of the environment state?
- **Required comparison:** Keep environment dynamics, trajectories, actions, and approximate missingness fixed while changing only dropout phase, frequency, or burst structure.
- **Evidence:** A substantial return or state-inference decline under schedule shift despite good performance under the training schedule.
- **Falsifier:** The standard model remains stable across schedules, or degradation is fully explained by longer information gaps rather than schedule identity.
- **Importance:** Without this result, there is no demonstrated failure mode for the proposed mechanism to solve.

### 2. Is the failure caused by observation-process entanglement rather than generic information loss?

- **Question:** Can the learned latent representation distinguish physical state from observation availability?
- **Diagnostics:**
  - Linear-probe error for hidden simulator state.
  - Latent divergence between differently masked views of matched trajectories.
  - Predictability of mask phase or observation age from the purported environment latent.
  - Error during dropout versus immediately after observation reacquisition.
- **Falsifier:** Schedule-shift failures occur without increased latent entanglement, or entanglement measures do not predict control failure.
- **Importance:** This establishes the mechanism of failure rather than merely documenting lower performance with missing pixels.

### 3. Does visibility isolation improve robustness beyond strong missing-observation controls?

- **Question:** Does preventing mask information from entering the dynamics prior produce a causal benefit?
- **Proposed mechanism:** Let action-conditioned dynamics evolve without masks or observation age; use visibility only to gate posterior evidence into the predicted state.
- **Essential controls:**
  - Standard recurrent world model.
  - Missing-frame or schedule-randomization augmentation.
  - Mask-aware model without visibility isolation.
  - Parameter-count-matched recurrent model.
- **Falsifier:** Ordinary augmentation or unrestricted mask conditioning matches the proposed method within uncertainty.
- **Importance:** This tests whether structural separation contributes anything beyond additional mask information or regularization.

### 4. Does improved latent-state preservation translate into planning or control gains?

- **Question:** Are representation improvements behaviorally useful rather than cosmetically better on auxiliary diagnostics?
- **Primary metric:** Episodic return under held-out observation schedules.
- **Secondary metric:** Simulator-state linear-probe error during dropout and immediately after reacquisition.
- **Interpretation requirement:** Better returns should coincide with better state preservation, without more than a 3% clean-return reduction.
- **Falsifier:** Latent metrics improve but return does not, or gains arise from conservative actions rather than better belief-state tracking.
- **Importance:** A world-model contribution requires downstream relevance, not only mask-invariant embeddings.

### 5. Is visibility-isolated updating genuinely novel relative to belief-state and missing-observation methods?

- **Question:** Have prior world-model, POMDP, predictive-state, masked-reconstruction, or robust filtering methods already combined:
  1. structured train–test observation-schedule shifts;
  2. isolation of observation availability from latent dynamics; and
  3. downstream planning or control evaluation?
- **Required evidence:** A 15–30-paper literature map, five nearest neighbors, and claim-by-claim comparison using verified primary sources.
- **Falsifier:** A close prior paper already states and evaluates the same central claim; minor architectural differences do n

... (truncated, see full artifact)
