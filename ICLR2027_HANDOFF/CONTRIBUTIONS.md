# Contribution audit

## Sufficiently supported

1. **Independent-run empirical base.** The block-bypass endpoint direction is supported across nine Pythia-160M pretraining runs, a prospectively held-out run, fixed-confidence controls, all tested interior layers, and five Pythia-70M runs. Evidence: ARC-003 frozen summary and run tables.
2. **Two-stream bounded replication.** The direction repeats on a HellaSwag-derived stream in six Pythia-160M runs. Evidence: ARC-011 summary and run-level outputs.
3. **Within-family damage-vs-magnitude discrimination.** Complementary matched contrasts show KL/NLL damage is more informative than raw displacement within residual attenuation. Evidence: ARC-004 mechanism summary and matching tables.
4. **Second-family qualitative replication.** Norm-controlled activation noise reproduces the negative endpoint direction. Evidence: ARC-005 summary.
5. **Corrected prospective family residual.** After joint KL/NLL targeting and a deterministic lowest-index exact-maximum rule, block bypass and activation noise retain a seed-stable aggregate top-1-damage difference. Evidence: ARC-006R corrected summary/results.
6. **Simple output geometry is incomplete.** A preregistered geometry block removes only part of the corrected residual. Evidence: ARC-007R geometry summary.
7. **Transparent negative mechanism result.** Directional causal identification failed prospective support gates; no causal outcome was revealed. Evidence: ARC-008/009 feasibility artifacts.

## Promising but still needing evidence

- Relevance to current billion-scale decoder-only LMs and modern architectures.
- Whether the residual appears on semantic/downstream tasks rather than teacher-forced next-token argmax.
- Whether the phenomenon persists across tokenizers, languages, and additional corpora.
- A principled explanation of the frozen practical-equivalence threshold.
- A mechanistic account that survives prospective causal isolation.
- A stronger methodological result about sufficient intervention matching beyond the two tested damage metrics.

## Claims not recommended

- Discovery that layer redundancy/equivalence changes during training.
- Novelty of `S`, `D_S`, `Delta S`, argmax disagreement, or matched-KL auditing.
- “Output-distribution matching proves functional non-equivalence” without naming the two matched metrics and top-1 endpoint.
- KL/NLL causes, mediates, or fully explains `D_S`.
- Raw magnitude is irrelevant in general.
- Intervention family is universally important or universally invariant.
- A monotone training law, scaling law, universal layer specialization, pruning-safety result, deployment fragility result, or downstream capability loss.
- An identified internal perturbation-direction mechanism.

## Novelty boundary

The novelty audit is `BORDERLINE`. The defensible delta is the combination of independent-pretraining-run replication, two small scales, two evaluation streams, prospective joint KL/NLL matching, deterministic assay repair, and a corrected cross-intervention residual. Each ingredient alone has close precedents; the contribution is the controlled joint evidence and its qualification of protocol-free interpretations.
