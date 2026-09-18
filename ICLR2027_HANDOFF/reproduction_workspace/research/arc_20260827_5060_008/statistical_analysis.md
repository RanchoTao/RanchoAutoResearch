# Statistical analysis

## Units and models

The scientific unit is one frozen run/checkpoint/layer cell. Token observations
were reduced to cell summaries. Generalization was evaluated by leaving out
one entire pretraining run. The baseline contained mean KL/NLL, ARC-007R output
geometry, checkpoint, and layer; the augmented model added hidden directional
disagreement and log noise/block hidden-norm ratio.

| Analysis | Baseline | Augmented | Change | Frozen gate |
| --- | ---: | ---: | ---: | --- |
| Residual RMSE | 0.013329 | 0.012045 | 9.63% lower | >=10% |
| Reversal AUC | 0.8602 | 0.8629 | +0.0026 | >=0.70 and +0.05 |
| Reversal balanced accuracy | — | 0.8217 | — | secondary |

Neither augmented analysis crosses its frozen gate. The high baseline reversal
AUC comes from already known damage/output geometry and nuisance structure;
internal direction adds essentially nothing.

Layer-median residual SD fell from `0.012621` to `0.006765` after adding the
hidden block, a 46.4% observational reduction. Because the block includes norm
ratio, disagreement is nearly constant, and Stage B is unidentified, this is a
correlational layer-structure clue only.

No counterfactual effect, confidence interval, seed consistency, or effect
fraction relative to `-0.016833` exists: the confirmatory outcome remained
sealed after support failure.
