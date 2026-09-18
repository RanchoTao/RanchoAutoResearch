# Strongest counterevidence

1. **Least supportive primary metric:** adding anchored boundary displacement
   changes the family coefficient from `-0.0170012` to `-0.0170836`; shrinkage
   is `-1.49%`, not an explanation.
2. **Geometry-matched persistence:** the sealed 31-cell subset has residual
   `-0.0243634`, 95% CI `[-0.0300637,-0.0181858]`.
3. **Worst run after M3:** seed 6 remains at `-0.0204839`; seed 8 remains at
   `-0.0177082`.
4. **Worst supported layer:** layer 6 is `-0.0490317` after M3. Layer 7 is even
   more negative (`-0.0544057`) but is not interpretable with three cells.
5. **Layer failure:** geometry increases weighted layer heterogeneity by
   26.18% rather than reducing it.
6. **Hard-to-explain reversals:** the leave-one-run-out geometry classifier
   gives AUC `0.664`, missing its preregistered gate. For example,
   `r2_s14000_l10` is a true reversal assigned probability `0.151`.
7. **Largest unexplained cell residual:** `r8_s143000_l4` has corrected residual
   `-0.078631` despite saved geometry being available.
8. **No equivalence:** M3 is `-0.0134364`, with 95% CI
   `[-0.0176410,-0.0092317]`; its point estimate remains outside the frozen
   band.

These observations rule out a strong claim that local output-logit geometry
accounts for Candidate A.
