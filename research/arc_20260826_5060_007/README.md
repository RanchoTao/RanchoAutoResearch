# ARC-20260826-5060-007

## Final status: PRIOR ASSAY INVALIDATION

ARC-007 stopped at its preregistered data-quality gate before any
geometry-conditioned model was fitted. ARC-006 mixed two definitions of the
intact top-1 class: the inherited block-family outcome used `topk`, whereas the
new noise-family outcome used `argmax`. Exact FP16 logit ties make those rules
select different classes, so the family residual did not compare like with
like.

The smallest diagnostic repair preserves the qualitative negative residual
under either consistent rule, but it does not rehabilitate the frozen ARC-006
estimate or its high-confidence assay claim. A formal ARC-006R repair and
reseal is required before ARC-007 can resume.

Start with `prior_assay_invalidation.md`. The raw ARC-007 geometry is retained
for provenance, but no geometry inference is scientifically valid against the
invalid baseline.
