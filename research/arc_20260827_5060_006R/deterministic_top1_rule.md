# Deterministic top-1 rule

## Canonical definition

For each intact logit vector `z`:

1. compute `m = max(z)` in the stored/computed numeric representation;
2. enumerate indices `i` for which `z[i] == m` exactly;
3. select `min(i)`.

No tolerance is introduced. The rule is family-independent, deterministic,
and outcome-independent. On a contiguous vocabulary axis, PyTorch
`argmax(dim=-1)` returns the first maximum and therefore implements this rule.

## Precision boundary

The frozen Pythia models executed in FP16. ARC-007 converted the output logits
to FP32 before top-1 selection. This conversion preserves, but cannot undo,
ties already created by reduced-precision model computation. The saved NPZ
flags are `uint8`; continuous derived logit quantities are `float32`. Full
logit tensors were not retained.

ARC-006R does not regenerate the model at higher precision because that would
change the frozen assay rather than repair its identity rule. The globally
consistent historical `topk` extraction is reported only as a numeric
sensitivity analysis.

## Implementation guard

The repair script verifies the lowest-index convention on explicit FP16 and
FP32 tied vectors before reading outcomes. Both families are loaded through the
same canonical column construction; there is no family-specific top-1 branch.
