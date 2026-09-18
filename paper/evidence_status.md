# Candidate A evidence status for Draft 0

This table reconciles the evidence chain before manuscript drafting. `VALID`
evidence may support main claims; `EXPLORATORY` evidence is labeled as such;
`INCONCLUSIVE` evidence appears only as a limitation; `INVALIDATED` evidence is
retained solely for transparency.

| ARC | Status | Evidence usable in Draft 0 | Boundary / disposition |
|---|---|---|---|
| ARC-003 | **VALID** | Nine independent Pythia-160M runs, held-out seed9, fixed-confidence and layer controls; 70M directional replication | WikiText-2, two small Pythia scales, block bypass; no universal training law |
| ARC-004 | **VALID** | Within residual attenuation, functional damage discriminates top-1 damage better than raw displacement under frozen matching | Controlled discrimination only; KL/NLL are not randomized mediators |
| ARC-005 | **VALID** for qualitative second-family replication; **EXPLORATORY** for its sparse cross-family residual | Norm-controlled additive activation noise gives 5/5 negative endpoint changes | Original cross-family match-quality gate failed; do not use its residual as the paper estimate |
| ARC-006 | **INVALIDATED** | None of the original cross-family `D_S`, reversal, or residual values | Mixed `topk`/`argmax` tie handling made the outcome contrast inconsistent |
| ARC-006R | **VALID** | Canonical deterministic-top-1 repair; corrected residual `-0.016833044`; 5/5 negative run medians | Only block bypass versus activation noise, Pythia-160M, WikiText-2 |
| ARC-007R | **VALID** | Frozen simple output-geometry block removes 20.18% of the corrected residual; adjusted residual remains | Associational decomposition, not causal mechanism identification |
| ARC-008 | **EXPLORATORY** observationally; **INCONCLUSIVE** causally | Directions differ; held-out improvement misses gate | Counterfactual reveal stopped at support gate; no direction effect was measured |
| ARC-009 | **INCONCLUSIVE** | Continuous-alpha design improves support but fails the frozen feasibility gate | No `D_S` reveal and no causal estimate; mechanism branch ends |
| ARC-010 | **VALID audit** | Recomputed evidence ledger, validity map, assay supersession chain | Its corpus blocker is superseded by ARC-011; original novelty uncertainty is superseded by ARC-012 |
| ARC-011 | **VALID** | HellaSwag-derived corpus: 6/6 negative, confidence and matching controls reproduce | Two English corpora, same tokenizer and architecture family; smaller magnitude |
| ARC-012 | **VALID literature audit** | Formal collision map and narrow intervention-conditioned positioning | Broad phenomenon and metric novelty are rejected; final novelty status remains borderline |

## Supersession rules

1. Any exact cross-family residual must cite ARC-006R, never ARC-006.
2. ARC-007R, ARC-008, and ARC-009 are interpreted against the corrected ARC-006R baseline.
3. ARC-011 supersedes ARC-010's `C16` corpus-inconclusive row, but does not expand beyond two English corpora.
4. ARC-012 supersedes the older phenomenon-first paper thesis.
