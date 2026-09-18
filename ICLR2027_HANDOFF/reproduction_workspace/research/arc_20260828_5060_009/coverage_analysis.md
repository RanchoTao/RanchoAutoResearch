# Coverage analysis

PASS-A support is **47/103**. Frozen coverage gate: **PASS**.

## By seed

| group | count |
|---|---:|
| 2 | 9 |
| 3 | 14 |
| 5 | 10 |
| 6 | 6 |
| 8 | 8 |

## By checkpoint

| group | count |
|---|---:|
| 14000 | 16 |
| 72000 | 18 |
| 143000 | 13 |

## By layer

| group | count |
|---|---:|
| 1 | 4 |
| 2 | 0 |
| 3 | 7 |
| 4 | 8 |
| 5 | 5 |
| 6 | 6 |
| 7 | 3 |
| 8 | 5 |
| 9 | 5 |
| 10 | 4 |

## Concentration

- Maximum seed share: 0.298 (frozen maximum 0.35).
- Maximum checkpoint share: 0.383 (frozen maximum 0.65).
- Damage-regime PASS-A counts: low=20, mid=17, high=10.

Damage regimes are outcome-blind terciles of frozen target KL. They are
descriptive and did not alter cell selection or the verdict.

Run/checkpoint coverage would have passed if total support had reached the
primary N threshold. Layer coverage is not broad: layer 2 has 0/15 PASS-A
cells (12 PASS-B, 3 tradeoff), and layer 7 has only 3 PASS-A cells. The high
damage tercile has 10 PASS-A versus 20 in the low tercile. These concentrations
reinforce, rather than rescue, the below-threshold total support.
