# Ranked paper risks

| Rank | Risk | Current evidence | Severity | Resolution |
|---:|---|---|---|---|
| 1 | Single-corpus dependence | All core and mechanism evidence uses one frozen WikiText-2 source; corpus robustness has never been tested. | HIGH; one major scientific gap | Run the selected cross-corpus replication. |
| 2 | Construct validity and external relevance of `S` | `S` is reproducible and connected to NLL/KL, but it is discontinuous and has no downstream or pruning-safety validation. | HIGH | Triangulate with an alternative metric after the corpus gate; keep claims operational. |
| 3 | Novelty collision with existing layer-robustness/specialization literature | Local evidence contains one direct robustness anchor and internal notes, not a defensible 2025–2026 primary-source map. | FATAL to a novelty claim, but not an artifact defect | Conduct the exact search plan in `literature_search_needed.md` before manuscript drafting. |
| 4 | Model/scale/family scope | Confirmatory evidence covers only 70M and 160M Pythia; SmolLM2-360M is one exploratory trajectory. | HIGH for broad LLM claims; MEDIUM for a bounded small-model paper | Say “two-small-scale replication”; defer scale/family expansion until the assay clears corpus and construct gates. |
| 5 | Intervention-family residual may be assay-specific | Two interventions disagree after matched damage; geometry is partial and direction causality is unidentified. | MEDIUM | Preserve as a bounded finding; a third family is high-value only after the core external-validity tests. |

## Why unresolved mechanism is not ranked as fatal

ARC-004 through ARC-009 already tested and falsified or bounded several simple
explanations. A paper can make an empirical contribution without identifying a
latent causal variable, provided it does not relabel a residual as a mechanism.
The current fatal path is external validity and novelty, not endless mechanism
search.
