# Functional-damage alignment

## Magnitude-matched comparison

The exact ARC-004 greedy matching and calipers produce 161 HellaSwag pairs.
At nearly equal local relative activation magnitude, the intervention with
higher KL damage also has greater top-1 damage:

- 6/6 run-median contrasts positive.
- Mean run-median contrast: **+0.0404369**.
- Run-bootstrap 95% CI: **[+0.0376338, +0.0437102]**.
- Confirmatory runs: 3/3 positive; mean +0.0403646.
- Median magnitude ratio: 1.01306, below the frozen 1.10 maximum.
- Median absolute KL gap: 0.0828450.
- Median absolute NLL-damage gap: 0.0893893.
- In 98.76% of pairs, higher KL also corresponds to higher NLL damage.

This closely matches the WikiText-2 result (+0.0429688,
95% CI [+0.0353733, +0.0524631]).

## Damage-matched raw-magnitude comparison

The frozen KL/NLL calipers produce 194 pairs:

- 6/6 run medians positive.
- Mean run-median contrast: **+0.00298394**.
- Run-bootstrap 95% CI: **[+0.00155527, +0.00448495]**.
- Median magnitude ratio: 1.11944.
- Median absolute KL gap: 0.00327197.
- Median absolute NLL-damage gap: 0.00454541.

Unlike WikiText-2, whose damage-matched CI included zero, HellaSwag retains a
small positive raw-magnitude residual. It is about 7.4% of the magnitude-matched
functional-damage contrast and satisfies the preregistered “less than half”
criterion. The raw-magnitude alternative is therefore **strongly weakened but
not eliminated** on the new corpus.

## Verdict for Test B

Functional-damage alignment passes the frozen criteria. The safe statement is:

> Across both tested corpora, functional predictive damage is substantially more
> discriminating than raw perturbation magnitude under frozen matching, although
> HellaSwag retains a small damage-matched magnitude component.

This remains discrimination, not evidence that KL or NLL causes ΔS.
