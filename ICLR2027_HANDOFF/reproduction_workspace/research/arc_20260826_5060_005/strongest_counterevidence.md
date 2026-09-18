# Strongest counterevidence

1. **Primary matching feasibility failed.** Only 26/150 block cells (17.3%)
   obtained a frozen 10% joint KL/NLL match, versus the preregistered minimum of
   50 cells, 30% coverage, and five per run. Seed5 had two and seed6 four.
2. **Cross-family equivalence failed on the available support.** The residual
   was -0.01960 with 90% CI [-0.02476, -0.01466], entirely outside the frozen
   ±0.01074 band. Activation noise caused less top-1 damage than deletion at
   comparable KL/NLL damage.
3. **Raw magnitude was not weakened enough within the new family.** Its
   damage-matched residual was +0.02624, 95% CI [+0.02472, +0.02791], or 34.3%
   of the functional contrast; the frozen small-effect threshold was 25%.
4. **A family-by-damage interaction flag triggered.** The slope-difference CI
   excluded zero and its point estimate exceeded the frozen relative threshold.
   However, sparse seed5 matching makes its magnitude unstable.
5. **The worst visualized stratum is only one matched cell.** Seed6, step72k,
   layer4 had residual -0.04688. It is disclosed in Figure 5 but cannot by
   itself support a localized scientific claim.

The most dangerous interpretation error would be to treat the locally balanced
26 matches as if they represented the full intervention support. They do not.
