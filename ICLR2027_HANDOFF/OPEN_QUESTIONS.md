# Open questions and revision backlog

## Motivation / So What

- Explain why protocol-conditioned intervention responses matter for claims about redundancy, necessity, pruning, editing, and mechanistic interpretation.
- Connect the small-model assay to methodological reliability without implying that large deployed LLMs have already been tested.
- State what decision changes when KL/NLL matching fails to equalize top-1 damage.

## Related Work

- Build a narrow map around Garcia 2026, Lad et al. 2025, SteerCheck, Divergent Token Metrics, training-time perturbation fragility, and activation-patching validity.
- Put the closest collisions in the Introduction, not only a broad XAI survey.
- Confirm that every 2026 preprint remains current before submission.

## Theory and definitions

- Define “intervention equivalence,” “predictive-damage matching,” and “behavioral interchangeability” precisely.
- Explain why matching two scalar logit-derived summaries is weaker than matching the full output distribution or function.
- Add a minimal counterexample/proposition only if rigorously checked; do not label the Jacobian intuition a theorem.
- Clarify the statistical estimand under incomplete 103/150 matching support.

## Models

Current 70M/160M Pythia evidence is insufficient for a strong modern-LLM claim. Future candidates, in staged order only after authorization:

1. a Qwen-family approximately 3–4B model;
2. a modern decoder-only 2B/7B model;
3. a Qwen-family approximately 27B model only after smaller-model evidence;
4. MoE only if scientifically necessary.

No model should be downloaded or run as part of this handoff.

## Main figure

Design one overview showing intact model/checkpoints, attenuation and noise interventions, joint KL/NLL matching, `D_S` residual, and the exact non-claim boundary. It must be a method/evidence map, not decorative art.

## Narrative

- Lead with measurement reliability under internal interventions.
- Present independent-run/corpus replication as the empirical base.
- Present matching as an attempted reduction, followed by the residual and incomplete geometry explanation.
- Keep the failed causal direction work as an integrity/limitation result.

## Robustness backlog

- Clean-environment reproduction and deterministic hash check.
- Additional modern architecture/scale only after preregistration.
- Confidence intervals and sensitivity for layer heterogeneity and unmatched support.
- Equivalence-band sensitivity and justification.
- Alternative semantic/downstream endpoint.
- Tokenizer/language/corpus extension.
- Explicit robustness of matching to caliper choice without outcome-tuned thresholds.

## Author/submission metadata

The current manuscript is anonymous. Verified non-anonymous author names, affiliations, contact email, submission ID, and final author order are absent from the package and must be supplied by the human research team.
