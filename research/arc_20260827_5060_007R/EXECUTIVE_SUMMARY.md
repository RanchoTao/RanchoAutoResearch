# ARC-20260827-5060-007R executive summary

## Verdict

`GEOMETRY-PARTIAL`

## Answer

Simple decision-boundary geometry does not explain the corrected Candidate A
residual. The families show systematic differences in logit norm and absolute
boundary alignment after KL/NLL matching, and the full preregistered
non-tautological geometry block shrinks the family coefficient by 20.18%.
Nevertheless, the adjusted coefficient is `-0.0134364` (95% CI
`[-0.0176410,-0.0092317]`) and does not enter the frozen equivalence region.

Boundary displacement alone produces negative shrinkage. A 31-cell
outcome-blind geometry-matched subset retains a stronger residual of
`-0.0243634`. Geometry fails to predict the 24/103 corrected reversals at the
frozen gate and increases rather than reduces layer heterogeneity. The far
margin stratum is near zero, but the effect is strongest at medium rather than
near margins.

## Direct answers

1. **Systematic family geometry difference?** Yes for logit norm and absolute
   alignment; no for anchored boundary displacement.
2. **Explained fraction?** M2: -1.49%; M3 block: 20.18%.
3. **Adjusted residual in equivalence?** No.
4. **Most informative quantity?** The joint norm/alignment block; neither
   component is individually identifiable due correlation.
5. **Sign reversals explained?** No; held-out AUC 0.664.
6. **Layer heterogeneity explained?** No; weighted heterogeneity increases
   26.18% after M3.
7. **Near-boundary concentration?** Absent in far-margin examples, but not
   monotonic; medium exceeds near.
8. **Family structure remains?** Yes, substantial and seed-consistent.
9. **Strongest safe claim?** Output-logit geometry is associated with a modest
   portion of the residual but is incomplete.
10. **Unjustified claim?** That decision-boundary geometry causes or explains
    Candidate A.
11. **Next experiment?** One internal perturbation-direction counterfactual
    matched on damage and frozen output geometry.

No new inference, download, API, external compute, or GPU experiment was run.
