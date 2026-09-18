# Corrected sign-reversal analysis

All corrected 24/103 reversal cells were retained.

| Group | Mean disagreement | Median disagreement | Mean log noise/block norm ratio |
| --- | ---: | ---: | ---: |
| Ordinary (79) | 1.000029 | 1.000055 | 0.0052 |
| Reversal (24) | 1.000090 | 1.000047 | 0.2167 |

Directional disagreement distributions are practically identical. Reversal
cells show a larger noise/block norm ratio, but adding both hidden variables to
the output-geometry classifier improves leave-one-run-out AUC by only `0.0026`.
The preregistered incremental AUC requirement was `0.05`.

Thus corrected sign reversals are not characterized by a distinct angular
direction regime. The observed norm-ratio difference is associative and does
not establish a direction mechanism.
