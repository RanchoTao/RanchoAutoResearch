# Abstract skeleton

**Problem.** Internal interventions are commonly used to infer layer redundancy
or robustness, but it is unclear whether their effects are stable across
pretraining runs and intervention protocols.

**Gap.** Prior work establishes static block substitutability and reports
training-dependent gaps between layer-intervention protocols, but does not test
the same endpoint across independent pretraining runs and corpora while
prospectively matching raw and functional perturbation budgets.

**Finding.** In the frozen Candidate A assay, intact/intervened next-token top-1
agreement after interior-block bypass is lower at late than competent early
checkpoints across the reported Pythia runs. A second, norm-controlled
activation-noise intervention preserves the qualitative direction, yet the two
families remain different after prospective KL/NLL matching.

**Evidence.** The sign repeats at 70M and 160M and on WikiText-2 and a
HellaSwag-derived stream; held-out-run, confidence, layer-location, and
functional-damage controls are reported with uncertainty. A frozen simple
output-geometry analysis explains only part of the corrected family residual.

**Implication.** Training-time intervention effects should be interpreted as
protocol-conditioned measurements rather than direct, protocol-free properties
of a layer.

**Limitation.** Evidence is restricted to small Pythia models, two corpora, two
intervention families, and a next-token agreement endpoint. It does not identify
a causal mechanism or establish downstream capability loss.
