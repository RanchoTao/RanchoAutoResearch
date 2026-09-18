# ARC-23 final report

## Verdict

**INCONCLUSIVE scientific test; KILL this ARC under the META-ARC policy.** The
descriptive quotient-first ordering is strong, but the preregistered exact-task
difficulty control fails badly. No tuning or post-hoc task redesign was used.

## Hypothesis tested

For finite-group state tracking, larger abelianization compression
`|G| / |G/[G,G]|` was hypothesized to produce a larger quotient-before-exact
learning gap and, after matching exact-task mastery, worse length extrapolation.
This would extend the parity-associative mechanism in [(How) Do Language Models
Track State?](https://proceedings.mlr.press/v267/li25r.html) beyond symmetric-group
parity, while differing from the static multiplication setting in [Grokking Group
Multiplication with Cosets](https://proceedings.mlr.press/v235/stander24a.html).

## Experiment

- Nine groups: four order-12 discovery groups and five order-24 held-out groups.
- Five seeds; 45 real training runs; online random products at depths 2–4.
- Four-layer, width-64 Transformers (168,588–170,136 parameters), 1,600 updates.
- Exact and quotient accuracy every 100 steps; exact evaluation at depths 4, 8,
  and 12.
- Quotients were calculated from the Cayley tables via commutator subgroups and
  cosets, rather than supplied as training labels.

## Main results

Values are mean ± sample SD over five seeds. OOD is mean exact accuracy over
depths 8 and 12.

| Group | Order | Compression | Gap AUC | ID exact | OOD exact |
|---|---:|---:|---:|---:|---:|
| C12 | 12 | 1 | 0.000 ± 0.000 | 0.980 ± 0.039 | 0.082 ± 0.013 |
| C6xC2 | 12 | 1 | 0.000 ± 0.000 | 0.992 ± 0.011 | 0.079 ± 0.013 |
| D6 | 12 | 3 | 0.340 ± 0.053 | 0.780 ± 0.045 | 0.085 ± 0.014 |
| A4 | 12 | 4 | 0.528 ± 0.061 | 0.464 ± 0.011 | 0.085 ± 0.005 |
| C12xC2 | 24 | 1 | 0.000 ± 0.000 | 0.914 ± 0.175 | 0.051 ± 0.010 |
| C24 | 24 | 1 | 0.000 ± 0.000 | 0.895 ± 0.163 | 0.042 ± 0.005 |
| Q8xC3 | 24 | 2 | 0.354 ± 0.026 | 0.546 ± 0.056 | 0.043 ± 0.006 |
| D12 | 24 | 6 | 0.445 ± 0.170 | 0.386 ± 0.062 | 0.041 ± 0.003 |
| S4 | 24 | 12 | 0.758 ± 0.023 | 0.198 ± 0.028 | 0.046 ± 0.005 |

Compression versus gap is perfectly rank-ordered at the group-mean level in
both cohorts (Spearman rho = 1.0) and has rho ≥ 0.7 in every seed. However,
compression versus ID exact accuracy is simultaneously rho = -0.949 (order 12)
and -0.975 (order 24). Across all 45 runs, gap versus ID exact accuracy is
rho = -0.879, whereas gap versus OOD exact accuracy is only rho = -0.095.

The OOD exact results are approximately chance (1/12 = 0.083; 1/24 = 0.042)
throughout. Thus the gap does not predict meaningful differences in length
generalization. The apparent law can be fully read as: harder non-abelian product
tasks leave more time during which an easier quotient is correct first.

## Predefined gate

- All groups/seeds ≥95% ID exact: **FAIL** (eight of nine groups have at least
  one failing seed; every non-abelian group has zero passing seeds).
- Compression-gap rho ≥0.7 in both cohorts: **PASS descriptively**.
- Gap-OOD rho ≤-0.7: **FAIL** (rho = -0.095).
- Direction in ≥4/5 seeds in both cohorts: **PASS descriptively**.

Because the mandatory difficulty control failed for multiple groups, the
preregistration requires an inconclusive interpretation rather than a claim.
Because this is the META-ARC's second and final MVP, the project is killed rather
than iteratively tuned.

## Resources and artifacts

- Sum of per-run train/eval timers: 592.9 seconds.
- Peak allocated CUDA memory: 86,420,992 bytes (~82 MiB).
- No paid API, pretrained model, or fabricated/simulated result.
- [`aggregate.json`](../results/aggregate.json)
- [`all_runs.csv`](../results/all_runs.csv)
- [`trajectories.csv`](../results/trajectories.csv)
- [`quotient_gap_controls.png`](../figures/quotient_gap_controls.png)
- [`learning_trajectories.png`](../figures/learning_trajectories.png)

