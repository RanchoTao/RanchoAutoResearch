# Corrected ARC-006 report

## Verdict

**006R-RESIDUAL-CONFIRMED**

The canonical same-rule residual is -0.016833044 with 95% CI
[-0.020044850, -0.012615741].
All 5/5 run medians are negative; every leave-one-run-out
estimate remains below the frozen negative equivalence boundary. The point and
interval do not satisfy equivalence.

## Repair effect

The invalid mixed estimate was -0.019234664. The correction is
+0.002401620, or 12.49% of its magnitude. The
qualitative family-residual conclusion survives;
the invalid exact estimate remains withdrawn.

## Robustness

The globally consistent `topk` estimate is
-0.016796875. Its difference from the
canonical estimate is 0.000036169, below the frozen 0.0025 numeric
instability threshold. Class A+B gives
-0.018156829.

## Sign reversals and layers

Reversals change from 18 to
24 of 103, with
8 cells changing membership. Layer weighted
heterogeneity changes from 0.016833 to
0.017455; low-support layers remain
[7].

## Scientific boundary

This repair establishes only whether the family-associated residual survives a
consistent top-1 assay in the frozen Pythia-160M experiment. It does not explain
the residual, establish geometry or causality, or extend to another model,
corpus, scale, or intervention family.
