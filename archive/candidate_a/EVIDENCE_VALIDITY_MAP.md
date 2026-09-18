# Candidate A evidence validity map

Only `VALID` rows may support paper claims. `EXPLORATORY` rows may be reported
with that label, `INCONCLUSIVE` rows establish only a limitation or failed gate,
and `INVALIDATED` rows are transparency records only.

| ARC / analysis | Class | Verdict | Scientific role | May support paper claims? | Canonical artifact directory | Important caveat |
| --- | --- | --- | --- | --- | --- | --- |
| ARC-003 | VALID | `PROMOTE-FULL` | Independent-run base, held-out run, confidence/layer controls, 70M replication | Yes | `meta_arc05/ARC-20260826-5060-003/` | WikiText-2 and small Pythia; no universal or strictly monotone law |
| ARC-004 | VALID | `MECHANISM-GO` | Magnitude- and damage-matched within-family discrimination | Yes | `research/arc_20260826_5060_004/` | KL/NLL not randomized; controlled association, not mediation |
| ARC-005 qualitative noise replication | VALID | `FAMILY-PARTIAL` | Second intervention family reproduces endpoint direction | Yes | `research/arc_20260826_5060_005/` | Five runs; quantitative family invariance is not supported |
| ARC-005 sparse family residual | EXPLORATORY | Match-quality gate failed | Motivated prospective inverse targeting | No as headline estimate | `research/arc_20260826_5060_005/` | Only 26/150 strict matches and uneven run support |
| ARC-006 matching assignments/diagnostics | VALID | Targeting quality passed | Defines the 150 targets and unchanged prospective support classes | Yes for matching provenance only | `research/arc_20260826_5060_006/` | Outcome values are superseded; assignments survive the repair |
| ARC-006 outcome analysis | INVALIDATED | Withdrawn | Original cross-family residual and reversal analysis | **No** | `research/arc_20260826_5060_006/` | Mixed `topk`/`argmax` tie handling; never reuse exact outcome estimates |
| ARC-006R | VALID | `006R-RESIDUAL-CONFIRMED` | Canonical deterministic top-1 repair and corrected family residual | Yes | `research/arc_20260827_5060_006R/` | Pythia-160M, WikiText-2, block bypass versus activation noise only |
| ARC-007R | VALID | `GEOMETRY-PARTIAL` | Frozen output-geometry decomposition of corrected residual | Yes, associationally | `research/arc_20260827_5060_007R/` | Geometry block is correlated and does not identify causality |
| ARC-008 observational direction analysis | EXPLORATORY | `DIRECTION-NONIDENTIFIABLE` | Shows nearly orthogonal hidden directions and failed predictive gates | Only as labeled negative evidence | `research/arc_20260827_5060_008/` | Held-out RMSE/AUC improvements miss frozen gates |
| ARC-008 counterfactual direction test | INCONCLUSIVE | Support gate failed | Attempted causal direction isolation | No | `research/arc_20260827_5060_008/` | 15/103 support; top-1 outcome never revealed |
| ARC-009 | INCONCLUSIVE | `ALPHA-NOT-FEASIBLE` | Continuous-alpha feasibility test | No causal claim | `research/arc_20260828_5060_009/` | 47/103 PASS-A, 29/103 PASS-B; no `D_S` reveal |
| ARC-010 evidence audit | VALID | `PAPER-BORDERLINE` | Evidence reconciliation, supersession chain, paper risk audit | Yes as audit provenance | `research/arc_20260828_5060_010/` | Its corpus blocker is superseded by ARC-011 |
| ARC-011 | VALID | `CORPUS-GO` | HellaSwag-derived replication and matched controls | Yes | `research/arc_20260828_5060_011/` | Same architecture/tokenizer; effect is smaller and not corpus invariant |
| ARC-012 | VALID | `NOVELTY-BORDERLINE` | Formal novelty collision map and narrow positioning | Yes for positioning | `research/arc_20260828_5060_012/` | Broad phenomenon novelty is weak and metric novelty is none |

## Mandatory supersession rule

```text
ARC-006 original results -> INVALIDATED
ARC-006R -> canonical corrected evidence
```

All geometry and direction analyses must use the ARC-006R baseline. No future
agent may recover an ARC-006 outcome value merely because the file still exists.
