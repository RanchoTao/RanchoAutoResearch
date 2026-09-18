# Known-explanation audit

## Explanations examined

### Parameter symmetries and function-space distance

Weight-space distance is not generally a function-space distance: permutations,
rescalings, and deep compositional effects can make equal Euclidean changes
functionally unequal. Bernstein et al. provide theory for layerwise relative
perturbations, while Dhawan et al. explicitly treat output discrepancy as a
function-space object. These works make a broad “raw norm is insufficient”
claim expected, but they do not derive Candidate A's sign, checkpoint trend, or
residual between the two frozen intervention families.

### Fisher, Hessian, sharpness, and loss-landscape geometry

Local curvature can predict loss sensitivity for sufficiently small parameter
perturbations. Candidate A includes a discrete block bypass and activation
noise, however, and does not estimate a local quadratic model. Curvature is a
plausible explanation class, not an already established explanation of the
observed `Delta S`.

### Residual architecture and layer redundancy

Residual connections make layer deletion technically possible, and static
final-model redundancy is well established by Lad et al., ShortGPT, and related
pruning work. This explains why `S` can be high, not why it declines across
independently pretrained runs or why functionally matched intervention families
retain a residual.

### Softmax margins and top-1 discontinuity

Top-1 agreement can change after a small logit perturbation near a decision
boundary. This is the strongest trivial-metric threat. ARC-007R found that the
frozen output-geometry block explains only a minority of the corrected family
residual, but that negative control does not exclude richer margin geometry.
Accordingly, no semantic or capability-loss interpretation is justified.

### Normalization and activation scale

LayerNorm, activation scale, and checkpoint-specific representation scale can
change perturbation effects. Reblitz-Richardson's checkpoint fragility work and
Rushing and Nanda's self-repair analysis make these serious alternatives. The
current assay's confidence matching and norm controls reduce, but do not fully
identify, these mechanisms.

### Protocol dependence

Garcia and SteerCheck independently show that intervention conclusions depend
on protocol or control family. This is not a trivial theorem, but it means the
Candidate A family residual should be positioned as a bounded instance of an
emerging empirical principle rather than a first discovery of protocol
dependence.

## Conclusion

No inspected theorem mechanically implies the full conjunction of Candidate A
results. Nevertheless, two components are already expected from prior work:
raw parameter distance need not determine functional change, and intervention
protocols need not be interchangeable. The nontrivial remainder is the exact
independent-run, cross-corpus block-bypass replication and its prospectively
matched comparison with activation noise.

Primary sources: [Bernstein et al.](https://proceedings.neurips.cc/paper/2020/hash/f4b31bee138ff5f7b84ce1575a738f95-Abstract.html),
[Dhawan et al.](https://proceedings.mlr.press/v202/dhawan23a.html),
[Rushing and Nanda](https://proceedings.mlr.press/v235/rushing24a.html),
[Garcia](https://arxiv.org/abs/2605.16234), and
[SteerCheck](https://arxiv.org/abs/2608.24335).
