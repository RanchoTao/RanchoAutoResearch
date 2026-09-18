# Strongest counterevidence

The preregistered primary result is unusually consistent, so the negative
evidence is about effect heterogeneity and remaining design limitations rather
than sign reversals.

## Weakest run-level decline

- Combined seed3 has the smallest endpoint decline:
  `Delta S = -0.089106` (`0.649978 -> 0.560872`).
- Its three fixed evaluation-shard changes are all negative; the diagnostic
  shard-bootstrap interval is `[-0.091992, -0.085026]`.
- This remains above the frozen magnitude requirement in absolute value, but
  shows that a universal numeric effect size should not be claimed.

## Strongest reversal

None. All 9/9 independent 160M runs, 27/27 run-resample endpoint contrasts,
45/45 eligible fixed-confidence run-bin contrasts, and 90/90 run-layer
endpoint contrasts are negative.

## Weakest layer

- The least negative individual run-layer contrast is seed7, layer1:
  `Delta S = -0.026042` (`0.529948 -> 0.503906`).
- Across runs, layer1 also has the weakest layer-median decline:
  `median Delta S = -0.065321`.
- This is a real location effect: the magnitude varies strongly by layer even
  though the direction is broad. Layer10 has the largest median decline
  (`-0.183811`). The ARC therefore supports a broad middle-layer aggregate,
  not equal specialization of every layer.

## Weakest confidence region

- The weakest eligible run-bin contrast is seed1 in the highest intact
  confidence bin `[0.4, 1.01]`: `Delta S = -0.077873`.
- The same bin is also weakest after pooling runs: mean `Delta S = -0.097044`.
- Confidence matching does not remove the result, but fixed bins do not prove
  exact distributional matching within a bin.

## Functional metric that disagrees most

- No measured functional metric reverses. NLL damage and KL increase in 9/9
  runs.
- KL is the relatively weakest supporting endpoint metric: seed1 has the
  smallest late-minus-early KL change, `+0.285242`.
- Margin damage and token-difficulty strata were not evaluated. They were
  optional, and the frozen prior assay did not store the required deleted-logit
  or per-token label values. Their absence is a limitation, not a null result.

## Design limitations

1. The nine PolyPythias combined seeds vary initialization and data order
   together, so this ARC does not identify which source drives run variance.
2. The corpus is one fixed WikiText-2 text source with three deterministic
   shards. Training-run replication is strong; corpus generalization is not
   established here.
3. All primary trajectories are strictly decreasing at the five coarse public
   checkpoints, but this does not establish continuous monotonicity between
   checkpoints.
4. The intervention is a block bypass. It measures functional
   substitutability under that intervention, not a mechanism, causal source of
   training change, or general fragility.
5. Per-run forest intervals resample only three evaluation shards and are
   explicitly diagnostic. The scientific aggregate interval resamples runs.

