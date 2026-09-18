# Why the result matters

Interventions are measurement procedures. Layer deletion, replacement,
attenuation, noise, and activation steering are often interpreted as if they
recover a common protocol-independent property such as redundancy, necessity,
or robustness. Prior work already warns that the protocol matters. The open
question addressed here is whether this dependence is merely a consequence of
one procedure damaging the model more than another.

Output-level functional damage is the natural control: if two interventions
have similar KL and NLL effects, a simple severity account predicts similar
top-1 response. Candidate A finds that this prediction is incomplete under its
frozen assay. The remaining family component implies that an intervention
result cannot be summarized by raw size or a single output-damage budget alone.

The implication is methodological rather than universal. For mechanistic
interpretability, it cautions against turning one intervention outcome into a
property of a component. For pruning and redundancy studies, it separates
operational substitutability from protocol-free dispensability. For robustness,
it shows why weight/activation-space and function-space controls should be
reported together. For causal-intervention work, it provides a concrete case
where increasingly strong controls narrow the explanation without identifying
the mechanism.

The result remains important only within its scope: two small Pythia scales,
two English corpora, two intervention families, and a next-token top-1 endpoint.
