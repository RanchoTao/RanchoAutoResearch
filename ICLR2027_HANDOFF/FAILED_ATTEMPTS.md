# Failed attempts, negative evidence, and superseded results

## Scientific negative results

- **Sparse cross-family matching in ARC-005:** only 26/150 strict matches; primary match-quality gate failed. The `-0.01960` exploratory residual is not the paper estimate.
- **Simple output geometry:** explains only 20.18% of the corrected aggregate residual, fails the reversal gate, and does not reduce layer heterogeneity. Classification: scientific negative result / incomplete explanation.
- **Internal-direction observational model:** held-out RMSE improves 9.63%, below the frozen 10% gate; reversal AUC changes only 0.0026. Classification: scientific negative result.
- **ARC-008 causal counterfactual:** only 15/103 cells satisfy joint support; outcome was not revealed. Classification: insufficient statistical support, not a zero effect.
- **ARC-009 continuous-alpha feasibility:** PASS-A 47/103 and PASS-B 29/103; frozen feasibility threshold fails; no `D_S` reveal. Classification: identification design insufficient; branch killed.
- **Uniform family ordering:** 24/103 strict corrected cells reverse sign. Classification: genuine heterogeneity/negative evidence against a uniform cellwise claim.

## Implementation bugs and assay invalidation

- **ARC-006 top-1 tie inconsistency:** one family used `topk` while another used `argmax`, producing inconsistent FP16 tie behavior. All original ARC-006 outcome estimates are invalid. ARC-006R fixes the rule to the lowest token index among exact maximum logits and recomputes outcomes without changing matches/exclusions.
- **ARC-005 analysis serialization:** first final analysis failed on NumPy `int64` JSON serialization. A scalar adapter repaired output serialization only; scientific logic was unchanged.
- **ARC-007R analysis dtype failure:** first corrected analysis stopped before model fitting because of a pandas dtype issue; a documented mechanical repair was applied. Logs are preserved.

## Superseded research and paper positions

- Broad novelty framing (“training changes layer redundancy”) was killed by the literature collision with Garcia 2026 and related work.
- Metric novelty for `S`/`Delta S` was killed by relative-accuracy/divergent-token precedents.
- ARC-010 `PAPER-BORDERLINE` corpus blocker was resolved by ARC-011, but its novelty concern remains and was formalized as ARC-012 `NOVELTY-BORDERLINE`.
- Any phenomenon-first thesis is superseded by the replication-and-qualification thesis in `PROJECT_STATE.md`.

## Unavailable or not evaluated

- Margin damage and token-difficulty stratification were not evaluated in ARC-003 because comparable frozen raw fields were unavailable.
- No billion-parameter, cross-architecture, semantic-task, multilingual, pruning-safety, or deployment robustness experiment exists.
- No causal internal mechanism has been identified.

These entries prevent a new agent from repeating failed routes or silently upgrading inconclusive outcomes.
