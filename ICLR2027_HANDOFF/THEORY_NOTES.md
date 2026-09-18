# Theory and interpretation notes

## Formal definitions implemented by the assay

For residual input `x` and intact block output `b(x)`, residual attenuation is

`b_alpha(x) = b(x) - alpha (b(x)-x)`.

`alpha=0` is intact; `alpha=1` returns `x` exactly and is the bypass endpoint. For fixed teacher-forced positions `T`,

`S(I,c) = |T|^{-1} sum_t 1[argmax p_c,t = argmax q_I,c,t]`,  
`D_S(I,c)=1-S(I,c)`,  
`Delta S(I)=S(I,c_late)-S(I,c_early)`.

Canonical argmax means the lowest token index among exact maximum logits. Output-level damage descriptors are forward `KL(p_intact || p_intervened)` and target-token `NLL(q)-NLL(p)`.

These are operational definitions implemented and checked in code. They are not theorems about model function.

## Strictly established calculations

- `S` is the complement of an argmax-disagreement rate on identical teacher-forced positions.
- The alpha-1 wrapper was checked against literal bypass within the frozen numerical tolerance.
- Matching is deterministic and outcome-blind with frozen calipers.
- The corrected family residual is a run-level aggregation of cellwise `D_S(noise)-D_S(block)`.
- The geometry analysis is a frozen associational adjustment of the corrected residual.

No formal proof or human-verified theorem is part of Candidate A.

## Heuristic explanations consistent with evidence

1. **Residual-stream intervention:** bypass removes the full learned block update, whereas attenuation removes a fraction and additive noise perturbs the intact output along a normalized direction. Equal local norm therefore need not produce equal downstream computation.
2. **Perturbation propagation:** later blocks and nonlinearities can transform equal-sized hidden perturbations differently depending on direction, layer, checkpoint, and intact representation geometry.
3. **Output sensitivity/Jacobian intuition:** locally, logit change may be approximated by a downstream Jacobian applied to the hidden perturbation. Norm alone omits direction and anisotropy; two directions of equal norm can yield different logit changes.
4. **KL/NLL incompleteness:** forward KL averages distributional change and NLL focuses on the target token. Neither fixes every logit ordering or the entire conditional function, so matched values can coexist with different argmax changes.
5. **Training-stage sensitivity:** changing representations and downstream Jacobians over training may change the response to the same intervention construction, even while intact NLL improves.

These are explanations, not causal findings.

## What the geometry results do and do not say

Logit norm and absolute boundary alignment differ systematically between families after KL/NLL matching, and the joint frozen geometry block shrinks the family coefficient by 20.18%. This establishes association with part of the residual. It does not prove that boundary geometry causes the residual, because predictors are correlated, the endpoint and controls share logits, reversals are not predicted adequately, and layer heterogeneity remains.

## Speculative/unresolved ideas

- Downstream Jacobian anisotropy or hidden perturbation direction could explain remaining family structure.
- Self-repair or nonlinear routing could make bypass and noise propagate differently.
- Later checkpoints could have different local curvature or residual-update organization.

ARC-008/009 failed to isolate direction causally, so none of these should appear as established mechanism claims.

## Intervention equivalence boundary

The current evidence rejects only the implication:

`matched forward KL + matched target-token NLL => equal teacher-forced top-1 damage`

for the tested block/noise pairs. It does not reject full output-distribution equality implying identical argmax, nor does it establish general functional non-equivalence. “Functional equivalence” must be defined before use.
