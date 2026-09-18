# WSD-window preregistration

Frozen on 2026-08-25 before inference at steps 2.08M, 2.24M, or 2.40M and
before inspecting any new dense-window result.

## Fixed scientific question

Determine whether the established SmolLM2-360M endpoint degradation is already
meaningful before the final WSD decay, is distributed through the decay window,
is concentrated at the final checkpoint, or has no stable temporal structure.
This ARC determines *when*, not why.

## Authoritative schedule and boundary

The official checkpoint card states that branches are released every 160,000
steps and that each step represents 1,572,864 tokens. The official paper states
that SmolLM2-360M was trained for 4T tokens using WSD with 20% decay. The public
trajectory ends at step 2,560,000 (4,026,531,840,000 tokens by the official
step conversion).

The best-supported decay boundary is therefore inferred as:

`0.80 * 2,560,000 = step 2,048,000 = 3,221,225,472,000 tokens`.

There is no public checkpoint exactly at step 2,048,000. The nearest public
checkpoints are step1.92M (75%, pre-decay) and step2.08M (81.25%, decay). Any
1.92M→2.08M change straddles the unobserved boundary and will be reported
separately, not assigned wholly to either phase.

## Checkpoint inclusion rule

Include the latest public checkpoint before the inferred boundary and every
official 160k-spaced checkpoint after the boundary through the final model:

`step-1920000, step-2080000, step-2240000, step-2400000, step-2560000`.

For the full trajectory and pre-decay estimate, reuse the exact valid BF16 raw
records from ARC-003 at steps 320k, 800k, and 1.28M. Reuse the exact ARC-003
records at steps 1.92M and 2.56M; do not rerun them. Newly evaluate only steps
2.08M, 2.24M, and 2.40M. All branches must resolve to the immutable commits in
`wsd_checkpoint_table.csv`; substitution is forbidden.

## Frozen assay

- Primary statistic: mean token-level top-1 agreement between intact logits
  and logits after independently bypassing one middle block, averaged over
  blocks 1–30 and the three fixed evaluation resamples.
- NLL damage: deleted-model next-token NLL minus intact-model next-token NLL.
- KL: `KL(p_intact || p_deleted)` at each next-token position.
- Data: unchanged WikiText-2 text; seeds 11/23/37; six length-256 sequences per
  seed; 4,608 token positions and 138,240 token-layer observations/checkpoint.
- Precision: native BF16 only. Any nonfinite checkpoint invalidates the window.
- Confidence control: unchanged bins `[0,.05), [.05,.1), [.1,.2), [.2,.4),
  [.4,1.01]`, with at least 100 token-layer observations at both endpoints.
- Competence: intact WikiText NLL <=5.5 plus HellaSwag normalized accuracy
  >=0.40, raw accuracy >=0.30, at least three predicted labels, and maximum
  label fraction <=0.60 on the unchanged 256-example sample.

No metric, layer, sequence, seed, bin, checkpoint, or competence threshold may
change after dense-window results are observed.

## Frozen partitions

- Total change: step320k → step2.56M.
- Pre-decay change: step320k → step1.92M.
- Boundary-straddling change: step1.92M → step2.08M.
- Confirmed-decay change: step2.08M → step2.56M.
- Boundary-bracketing window: step1.92M → step2.56M.
- Final-excluded total: step320k → step2.40M.
- Final-excluded confirmed decay: step2.08M → step2.40M.

The primary "fraction inside decay" is the conservative confirmed-decay change
divided by total change. The boundary-bracketing fraction is also reported as
an upper-inclusive estimate. Fractions are descriptive when interval signs
differ.

## Uncertainty and stability

For every partition, first average over candidate layers within each fixed
evaluation seed, compute the three paired seed deltas, then use a frozen
10,000-draw seed-level bootstrap (seed 20260825) for the mean-delta 95% CI.
Report all three seed deltas. Evaluation seeds are resamples, not independent
pretraining runs.

Fit unweighted agreement-versus-progress lines separately to four pre-decay
points (320k, 800k, 1.28M, 1.92M) and four confirmed-decay points (2.08M,
2.24M, 2.40M, 2.56M). Compute one slope per evaluation seed and bootstrap the
three slopes identically. Strict adjacent monotonicity is not required and all
sign changes remain visible.

The prior standardized-progress coefficient controlling intact NLL and partial
correlation are recomputed descriptively on all eight points. They cannot
establish causality.

## Frozen verdict hierarchy

`BLOCKED-WINDOW` if fewer than one pre-boundary plus three decay checkpoints and
the final checkpoint are valid, or if any required checkpoint fails finite or
competence checks.

`PROMOTE-BROAD` if all hold:

1. pre-decay delta <= -0.01 and is at least 25% of the absolute total decline;
2. all three pre-decay seed deltas are negative and bootstrap CI upper <0;
3. pre-decay slope is negative with bootstrap CI upper <0;
4. final-excluded total change is negative in all three seeds with CI upper <0.

`NARROW-WSD` if `PROMOTE-BROAD` fails but all hold:

1. confirmed-decay change is negative and at least 50% of total decline;
2. at least two of three adjacent confirmed-decay intervals have negative mean
   changes;
3. final-excluded confirmed-decay change is negative in all three seeds with
   CI upper <0.

`FINAL-CHECKPOINT-RISK` if both broader verdicts fail, the final 2.40M→2.56M
interval contributes at least 50% of the absolute boundary-bracketing decline,
and the confirmed-decay change before the final checkpoint is not robustly
negative (CI upper >=0 or mixed seed signs).

`MIXED` applies to every other valid heterogeneous or uncertain trajectory.

The hierarchy prevents a post-result choice among attractive narratives.

