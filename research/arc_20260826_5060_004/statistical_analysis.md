# Statistical analysis

## Analysis units

- Scientific replicates: six independent combined initialization/data-order
  pretraining runs.
- Pilot runs: seeds 1, 4, 9.
- Confirmatory runs: seeds 6, 7, 8.
- Descriptive cells: 720 run-checkpoint-layer-strength cells after averaging
  three fixed evaluation selections.
- Uncertainty: 100,000-sample bootstrap over the six run-level medians. Tokens,
  layers, matched pairs, and evaluation selections are not counted as
  independent scientific replicates.

## Experiment A: raw magnitude held approximately constant

Primary relative-activation matching yielded 185 disjoint within-run,
within-checkpoint pairs.

| Quantity | Result |
| --- | ---: |
| Median magnitude ratio | 1.01933 |
| Median absolute KL separation | 0.08715 |
| Median absolute NLL-damage separation | 0.09829 |
| Higher-KL member also higher-NLL | 94.59% |
| Positive run medians | 6/6 |
| Mean run-median `D_S` contrast | 0.04297 |
| Run-bootstrap 95% interval | [0.03537, 0.05246] |
| Confirmatory positive runs | 3/3 |
| Confirmatory mean run median | 0.03885 |
| Leave-one-run-out mean range | [0.03872, 0.04512] |

The contrast is positive at every checkpoint: mean 0.04051 at step14k,
0.04919 at step72k, and 0.06652 at step143k.

The frozen absolute-RMS sensitivity is stronger, not weaker: 240 pairs, median
magnitude ratio 1.02161, positive in 6/6 runs, mean run-median contrast 0.09480,
95% interval `[0.08887, 0.10062]`, and confirmatory mean 0.09737.

## Experiment B: KL and NLL damage held approximately constant

The pooled prespecified arm yielded 162 disjoint pairs.

| Quantity | Result |
| --- | ---: |
| Median absolute KL gap | 0.00503 |
| Median absolute NLL-damage gap | 0.00704 |
| Median magnitude ratio | 1.12948 |
| Positive run medians | 4/6 |
| Mean run-median `D_S` contrast | 0.00246 |
| Run-bootstrap 95% interval | [-0.00090, 0.00575] |
| Confirmatory mean run median | 0.00582 |

Because eligibility allowed either layer separation or magnitude separation,
the prespecified factor split is important. The 37 pairs with magnitude ratio
at least 1.25 had median ratio 1.34205, mean run-median contrast `-0.00054`, 3/6
positive runs, and 95% interval `[-0.00456, 0.00371]`. Thus the near-zero pooled
result is not explained by insufficient magnitude separation. The 158
location-separated pairs also remained small and heterogeneous: 0.00242,
95% interval `[-0.00101, 0.00575]`.

Checkpoint diagnostics argue against a stable residual magnitude effect. In
the >=1.25 magnitude subset, mean pair contrast was 0.00961 at step14k,
-0.00360 at step72k, and -0.00151 at step143k.

## Confidence control

Among 925 eligible Experiment-A pair/bin cells, 824 (89.08%) were positive.
Mean matched contrasts were positive in all five frozen intact-confidence bins:

`[0.05131, 0.06585, 0.05938, 0.05537, 0.04360]` from lowest to highest bin.

## Secondary associations and models

Simple within-run median Spearman associations with `D_S` were:

- KL: 0.9936;
- NLL damage: 0.9793;
- relative activation magnitude: 0.9753;
- absolute activation RMS: 0.6246;
- alpha x layer-parameter-norm proxy: 0.6076.

These high raw correlations demonstrate why matching was necessary.

With run, checkpoint, and layer fixed controls, standardized coefficients were
0.06039 for KL and 0.07215 for relative magnitude (`R^2=0.9593`, condition
number 14.33). The NLL alternative was similar (0.06126 NLL, 0.06997 magnitude).
The joint KL+NLL model had condition number 28.18, so its split coefficients are
not mechanistically interpretable. All continuous coefficient signs survived
leave-one-run-out analysis.

The longitudinal model left a standardized progress coefficient of only
-0.00174 after KL and magnitude, versus 0.06032 for KL and 0.07224 for
magnitude. One of six leave-one-run-out progress coefficients was positive.
This is consistent with the training association being captured by changing
assay damage variables, but it is not causal mediation evidence.

## Residual location structure

After removing KL, NLL, magnitude, run, and checkpoint associations,
the mean residual layer range was 0.02379 versus a within-run/checkpoint
permutation 95th percentile of 0.01372. Median pairwise run Spearman correlation
of layer profiles was 0.3697 (11/15 pairwise correlations positive).

This satisfies the preregistered supportive H_location criterion, but it is not
a clean directional location mechanism: damage-matched location contrasts
span zero and reverse at the final checkpoint. Location remains a secondary,
unidentified contributor rather than a rival primary explanation.

## Statistical verdict

The matched evidence rejects a **pure raw-magnitude account** within this
intervention family. It favors functional-damage alignment, while retaining
secondary location structure and substantial observational magnitude
association. Because KL/NLL and `D_S` are computed from the same output
distributions and KL was not randomized, the result does not prove that
functional damage causally mediates the original training effect.
