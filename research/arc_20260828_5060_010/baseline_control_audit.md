# Baseline and control audit

## Existing controls

| Control | Present evidence | What it addresses | Residual limitation |
|---|---|---|---|
| Independent pretraining runs | 9×160M; 5×70M | Seed/run idiosyncrasy | Shared training recipe/family. |
| Prospective held-out run | Seed 9 passed frozen interval | Retrospective fit | One held-out run. |
| Intact-confidence bins | 45/45 negative | Confidence/token-mix artifact | Coarse stratification, not exact matching. |
| Intact competence/NLL | NLL improves early→late | Declining base-model competence | One corpus and next-token fit only. |
| Layer-location control | 90/90 negative | Single-layer sign artifact | Strong magnitude heterogeneity remains. |
| Random/size control | Magnitude matching; norm-controlled noise | Pure perturbation-size explanation | Noise is a second family, not a neutral semantic null. |
| Functional-damage matching | KL/NLL-matched cells | Whether damage fully equates families | Predictors share model outputs with `S`. |
| Deterministic tie audit | ARC-006R canonical rule and reversals | Exact argmax implementation artifact | Top-1 remains inherently boundary-sensitive. |
| Output-geometry sequence | ARC-007R | Simple boundary/logit geometry | Only preregistered feature block tested. |
| Blinded causal gate | ARC-008/009 | Post-hoc direction storytelling | Gate failed; no causal estimate. |

## Missing baselines and controls

| Missing item | Scientific importance | Difficulty | GPU | Runtime | Expected paper value |
|---|---|---|---|---|---|
| Distinct evaluation corpus, frozen endpoint contract | CRITICAL | Low–medium | Yes, local | 1–2 h | Highest: directly tests current #1 gap. |
| Continuous/rank-based alternative to top-1 `S` | HIGH | Medium | Possibly none if logits stored; otherwise local | 0–1 h GPU + 4–8 h analysis | High construct-validation value. |
| Matched random-direction/null perturbation | HIGH | Medium | Local | 1–3 h | Distinguishes block structure from generic boundary susceptibility. |
| Downstream/pruning-predictivity endpoint | HIGH | Medium–high | Local, possibly tight | 2–6 h | Links operational assay to consequence. |
| Proper replicated non-Pythia training family | HIGH for generality | High | May exceed convenient local storage/runtime | 4–12 h | High only after corpus/construct gates. |
| 410M/1B scale | MEDIUM | High | 5060 may be slow/tight | 4–12 h | Lower than corpus or construct validation now. |
| Third intervention family | MEDIUM | High engineering | Local | 2–4 h + engineering | Useful for family-residual scope, not core validity. |
| Attention-only versus MLP-only intervention | MEDIUM | Medium | Local | 1–3 h | Mechanistic localization; premature now. |

## Scale evidence conclusion

The correct phrase is **two-small-scale replication**. “Cross-scale” may appear
only with the explicit range 70M–160M and no implication of a scaling law. An
ICLR reviewer could reasonably request 410M/1B or another architecture for broad
claims, but that request has lower expected value than testing the only corpus
and validating the construct. Scaling a corpus artifact would not strengthen
the science.
