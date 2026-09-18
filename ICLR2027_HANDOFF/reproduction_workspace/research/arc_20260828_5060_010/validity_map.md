# Validity map

## Decision rule

`VALID` means the stated, bounded claim is supported by stored artifacts and a
consistent assay. `INVALIDATED` means the claim is contradicted, over-broad, or
depends on the withdrawn ARC-006 analysis. `INCONCLUSIVE` means the required
quantity was not identified or tested. `EXPLORATORY` means informative evidence
exists but is outside the confirmatory core. Exact row-level provenance is in
`evidence_ledger.csv`.

## Valid evidence

| ID | Evidence that may enter the main paper | Boundary |
|---|---|---|
| C01-C05 | Nine Pythia-160M runs, a prospective held-out run, confidence and layer controls, and five Pythia-70M runs support an early-to-late decline in block-bypass top-1 substitutability. | WikiText-2; two small scales; one architecture family. |
| C08 | In residual attenuation, predictive damage distinguishes top-1 damage under magnitude matching better than raw displacement does under damage matching. | Discrimination, not KL/NLL causation or mediation. |
| C09 | Norm-controlled additive activation noise reproduces the endpoint direction in 5/5 runs. | Qualitative family robustness only. |
| C12 | Under corrected deterministic top-1 scoring, a KL/NLL-matched intervention-family residual remains: -0.016833044, 95% CI [-0.020044850, -0.012615741], 5/5 run medians negative. | Two intervention families; no identified mechanism. |

## Invalidated evidence and claims

| ID | Invalid statement | Reason |
|---|---|---|
| C06 | Strict checkpoint-by-checkpoint monotonicity or a universal smooth training law. | Sparse trajectories and intermediate rebounds outside the primary 160M set. |
| C07 | Raw perturbation magnitude alone explains the effect. | Magnitude-matched interventions retain a large functional-damage contrast. |
| C10 | One family-invariant KL/NLL-to-top-1 law explains both interventions. | Corrected family residual remains outside the frozen equivalence interval. |
| C11 | ARC-006's mixed-rule residual is valid. | Family-specific `topk` versus `argmax` tie handling invalidated it; ARC-006R supersedes it. |
| C13 | Simple output geometry fully explains the family residual. | The full preregistered geometry block removes only 20.18%; the adjusted residual persists. |

## Inconclusive or exploratory evidence

| ID | Status | Safe interpretation |
|---|---|---|
| C14 | EXPLORATORY | Extracted internal directions are distinct but add little held-out prediction beyond the frozen baseline. |
| C15 | INCONCLUSIVE | Direction causality was never revealed because ARC-009 failed its support gate; neither zero nor nonzero causal effect is established. |
| C16 | INCONCLUSIVE | Corpus robustness is absent: every headline analysis uses the same frozen WikiText-2 source. |
| C17 | EXPLORATORY | One SmolLM2-360M trajectory supplies directional context only and missed the original magnitude gate. |
| C18 | INCONCLUSIVE | The assay has not been connected to downstream capability or deployment/pruning safety. |

## Supersession chain

ARC-006 is retained only as an audit trail. Any exact family residual, reversal
count, or support set used in future writing must come from ARC-006R. ARC-007R,
ARC-008, and ARC-009 all use or verify the corrected baseline. The internal-
direction branch ends at ARC-009's `ALPHA-NOT-FEASIBLE`; no causal direction
effect was unblinded.
