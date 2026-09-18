# Adversarial reviewer test

Only T4–T5 papers receive the full “this is basically X” test.

## No Free Swap — T5

### Reviewer attack

“This is basically Garcia (2026): Pythia layer-equivalence gaps already grow
over training and depend on intervention protocol.”

### Required response

Accept the collision. Candidate A must not claim the broad phenomenon. Its
additional evidence is nine independent 160M pretraining runs, a held-out run,
70M and two-corpus sign replication, and prospective block/noise matching by raw
and functional damage. Garcia analyzes released checkpoint trajectories and a
replacement–interchange gap, not those controls.

### Assessment

Fatal to the original phenomenon-first framing; not fatal to the narrower
replication-and-qualification thesis.

## The Remarkable Robustness of LLMs — T4

### Reviewer attack

“Your layer bypass and top-1 agreement metric are Lad et al.'s experiment with
more seeds.”

### Required response

The intervention and metric are prior art and must be credited as such. The
remaining question is whether their static observation has a repeatable
training-associated endpoint and whether matched interventions are equivalent.
Candidate A supplies evidence for those narrower questions.

### Assessment

Fatal to method/metric novelty; survivable only if independent-run dynamics and
matched controls are central.

## SteerCheck — T4

### Reviewer attack

“Matched KL and intervention-family residuals are already the point of
SteerCheck.”

### Required response

SteerCheck audits attribution specificity of activation steering in Qwen3-14B
with matched off-target KL and null directions. Candidate A measures
block-bypass substitutability over pretraining and compares block bypass with
activation noise. The estimand, intervention pair, and temporal claim differ;
the general matched-control methodology is not claimed as new.

### Assessment

Substantial positioning threat. It prevents a general “functional matching
reveals protocol dependence” first claim.

## Divergent Token Metrics — T4

### Reviewer attack

“`S` is simply one minus DTM.”

### Required response

Correct under identical evaluation positions and aggregation. Candidate A does
not claim metric novelty. It uses the known statistic in a preregistered
training and intervention-comparison design.

### Assessment

Fatal to metric novelty, not to the empirical controls.

## Training Dynamics Impact PTQ Robustness — T4

### Reviewer attack

“Training-dependent perturbation fragility is already established at greater
checkpoint density and scale.”

### Required response

The prior result concerns post-training quantization and learning-rate phases.
Candidate A's bounded addition concerns interior-block bypass, independent
pretraining runs, token agreement, and a prospectively damage-matched second
intervention. It should not claim generic training-dependent fragility.

### Assessment

Eliminates a broad training-robustness thesis; leaves the assay-specific result.

## When Probing Accuracy Saturates, Fragility Resolves — T4

### Reviewer attack

“Activation-noise fragility already tracks language-model pretraining.”

### Required response

Yes, on an OLMo probe trajectory. Candidate A's activation-noise arm is a
control for a block-bypass endpoint, not a first activation-fragility metric.
Its distinct evidence is independent-pretraining-run block-bypass replication
and prospective cross-family matching.

### Assessment

Weakens the second-intervention novelty; not a direct collision with the
combined design.

## Not the Dimension, the Norm — T4

### Reviewer attack

“Your claim that raw magnitude is insufficient conflicts with evidence that
norm is the only relevant factor.”

### Required response

The claims concern different regimes. Kim et al. study gradient-free
weight-perturbation adaptation across directions and tasks; Candidate A's
conclusion is restricted to residual attenuation and the frozen `Delta S`
assay. The paper must present this as boundary evidence, not a universal
refutation.

### Assessment

Not a direct collision, but a serious external-validity attack that requires
assay-bounded wording.

## Reviewer-2 bottom line

The response to “this is basically No Free Swap plus Lad et al.” is only
convincing after discarding phenomenon and metric novelty. The surviving paper
is a controlled replication and qualification of intervention-conditioned
training fragility. Whether that scope clears ICLR significance remains the
largest non-novelty risk.
