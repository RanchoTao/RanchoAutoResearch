# ARC-20260826-5060-006 final report

## Primary verdict

**TARGETING-FAMILY**

**Confidence: HIGH for the frozen Pythia-160M assay; not a universality claim.**

Prospective inverse targeting substantially improved joint functional-damage
support, yet the family residual remained almost unchanged and clearly outside
the frozen equivalence region. The sparse ARC-005 post-hoc match was therefore
not the main explanation for the observed offset.

## Contract and blinding

The assay definitions, targets, tolerances, equivalence band, aggregation, and
verdict logic were frozen before reveal. Target optimization accessed only
strength, KL, NLL, identity, and technical diagnostics. It neither computed nor
logged `D_S`. The confirmatory target manifest and reveal/analysis code were
sealed in commit `282b3663dd541aedffd4c4bca4e2b7683deb452c`; only then was
`D_S` evaluated. No target strength, class, threshold, seed, checkpoint, or
layer was changed after reveal.

## Targeting result

| Measure | Result |
| --- | ---: |
| Targets | 150 |
| Class A | 103 (68.67%) |
| Class A+B | 134 (89.33%) |
| Class C | 16 (10.67%) |
| Mean relative KL error, all targets | 3.89% |
| Mean relative NLL error, all targets | 4.17% |
| Mean relative KL error, Class A | 1.94% |
| Mean relative NLL error, Class A | 1.87% |
| Boundary solutions | 0 |
| Frozen quality gate | PASS |

This raises strict coverage from ARC-005's 26/150 (17.3%) to 103/150 (68.7%),
a 3.96-fold increase. A+B coverage is 134/150 (89.3%). All run, checkpoint,
layer, harness, reproducibility, and median-error sub-gates passed.

## Reveal result

The Class A primary mean of five run medians is **-0.019235**. Its 90% bootstrap
CI is [-0.022801, -0.014851] and 95% CI is
**[-0.023206, -0.013715]**. All five run medians are negative; every
leave-one-run-out estimate remains below the negative equivalence boundary.

The frozen equivalence band is +/-0.010742. The primary interval is wholly
outside it. ARC-005 estimated -0.019604; ARC-006 estimated -0.019235, only
**1.88% shrinkage**. A+B sensitivity gives -0.021376 (95% CI
[-0.025434, -0.016529]), also outside equivalence.

## Family-invariant curve result

The simple frozen diagnostic estimates a family offset of -0.020066 but no
strong family-by-damage slope interaction: mean cross-run slope difference
-0.001689, 95% CI [-0.006043, +0.002665]. The current data are better described
as approximately parallel damage relationships with a family-specific offset
than as a single invariant curve or strongly different slopes.

## Answers to the paper-level questions

1. **Did targeting improve quality?** Yes: strict coverage increased from 17.3%
   to 68.7%; acceptable coverage reached 89.3%.
2. **Class A fraction?** 103/150, 68.67%.
3. **Class A+B fraction?** 134/150, 89.33%.
4. **New residual?** -0.019235, 95% CI [-0.023206, -0.013715].
5. **Compared with ARC-005?** Nearly identical to -0.019604; 1.88% shrinkage.
6. **Inside equivalence?** No; the entire 95% CI is below -0.010742.
7. **Did poor overlap inflate ARC-005?** At most minimally under this design;
   the point estimate barely moved after a 3.96-fold strict-coverage increase.
8. **Does a family component remain?** Yes, conditional on frozen KL/NLL and
   this assay.
9. **Family-by-damage interactions?** No strong interaction was detected; the
   run-slope-difference interval includes zero.
10. **Strongest safe claim?** Functional damage aligns with Candidate A across
    both families, but a reproducible family offset remains after prospective
    joint KL/NLL matching.
11. **No longer defensible?** A family-invariant KL/NLL-to-`D_S` curve.
12. **Next reviewer attack?** Shared-logit/decision-boundary geometry may explain
    the offset without a deeper intervention-specific mechanism.

## Negative evidence

Strict Class A coverage was 1.33 percentage points below the aspirational 70%
description, although it exceeded the frozen gate and A+B reached 89.3%.
Eighteen Class A cells reversed the aggregate sign. Layer means were
heterogeneous, and layer 7 had only three Class A matches. The worst target was
Class C with 16.45% KL and 23.42% NLL relative error. These facts rule out a
uniform cellwise effect and motivate decision-boundary analysis.

## Resource use

- Local GPU only: NVIDIA RTX 5060 Laptop GPU.
- Measured GPU-stage/checkpoint runtime: 2,244.98 seconds (0.624 hours),
  including pilot, refined pilot, confirmation, and reveal.
- Confirmatory targeting: 1,911.65 seconds; reveal: 79.22 seconds.
- Wall time from baseline to completed analysis: approximately 53 minutes;
  final documentation and integrity checks add only CPU time.
- Peak allocated CUDA memory: 1,062,199,808 bytes (about 1.06 GB decimal).
- Peak process RAM: not instrumented; no retrospective estimate is reported.
- Initial ARC size: 78,550 bytes; final pre-integrity size excluding generated
  `__pycache__`: 3,536,901 bytes (3.30 MiB added).
- API cost: USD 0.
- External compute cost: USD 0.
- Model downloads: none.

## Recommended next ARC

Run one decision-boundary-geometry ARC using the already sealed interventions.
Test whether intact margin and the direction/distribution of logit changes
absorb the family offset after KL/NLL matching. Do not add an intervention
family or scale models until this shared-logit confound is resolved.
