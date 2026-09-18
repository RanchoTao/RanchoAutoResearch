# Paper implications

## Currently safe claim

The previously reported cross-family residual is sensitive to a subtle but
material outcome-definition inconsistency under tied FP16 logits. A minimal
same-rule diagnostic retains its aggregate direction, so the research line is
not yet falsified, but the ARC-006 estimate and downstream heterogeneity claims
require formal repair.

## Unsupported claims

- Decision-boundary geometry explains or fails to explain the residual.
- The 18/103 sign reversals are stable.
- Layer heterogeneity is a property of intervention family rather than the
  mixed tie rule.
- ARC-006's exact -0.019235 residual is frozen high-confidence evidence.

## Reviewer risk

The first reviewer attack is assay non-equivalence: the two intervention
families were scored against different intact classes. Any paper-level result
must repair this before adding mechanistic interpretation.
