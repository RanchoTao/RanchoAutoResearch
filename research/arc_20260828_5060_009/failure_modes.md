# Failure modes

The frozen priority classification produced:

| group | count |
|---|---:|
| PASS-A | 47 |
| PASS-B | 29 |
| FAIL-NO-BRACKET | 0 |
| FAIL-TRADEOFF | 27 |
| FAIL-NUMERICAL | 0 |
| FAIL-PATHOLOGICAL | 0 |

No failed cell was dropped. `FAIL-NO-BRACKET` means at least one frozen target
was unreachable inside `[0.125 beta, 2 beta]`; `FAIL-TRADEOFF` means roots were
numerically available but the unchanged joint damage/geometry conditions could
not all be met. Numerical and pathological failures are reported separately.

The observed pattern is not a grid-resolution failure. All 103 cells bracketed
both targets in both families, and there were zero numerical/pathological
failures. Of the 27 tradeoff cells, 6 failed strict KL balance, 3 failed strict
NLL balance, 11 failed hidden-norm balance, and 10 failed output-norm balance
(categories overlap). Output alignment passed for 103/103.

Among the 29 PASS-B cells, 27 missed only the strict hidden-norm ratio and 2
missed only the strict output-norm ratio. Thus continuous target matching made
damage balance broadly attainable but exposed a genuine downstream magnitude
tradeoff under the unchanged geometry conditions.
