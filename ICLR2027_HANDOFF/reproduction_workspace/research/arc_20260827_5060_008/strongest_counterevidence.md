# Strongest counterevidence

1. Directional disagreement is almost a constant: cell SD `0.000290`, seven
   times below the frozen usable-variation threshold.
2. Adding hidden variables misses the residual-prediction gate: 9.63% RMSE
   reduction versus required 10%.
3. Corrected reversal discrimination improves by only 0.0026 AUC.
4. Only 15/103 outcome-blind calibrated cells pass all balance calipers.
5. Runs 2,5,8 each retain only two cells; 14k and 143k each retain only three.
6. Median selected-pair KL/NLL imbalances are roughly 30%, double the 15%
   tolerance, despite hidden norms being closely matched.
7. The apparent layer improvement cannot be assigned to angular direction
   because the augmented block also contains hidden norm ratio.
8. Held-out direction-swap `D_S` was correctly never revealed; there is no
   causal effect estimate to promote.

The key falsification is identification failure: changing block versus random
direction also changes downstream functional damage too strongly for the
frozen design to isolate direction.
