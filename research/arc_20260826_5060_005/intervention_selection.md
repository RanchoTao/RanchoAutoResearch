# Intervention-family selection

Frozen before ARC-005 calibration outcomes.

## Architecture and prior-family audit

Pythia-160M is a 12-block pre-layer-normalized GPT-NeoX model with parallel
attention/MLP residual updates. The frozen family bypasses one complete interior
block. ARC-004's continuous alpha family scales that same complete residual
update and therefore remains part of the block-bypass family.

## Shortlist

| Candidate | Distinct from block bypass? | Strength semantics | Main risk | Decision |
| --- | --- | --- | --- | --- |
| Norm-controlled additive activation noise | Yes: computes the full block and adds an independent direction afterward | Relative local displacement `beta` | Stochastic direction and output-metric geometry | **Selected** |
| Attention-only or MLP-only bypass | Partly; still removes a block subcomputation | Fraction of one sub-update removed | Too close to deletion for the primary independence test | Reserve only for later work |
| Channel masking | Yes | Fraction/channels masked | Mask identity and sparsity pattern become major confounds | Reject for this ARC |
| Multiplicative parameter scaling | Yes | Weight scale | LayerNorm/bias interactions; repeated mutation/restoration risks state leakage | Reject for this ARC |
| Low-rank parameter perturbation | Yes | Low-rank norm | Rank/direction selection adds avoidable modeling choices | Reject for this ARC |

## Selected family

For target block output `h`, draw a deterministic Gaussian direction `u` for
each token, normalize it in hidden space, and apply

`h_beta = h + beta * ||h||_2 * u / ||u||_2`.

The intervention:

- executes every original attention and MLP computation;
- changes no parameter and deletes no computation;
- has an exact zero endpoint (`beta=0` returns the original tensor);
- has an interpretable local relative magnitude approximately equal to beta;
- permits the same measured relative/absolute activation-magnitude definitions
  used by ARC-004;
- can be calibrated over KL/NLL without inspecting the primary `Delta S`
  direction.

Noise directions are deterministic and shared across runs/checkpoints for the
same evaluation selection, layer, batch, and direction ID. Strengths reuse the
same direction, so dose monotonicity is not confounded by new noise draws.
Three direction IDs are averaged in confirmation; they are repeated
measurement controls, not independent scientific runs.

## Why this is the strongest feasible choice

This family attacks the current fatal risk directly: it perturbs the residual
stream without suppressing the target block's learned computation. It retains
the frozen output assay and magnitude definition, is exactly reversible, and
is cheap enough to evaluate across five genuine pretraining runs locally.

