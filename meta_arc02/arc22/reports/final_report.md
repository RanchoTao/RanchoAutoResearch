# ARC-22 final report

## Verdict

**KILL.** The preregistered claim that duplicate burstiness itself worsens
generalization does not survive the position control or the held-out generator.

## Primary result

| Generator | Mean massed − spaced fresh NLL | Positive seeds | Interpretation |
|---|---:|---:|---|
| Markov | +0.00835 ± 0.00072 | 5/5 | Entirely driven by the late block |
| Recurrence4 | -0.02180 ± 0.08623 | 2/5 | Direction reverses and is seed-unstable |

For Markov, early and middle massed blocks change NLL by -0.00132 and -0.00124
relative to spacing, while a late block changes it by +0.02759. For Recurrence4,
early massing *improves* NLL by -0.28643, while middle and late worsen it by
+0.08860 and +0.13244. The observed variable is therefore training position and
recovery time, not a generator-independent burstiness penalty.

The memorization diagnostic behaves coherently: late massing produces the largest
fresh-minus-repeated NLL gap in both generators. This confirms that the null is not
caused by a completely insensitive model, but it does not rescue H1.

## Resources

- 60 real training runs, five seeds, two generators, six schedules.
- 129,408 parameters; 469 updates per run.
- Sum of per-run train/eval timers: 199.6 seconds.
- Peak allocated CUDA memory: 72,374,272 bytes (~69 MiB).
- No API calls or pretrained models.

## Artifacts

- [`aggregate.json`](../results/aggregate.json)
- [`all_runs.csv`](../results/all_runs.csv)
- [`fresh_nll_by_schedule.png`](../figures/fresh_nll_by_schedule.png)
- [`position_contrasts.png`](../figures/position_contrasts.png)

The position/recovery phenomenon is not promoted as a pivot: it is expected from
continued clean training and differs sharply by generator. ARC-22 stops.

