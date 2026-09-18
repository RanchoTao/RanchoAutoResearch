# Precision incident and protocol correction

The first full trajectory attempt loaded SmolLM2 BF16 weights as FP16 to mirror
the prior Pythia evaluator. It is invalid and is not used for scientific
inference.

Observed failure:

- step1.92M intact NLL was NaN in all three evaluation resamples;
- all 90 step1.92M layer/resample rows had nonfinite NLL damage or KL;
- one layer row was also nonfinite at step320k and step2.56M;
- top-1 agreement remains numerically populated under NaN logits because
  `argmax` returns an index, so agreement alone cannot validate the run.

The raw invalid artifact is preserved with SHA-256
`FFDE3D0DA07596240C5178710FFBC5ECB7A8047AB21C00B36A3D22A7F70E735C`.

SmolLM2's official config and model card specify BF16 training/weights. The
minimal scientifically necessary correction is therefore to use native BF16
for this family. The config now fixes `dtype: bfloat16`; downstream competence
and all five trajectory checkpoints are rerun from scratch. No checkpoint,
layer, sample, metric, or verdict threshold changes. FP16 results remain
available only as harness-failure evidence.

