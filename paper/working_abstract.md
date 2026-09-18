# Working abstract

Interventions on neural-network components are often interpreted as measuring
properties such as redundancy or robustness, yet recent work shows that the
conclusion can depend on the intervention protocol. We test whether such
protocol dependence can be reduced to differences in output-level functional
damage. Our assay measures the fraction of intact next-token top-1 predictions
preserved after an interior-block intervention across independently pretrained
small Pythia models. The early-to-late block-bypass response replicates across
nine 160M runs, a held-out run, a 70M scale, and WikiText-2 and HellaSwag-derived
evaluation streams. Within residual attenuation, matched comparisons show that
KL/NLL predictive damage discriminates top-1 damage more strongly than raw
activation displacement. However, prospective joint KL/NLL matching does not
make block bypass and norm-controlled activation noise interchangeable: a
corrected family residual of -0.0168 remains across five runs. A frozen block of
simple output-logit and decision-boundary features accounts for only 20.2% of
that residual. These results support a bounded methodological conclusion: in
the tested setting, intervention responses are conditioned on how a model is
perturbed and cannot be summarized by raw magnitude or matched predictive
damage alone. We do not identify a causal mechanism, establish downstream
capability loss, or claim generality beyond the tested small-model regime.

Approximate length: 185 words.
