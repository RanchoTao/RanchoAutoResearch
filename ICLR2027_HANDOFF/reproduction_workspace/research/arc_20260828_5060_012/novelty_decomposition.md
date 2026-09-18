# Novelty decomposition

| Dimension | Rating | Reason |
|---|---|---|
| Novel phenomenon | **WEAK** | Static block robustness is established, and Garcia directly reports checkpoint-wise growth of a layer-intervention protocol gap. Quantization and activation-fragility papers also establish training-dependent perturbation sensitivity. |
| Novel empirical regularity | **WEAK** | Function-space damage being more informative than raw distance has strong conceptual precedent. The exact within-assay matching result is narrower than those precedents. |
| Novel control result | **MODERATE** | The corrected prospective KL/NLL matching leaves a seed-stable block-bypass versus activation-noise residual. SteerCheck is a close methodological collision, but studies steering specificity rather than block substitutability over pretraining. |
| Novel methodology | **WEAK** | Preregistration and prospective matching strengthen validity but are not themselves new methods; matched functional budgets already appear in adjacent intervention audits. |
| Novel scope | **MODERATE** | Independent pretraining-run replication, two small Pythia scales, and two corpora are a meaningful extension beyond the closest single-trajectory study, but remain within one architecture family and small scales. |

## Strongest novelty dimension

The strongest defensible delta is the **controlled replication scope**: repeated
pretraining runs plus a prospective, functionally matched comparison of two
intervention families on the same frozen assay.

## Weakest novelty dimension

The `S`/`Delta S` statistic itself has no meaningful novelty, and the broad
claim that layer equivalence changes during training is already occupied.

## Overall

The components do not support a “new layer-redundancy phenomenon” paper. They
may support a narrower qualification paper about how robust the training trend
is across runs/corpora and why its magnitude cannot be interpreted independently
of intervention family.
