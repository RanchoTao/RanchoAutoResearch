# Figure contract

Static Matplotlib PNGs are the selected delivery surface because the ARC
requires regenerable publication-draft files. Every source table will retain
run, checkpoint, layer, family, KL, NLL damage, magnitude, `D_S`, sample count,
match status, and support/discard reason.

Palette policy: hard two-root cap—blue filled circles for block deletion,
orange open triangles for activation noise, charcoal references/equivalence
bands. Family distinction never relies on color alone. White background, quiet
gray grid, honest common axes, neutral descriptive titles and subtitles with
grain/sample counts.

| Figure | Question | Form | Prespecified evidence |
| --- | --- | --- | --- |
| 1 | Is there common functional-damage support? | Faceted empirical CDF plus support rug for KL and NLL | Candidate/retained counts, common-support bounds |
| 2 | Is `D_S` similarly related to damage? | Family-shaped scatter, small-multiple by checkpoint, fixed curves | Individual run-layer observations; no pseudo-CI over tokens |
| 3 | At matched damage, are families similar? | Paired block-vs-noise dot/slope plot by run | Every matched pair plus run medians |
| 4 | Is residual family effect scientifically small? | Run-level forest with 90/95% intervals and equivalence band | Five scientific runs and frozen ±0.010742 bound |
| 5 | Where does alignment fail worst? | Faceted paired residual plot for the prespecified maximum-absolute run/checkpoint/layer or damage-quartile stratum | Exact selection rule and all observations in that stratum |

Every exported figure will be inspected at original resolution for clipping,
labels, marker distinction, scales, and counterevidence visibility.

