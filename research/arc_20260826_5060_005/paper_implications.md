# Paper implications

## Claim currently supported

Across block deletion and norm-controlled additive activation noise in
Pythia-160M, later checkpoints show lower top-1 agreement with their intact
predictions under perturbation. Functional predictive damage is strongly
associated with top-1 damage within both assays, but the quantitative mapping
is not demonstrably intervention-family invariant.

## Claim not supported

- KL or NLL damage is the causal mechanism of Candidate A.
- Raw perturbation magnitude is irrelevant once KL/NLL are matched.
- A single family-independent damage-to-ΔS curve exists.
- The observed residual generalizes beyond the sparse matched support.
- The result is universal across architectures, corpora, or scale.

## Potential result-section outline

1. Freeze and reproduce Candidate A with block deletion.
2. Introduce a structurally distinct, norm-controlled activation intervention.
3. Show five-run qualitative replication and confidence controls.
4. Compare functional-damage and magnitude-matched contrasts within family.
5. Report sparse cross-family support, failed equivalence, and interaction.
6. Treat family dependence and shared-logit measurement as unresolved risks.

## Paper-killing risk

The result may reduce to two output-derived damage metrics co-moving differently
under two perturbation geometries. Without exact common-support targeting and an
independent outcome/measurement, the current mechanism story is not ICLR-ready.
