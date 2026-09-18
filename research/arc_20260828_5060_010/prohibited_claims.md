# Prohibited claims for manuscript drafting

Do not write or imply any of the following:

| Prohibited statement | Why unsupported | Safe replacement |
|---|---|---|
| “KL/NLL causes ΔS.” | KL, NLL damage, and top-1 damage are read from related predictive outputs; interventions were not randomized over KL/NLL. | Predictive damage discriminates ΔS better than raw magnitude within one family. |
| “We identified the causal mechanism.” | Geometry is partial and internal-direction causality was not identified. | Several simple explanations were weakened; the internal determinant remains unresolved. |
| “The relationship is intervention invariant.” | ARC-006R finds a stable family residual after KL/NLL matching. | The sign generalizes qualitatively across two interventions, but the quantitative mapping is family-dependent. |
| “The phenomenon is universal across LLMs.” | Core evidence is Pythia 70M/160M; one SmolLM2 trajectory is exploratory. | The phenomenon replicates across two small Pythia scales. |
| “Internal perturbation direction causes the effect.” | ARC-009 failed its preregistered support gate and never revealed D_S. | Direction causality is non-identifiable under the current assay. |
| “Internal direction has no effect.” | A failed identification design is not a null-effect estimate. | No causal estimate was obtained. |
| “The result scales to large language models.” | No model above 360M appears, and 360M evidence is a single exploratory trajectory. | Large-model scaling is unknown. |
| “ΔS measures downstream capability, modularity, or safe pruning.” | No downstream task, pruning deployment, or semantic utility endpoint was tested. | ΔS measures next-token top-1 substitutability under the specified intervention. |
| “Training produces a smooth monotonic law or phase transition.” | Cross-scale intermediate trajectories do not support a universal checkpoint-by-checkpoint shape. | A robust early-to-late endpoint decline is supported. |
| “Layer location is irrelevant.” | The sign is broad but the magnitude is strongly layer-dependent. | Every tested interior location shares the endpoint direction. |
| “Output geometry explains the family effect.” | The full geometry block removes only 20.18%; matching does not eliminate the residual. | Measured output geometry correlates with a minority of the residual. |
| “ARC-006 found a -0.01923 residual.” | That mixed-rule result was invalidated by inconsistent tie-breaking. | Cite only ARC-006R's corrected -0.016833 estimate. |
