# Assay validation

## Frozen-assay audit

The original ARC-002/003 evaluator was inspected before preregistration. It:

- restores the intact 12-block module list before every baseline;
- deletes one interior block by omitting it from the executed module list;
- compares intervened to intact top-1 predictions on identical tokens;
- calculates intervened-minus-intact NLL;
- calculates `KL(p_intact || p_intervened)`;
- uses intact top-1 confidence for fixed-bin controls.

No bug was found in those definitions or implementation. ARC-003 remains
frozen evidence.

## New-wrapper validation

The first pre-formal wrapper attempt was rejected because algebraically
reconstructing the bypassed block input in FP16 produced a `0.0234375` maximum
logit difference despite identical top-1 predictions. It saved no formal data.
The active wrapper directly returns the input tensor at `alpha=1` and directly
returns the block output at `alpha=0`.

Every one of the 18 formal run/checkpoint records passed:

- `alpha=0` versus intact max absolute logit difference <= `1e-4`;
- `alpha=1` versus direct module-list deletion max difference <= `1e-4`;
- identical top-1 predictions at both endpoints;
- order-reversal repeat max difference <= `1e-4`.

As an independent artifact check, all 540 formal `alpha=1` cells were compared
against the retained ARC-002/003 raw records (6 runs x 3 checkpoints x 3
evaluation selections x 10 layers). Maximum difference was exactly zero for
top-1 agreement, NLL damage, and KL.

**Conclusion:** no assay invalidation. The rejected implementation is retained
in `technical_failure_log.md` and its hash is retained in
`execution_manifest.sha256`.

