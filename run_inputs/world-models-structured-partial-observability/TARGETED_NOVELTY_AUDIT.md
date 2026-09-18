# Targeted novelty audit addendum

This addendum covers the blind spots explicitly identified by Stage 7. It used
the project’s real OpenAlex and arXiv clients with the queries in
`targeted_novelty_queries.txt`. All 143 retrieved records are preserved in
`targeted_novelty_candidates.jsonl`.

## Strong new novelty threat

**Flow Equivariant World Models: Memory for Partially Observed Dynamic
Environments** (Lillemark et al., 2026; arXiv:2601.01075) introduces a latent
memory that transforms equivariantly with self-motion and inferred object motion
and evaluates against diffusion, recurrent, and memory-augmented world models on
2D and 3D partially observed video benchmarks. This work removes generic
"symmetry-aware memory under partial observability" from the defensible novelty
space. The proposed project must instead isolate held-out changes in the
observation process while keeping environment dynamics fixed.

## Relevant diagnostic neighbor

**Prediction-Based Markov Violation Scores for Detecting Non-Markovian
Observations in Reinforcement Learning** (Mysore, 2026; arXiv:2603.27389)
provides a post-hoc diagnostic for non-Markovian observations and reports both
successful detections and a low-dimensional inversion failure mode. It is a
strong diagnostic baseline but does not, from its abstract, optimize a world
model for held-out observation mechanisms.

## Adjacent missing-sensor baseline

**Increasing the Robustness of Model Predictions to Missing Sensors in Earth
Observation** (Mena et al., 2024; arXiv:2407.15512,
doi:10.1007/978-3-032-25311-8_14) studies input-sensor dropout and
sensor-invariant ensembles on multi-sensor temporal datasets. It is outside RL
world models but makes ordinary sensor dropout and invariant ensembles mandatory
baselines.

## Audit conclusion

Novelty remains **unverified**. The broad topic is a **PIVOT**, not a GO. A
defensible pilot can test whether severity-matched observation-process shift is
a real residual phenomenon, but no new method claim should be made unless it
beats mask/age conditioning, mixed-corruption augmentation, sensor dropout,
matched ensembles, recurrent model-free policies, and a dynamics-equivariant
memory baseline.
