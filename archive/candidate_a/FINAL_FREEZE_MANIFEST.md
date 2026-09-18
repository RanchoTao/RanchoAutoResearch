# Candidate A final freeze manifest

## Freeze identity

- Project: Candidate A
- Status: `PAPER FREEZE`
- Repository branch: `main`
- Freeze commit: `5ba0df6518e6d1782ae46001150e6df0dda684a0`
- Freeze tag: `Candidate-A-Paper-Freeze-v1`
- Tag timestamp: `2026-08-28T23:26:58+08:00`
- Manuscript title: *Intervention-Conditioned Layer Fragility Across Language-Model Pretraining*

The annotated tag points to the validated ICLR 2027 Draft 2 commit. Later
archival commits do not move the tag or redefine the frozen scientific state.

## Scientific question

Within a controlled small-Pythia assay, does robustness to an interior-block
intervention change over pretraining, and can the measured response be reduced
to raw perturbation magnitude or matched output-level KL/NLL damage?

## Frozen paper thesis

Across independently pretrained small Pythia runs, top-1 robustness to
interior-block bypass declines from competent early to late checkpoints on two
evaluation streams. Raw displacement is insufficient within residual
attenuation, while prospective joint KL/NLL matching does not make block
bypass and norm-controlled activation noise behaviorally interchangeable.
Simple frozen output-geometry controls account for only part of the corrected
family residual. This is an intervention-conditioned replication and
qualification result, not a universal training law or identified mechanism.

## Validated ARC chain

1. **ARC-003:** established independent-run, held-out, confidence, layer, and
   second-small-scale robustness for the block-bypass endpoint.
2. **ARC-004:** showed through complementary matched contrasts that functional
   predictive damage is more informative than raw displacement within the
   frozen attenuation assay, without identifying KL/NLL causality.
3. **ARC-005:** supplied valid qualitative replication with norm-controlled
   activation noise; its sparse cross-family residual remained exploratory.
4. **ARC-006:** improved prospective matching support, but its outcome analysis
   was later invalidated by inconsistent top-1 tie handling.
5. **ARC-006R:** froze a family-independent lowest-index exact-maximum rule and
   produced the canonical corrected cross-family result.
6. **ARC-007R:** found that a frozen output-geometry block explains only part of
   the corrected residual.
7. **ARC-008:** found distinct hidden directions observationally, but causal
   identification failed the outcome-blind support gate.
8. **ARC-009:** improved calibration support but failed its frozen feasibility
   gate; no top-1 outcome was revealed and the direction branch terminated.
9. **ARC-010:** consolidated and audited the evidence; its corpus blocker was
   later resolved.
10. **ARC-011:** reproduced the endpoint and matched-control ordering on a
    HellaSwag-derived stream, advancing the empirical paper state to `PAPER-GO`.
11. **ARC-012:** returned `NOVELTY-BORDERLINE` and froze the narrower
    replication-and-qualification positioning.

## Superseded and invalidated results

The following rule is absolute:

```text
ARC-006 original results -> INVALIDATED
ARC-006R -> canonical corrected evidence
```

No original ARC-006 cross-family `D_S`, residual, reversal count, or downstream
analysis may support a paper claim. ARC-005's sparse cross-family estimate is
exploratory only. ARC-010's missing-corpus blocker is superseded by ARC-011,
and all phenomenon-first novelty framing is superseded by ARC-012.

## Canonical numerical results

The authoritative value-by-value ledger is
`manuscript/numerical_provenance.csv`; the compact frozen table is
`FROZEN_RESULTS.md`. Headline valid results include:

- Pythia-160M block bypass: 9/9 negative; mean `Delta S=-0.103527681`, 95% CI
  `[-0.111494502, -0.095847620]`.
- Pythia-70M: 5/5 negative; median `Delta S=-0.143338`, 95% CI
  `[-0.153852, -0.110297]`.
- HellaSwag-derived stream: 6/6 negative; mean `Delta S=-0.079264`, 95% CI
  `[-0.088509, -0.067672]`.
- Magnitude-matched functional-damage contrast: `+0.04296875`, 95% CI
  `[0.0353733, 0.0524631]`.
- Damage-matched raw-magnitude contrast: `+0.002459`, 95% CI
  `[-0.000904, 0.005751]`.
- Corrected ARC-006R family residual: `-0.016833044`, 95% CI
  `[-0.020044850, -0.012615741]`, with 5/5 negative run medians.
- Geometry-adjusted residual: `-0.0134364`, 95% CI
  `[-0.0176410, -0.0092317]`.

## Novelty position

Novelty is `BORDERLINE`, with high-confidence literature coverage. No novelty
is claimed for top-1 agreement, `S`, `Delta S`, broad training-dependent layer
equivalence, or intervention-protocol dependence. *No Free Swap* is the closest
collision; Lad et al. and DTM delimit assay/metric novelty, and SteerCheck is a
matched-intervention methodological near-neighbor. The remaining contribution
is the combined independent-run, two-small-scale, two-stream replication and
prospective corrected cross-intervention control.

## Known limitations

- Pythia only; 70M and 160M only.
- Two English evaluation streams with one tokenizer.
- Two intervention families; the corrected cross-family analysis is 160M and
  WikiText-2 only.
- `S` is discontinuous teacher-forced top-1 agreement, not semantic
  equivalence, downstream capability, pruning safety, or deployment fragility.
- KL, NLL, geometry, and `D_S` share logits; matching is not causal mediation.
- Twenty-four of 103 corrected cells reverse sign and layer effects are
  heterogeneous; layer 7 has low strict-match support.
- Internal perturbation-direction causality remains unidentified.

## Known reviewer risks

The highest risks are incremental significance relative to *No Free Swap*, the
scientific meaning and incompleteness of KL/NLL matching, justification of the
`+/-0.010742188` equivalence threshold, only five independent cross-family
runs, unmatched-cell representation at 103/150 strict support, small-model
scope, and lack of a positive internal mechanism.

## Manuscript and package state

- Verdict at freeze: `DRAFT2-PAGE-GO`.
- Main text: 8 pages.
- Total PDF: 11 pages.
- Official locally supplied ICLR 2027 style: unchanged.
- Anonymous mode and required statements: present.
- Extracted Overleaf ZIP clean build: pass with pdfLaTeX plus BibTeX.
- Undefined citations/references and overfull boxes: zero.
- Final PDF and source ZIP are preserved under `manuscript/` and hashed in
  `SHA256SUMS.txt`.

## Contamination barrier

Candidate B/C work must not modify Candidate A ARC directories, cached results,
figures, numerical provenance, experimental IDs, or frozen paper artifacts.
Shared model/dataset caches may be reused read-only. Candidate A hypotheses or
results may be cited as prior project state but must not be silently presented
as new findings in another candidate.
