# Frozen confidence control

All five preregistered intact-confidence bins have sufficient early and late
support in every run, yielding 30 run-bin comparisons.

- Eligible comparisons: 30
- Negative comparisons: 30/30
- Mean within-bin ΔS: -0.0894881
- Median within-bin ΔS: -0.0929936
- Bootstrap 95% CI over per-run mean bin effects:
  [-0.1002919, -0.0740966]
- Per-run mean bin effects: seed1 -0.0538901; seed4 -0.1039029; seed6
  -0.0911424; seed7 -0.0974554; seed8 -0.1026738; seed9 -0.0878639.

The least-negative comparison is seed1 in the `[0,.05)` bin: -0.012684,
with 1,100 early and 1,050 late layer-token observations. It is retained and
reported as the strongest confidence-control counterexample.

The new-corpus effect is not eliminated by fixed intact confidence. This does
not equal exact propensity matching and does not control every token property.
