# META-ARC-02 literature wedges

Search window: primarily 2025–2026, with older work retained only when it is the
closest necessary neighbor. Thirty wedges span eight themes. A wedge records a
tension; it is not a novelty claim.

## Theme A — optimization dynamics

### W01 — numerical stability versus feature emergence

**Recent result:** [Grokking at the Edge of Numerical Stability (ICLR 2025)](https://openreview.net/forum?id=e1ba83228ebfeb112400fb06f593afdd0826f629)
argues that naive loss minimization and floating-point effects explain delayed
generalization in important grokking settings. **Closest neighbor:** an
[ICLR 2026 feature-emergence analysis](https://openreview.net/pdf/132c3967ef6524697ed2518ac7c4e7dc5f6d5301.pdf)
derives feature dynamics and scaling behavior. **Tension:** numerical precision
and feature acquisition offer different causal stories. **Why not answered:** the
papers do not provide a matched precision-versus-feature intervention across task
families. **Cheapest test:** modular arithmetic MLPs in fp16/fp32/fp64 with
identical trajectories and a non-grokking held-out construction.

### W02 — seed allocation in small-model scaling laws

**Recent result:** [A Hitchhiker's Guide to Scaling Law Estimation (ICML 2025)](https://proceedings.mlr.press/v267/choshen25a.html)
shows that variability across seeds can make multiple small runs more useful than
one large run. **Closest neighbor:** current scaling work often fits independent
models at each scale. **Tension:** common-random-number coupling across scales may
reduce extrapolation uncertainty without more compute. **Why not answered:** the
paper gives broad estimation guidance, not a controlled paired-seed law.
**Cheapest test:** synthetic language-model scaling fits with paired versus
independent data/init seeds and held-out largest scale.

### W03 — geometry is predictive, but is it causal?

**Recent result:** [Feature Learning beyond the Lazy-Rich Dichotomy (ICML 2025)](https://openreview.net/forum?id=gKdjHLrHDS)
connects manifold untangling to learning stages and OOD behavior. **Closest
neighbor:** [Controlling Neural Collapse Enhances OOD Detection and Transfer](https://openreview.net/forum?id=8AGdUCdDyI)
actively controls collapse. **Tension:** geometry may merely co-move with margin,
norm, or calibration. **Why not answered:** no minimal matched-function
reparameterization isolates geometry from predictions. **Cheapest test:** small
MLPs on latent-factor data with feature-space interventions preserving logits.

### W04 — task order rules versus within-task sample order

**Recent result:** [Optimal Task Order for Continual Learning (ICML 2025)](https://proceedings.mlr.press/v267/li25z.html)
derives rules based on representativeness and adjacent-task dissimilarity.
**Closest neighbor:** classical SGD assumes shuffled within-task data. **Tension:**
the same similarity principles may or may not govern example ordering inside one
stationary task. **Why not answered:** task-order results do not imply sample-order
results. **Cheapest test:** matched latent-factor classification streams with the
same multiset but similarity-clustered, alternating, and shuffled order.

### W05 — frequency-driven focus-dilution cycles

**Recent result:** [Focus and Dilution (2026)](https://arxiv.org/abs/2605.01199)
derives cycles in one-layer attention on Markov data. **Closest neighbor:**
[Information Entropy Invariance (2025)](https://arxiv.org/abs/2501.08570)
treats score dilution as a length-extrapolation problem. **Tension:** token
frequency and context length may be two views of the same softmax-denominator
variable. **Why not answered:** distinct-token diversity is not isolated from raw
length. **Cheapest test:** fixed-length retrieval with controlled distractor
diversity and multiplicity.

## Theme B — data efficiency and reuse

### W06 — repetition harms pretraining but can help SFT

**Recent result:** [Internal Data Repetition Destroys Language Models (2026)](https://arxiv.org/abs/2606.24998)
finds non-monotone repetition damage. **Closest neighbor:** [Data Repetition Beats
Data Scaling in Long-CoT SFT (2026)](https://arxiv.org/abs/2602.11149) reports the
opposite sign under a fixed update budget. **Tension:** objective, target entropy,
or schedule must change the sign. **Why not answered:** neither study causally
isolates those variables. **Cheapest test:** tiny sequence models with matched
token budgets, varying only target stochasticity or repeat schedule.

### W07 — dataset size versus distribution controls reusable epochs

**Recent result:** [Larger Datasets Can Be Repeated More (2025)](https://arxiv.org/abs/2511.13421)
predicts effective reuse saturation depending on dataset size and distribution.
**Closest neighbor:** [Improved Scaling Laws via Data Reuse](https://arxiv.org/abs/2506.08415)
links gains to covariance spectra. **Tension:** raw dataset size may be a proxy for
effective rank. **Why not answered:** a neural controlled test matching N while
varying spectrum is missing. **Cheapest test:** teacher-student regression/MLPs
with matched N and adjustable covariance effective rank.

### W08 — burstiness of duplicate exposure

**Recent result:** repetition studies control counts and fraction, and
[Scaling Laws and Interpretability of Repeated Data](https://arxiv.org/abs/2205.10487)
links duplicates to copying/generalization damage. **Closest neighbor:**
[Optimal Task Order](https://proceedings.mlr.press/v267/li25z.html) establishes
that temporal ordering can matter in continual learning. **Tension:** identical
duplicate multisets may have different effects when massed or temporally spaced.
**Why not answered:** no direct study was found that isolates duplicate spacing at
fixed tokens, counts, initialization, and optimizer steps. **Cheapest test:** tiny
LM on two exact synthetic generators, comparing massed, evenly spaced, and random
duplicate schedules over five seeds.

### W09 — contamination recency versus repetition count

**Recent result:** [How Much Can We Forget about Data Contamination? (ICML 2025)](https://proceedings.mlr.press/v267/bordt25a.html)
shows that later clean training can erase benchmark overfitting. **Closest
neighbor:** [Measuring Forgetting of Memorized Examples](https://arxiv.org/abs/2207.00099)
finds empirical forgetting and a role for nondeterminism. **Tension:** a fixed
number of contaminating exposures can be front-loaded, back-loaded, or spaced.
**Why not answered:** contamination position is studied, but the interaction of
spacing with multiple exposures is weakly mapped. **Cheapest test:** tiny LM with
fixed contamination count and clean-token suffix, measuring exact exposure
advantage and fresh-test loss.

### W10 — clean-data injection and forgetting

**Recent result:** [Scaling Laws for Forgetting during Finetuning with Pretraining
Data Injection (ICML 2025)](https://proceedings.mlr.press/v267/) studies
pretraining-data injection. **Closest neighbor:** contamination-forgetting work
shows novel clean data erases memorization. **Tension:** random replay and
similarity-matched replay may have different retention per token. **Why not
answered:** replay semantic similarity is not isolated in the scaling statement.
**Cheapest test:** two-domain synthetic language models with equal replay rate and
controlled cross-domain transition overlap.

## Theme C — algorithmic and length generalization

### W11 — parity shortcut or general quotient shortcut?

**Recent result:** [(How) Do Language Models Track State? (ICML 2025)](https://proceedings.mlr.press/v267/li25r.html)
finds associative and parity-associative state-tracking mechanisms. **Closest
neighbor:** [Grokking Group Multiplication with Cosets (ICML 2024)](https://proceedings.mlr.press/v235/stander24a.html)
shows networks use subgroup/coset structure. **Tension:** parity may be one example
of a general preference for cheap quotient-group features. **Why not answered:**
the state-tracking study uses symmetric-group parity rather than a controlled
family of groups with different quotient structures. **Cheapest test:** tiny
Transformers on matched finite-group product streams, measuring exact product,
quotient prediction, and OOD length.

### W12 — sequence length or recurrent-state coverage?

**Recent result:** [Understanding and Improving Length Generalization in Recurrent
Models (ICML 2025)](https://openreview.net/forum?id=2OEb20dy7B) improves
generalization by expanding state coverage. **Closest neighbor:** [A Formal
Framework for Transformer Length Generalization (ICLR 2025)](https://openreview.net/pdf?id=U49N5V51rU)
studies identifiability from training lengths. **Tension:** raw length and visited
latent states are correlated in standard benchmarks. **Why not answered:** the
state-coverage intervention is recurrent-model-specific. **Cheapest test:** match
length while varying reachable automaton-state coverage, then match state coverage
while varying length, for a tiny Transformer and GRU.

### W13 — positional misalignment versus score dilution

**Recent result:** [Dissecting the Role of Positional Encoding in Length
Generalization (ICLR 2026 submission)](https://openreview.net/pdf/e4271113e9b6eecc295b51d021fa84269a56fa98.pdf)
emphasizes task/PE alignment. **Closest neighbor:** [NoPE length generalization](https://arxiv.org/abs/2404.12224)
links failure to distracted attention. **Tension:** alignment and entropy predict
different outcomes when position support is extended with semantically inert
tokens. **Why not answered:** padding/data-format work is close, so the residual
novelty is narrow. **Cheapest test:** no-op padding and position-randomization with
matched computation depth.

### W14 — auxiliary-task length transfer

**Recent result:** [Extrapolation by Association (2025)](https://arxiv.org/abs/2506.09251)
shows length generalization transfers from a related long auxiliary task.
**Closest neighbor:** state-tracking work associates better mechanisms with
better extrapolation. **Tension:** transfer could come from position exposure or
algorithm reuse. **Why not answered:** an auxiliary task matching positions but
forbidding reusable computation is not the central control. **Cheapest test:**
related/unrelated auxiliary tasks crossed with matched long-position exposure.

### W15 — computational frontier versus architectural recurrence

**Recent result:** [Thinking Deeper, Not Longer (2026)](https://arxiv.org/abs/2603.21676)
reports a computational frontier in depth-recurrent Transformers. **Closest
neighbor:** fixed-depth Transformer work links depth to compositional
generalization. **Tension:** the frontier may reflect recurrent-step optimization
rather than task complexity. **Why not answered:** tied-parameter recurrence and
untied depth are not fully factorially matched. **Cheapest test:** equal-parameter
tiny models crossing tied/untied blocks and train/test recurrence counts.

## Theme D — representation geometry and small-model learning

### W16 — neural-collapse detection/generalization tradeoff

**Recent result:** [Controlling Neural Collapse Enhances OOD Detection and
Transfer (ICML 2025)](https://openreview.net/forum?id=8AGdUCdDyI) reports that
stronger collapse helps OOD detection but hurts generalization. **Closest
neighbor:** [Neural Collapse Beyond the Unconstrained Features Model](https://openreview.net/forum?id=ZrhGq664om)
ties NC1 to data-specific dynamics. **Tension:** the tradeoff may be mediated by
feature norm or calibration. **Why not answered:** the recent control paper is a
high collision risk; only a logit-preserving causal control remains. **Cheapest
test:** post-hoc invertible feature transformations plus retrained last layer.

### W17 — long-tail collapse and tail OOD

**Recent result:** [Geometry of Long-Tailed Representation Learning (ICLR 2025)](https://openreview.net/forum?id=GySIAKEwtZ)
derives conditions for tail-class centers to collapse. **Closest neighbor:** NC
work reports a detection/generalization tradeoff. **Tension:** tail-center collapse
may predict which classes fail under covariate rather than label shift. **Why not
answered:** the long-tail paper focuses on skew geometry, not held-out causal
shifts per class. **Cheapest test:** synthetic Gaussian mixtures with class
imbalance and orthogonal covariate shifts.

### W18 — scale-dependent loss of predictive geometry

**Recent result:** [Scale Determines Whether Language Models Organize
Representation Geometry for Prediction (2026)](https://arxiv.org/abs/2605.17084)
reports that small models lose predictive geometry in late layers while loss
improves. **Closest neighbor:** manifold-geometry work associates untangling with
feature learning. **Tension:** late-layer loss may be caused by tied unembedding or
width bottlenecks rather than scale itself. **Why not answered:** architecture and
scale are not causally separated. **Cheapest test:** small teacher-student LMs
crossing width with tied/untied output embeddings.

### W19 — compression helps generalization but hurts flexibility

**Recent result:** [Representational Compression and Flexibility (2025 workshop)](https://openreview.net/forum?id=oayAy75SRM)
reports longer pretraining reduces flexibility and reconstruction preserves it.
**Closest neighbor:** neural-collapse work reports a similar generalization
tradeoff. **Tension:** intrinsic dimension, elapsed optimization, and confidence
co-vary. **Why not answered:** a matched-function compression intervention is
missing. **Cheapest test:** latent-rule switching with bottleneck rank controlled
at fixed accuracy.

### W20 — language identity versus fact association in unification

**Recent result:** [Beyond the Rosetta Stone (ICLR 2026 submission)](https://openreview.net/forum?id=EGf7dks3tw)
shows synthetic multilingual fact unification depends on language association and
identifiability. **Closest neighbor:** weak-to-strong work highlights feature-space
alignment. **Tension:** token overlap and distributional co-occurrence may make
independent predictions. **Why not answered:** tokenizer overlap is manipulated,
but a held-out orthography with fixed mutual information offers a sharper causal
test. **Cheapest test:** tiny synthetic bilingual LM with independently varied
token overlap and fact-language mutual information.

## Theme E — distillation and test-time adaptation

### W21 — asymmetric negative transfer in distillation

**Recent result:** [Rethinking Knowledge Distillation (ICLR 2026 submission)](https://openreview.net/forum?id=ja0tZJS3hM)
reports a negative asymmetric payoff from teacher knowledge. **Closest neighbor:**
[On student-teacher deviations in distillation](https://openreview.net/forum?id=uV3Z2IG6oj)
links deviations to implicit bias. **Tension:** error inheritance may depend on
whether teacher errors align with high-variance student features. **Why not
answered:** the functional study does not give a clean feature-alignment boundary.
**Cheapest test:** controlled teacher/student subspaces with equal teacher error.

### W22 — weak-to-strong gains and subspace discrepancy

**Recent result:** [Discrepancies are Virtue (ICML 2025)](https://proceedings.mlr.press/v267/dong25g.html)
characterizes weak-to-strong variance reduction through intrinsic subspaces.
**Closest neighbor:** student-teacher deviation work studies eigendirection bias.
**Tension:** finite-depth nonlinear students may violate the linear prediction.
**Why not answered:** real-task validations exist, but the exact question is
already substantially owned. **Cheapest test:** nonlinear teacher/student MLPs on
rotated latent subspaces.

### W23 — test-time training alignment boundary

**Recent result:** [Test-Time Training Provably Improves Transformers as
In-context Learners (ICML 2025)](https://proceedings.mlr.press/v267/gozeten25a.html)
quantifies the role of pretrain-target alignment. **Closest neighbor:**
[The Surprising Effectiveness of TTT for Few-Shot Learning](https://proceedings.mlr.press/v267/akyurek25a.html)
shows large empirical gains. **Tension:** demonstration diversity and alignment
co-vary. **Why not answered:** a nonlinear controlled phase diagram over both is
missing. **Cheapest test:** tiny in-context regression Transformer with crossed
task-subspace angle and demonstration diversity.

### W24 — entropy-minimization collapse and stream composition

**Recent result:** [Ranked Entropy Minimization (ICML 2025)](https://openreview.net/forum?id=lHaGLJ65J9)
documents single-class collapse. **Closest neighbor:** [GOTTA be diverse](https://openreview.net/forum?id=6EwuwivLSp)
studies diversity-aware memory under changing label distributions. **Tension:**
collapse may be controlled by effective class diversity per adaptation window,
not covariate-shift severity. **Why not answered:** this boundary is now directly
occupied by memory/diversity studies. **Cheapest test:** CIFAR features with
synthetic stream priors and fixed corruptions.

### W25 — selective adaptation under partial modality shift

**Recent result:** [Test-Time Selective Adaptation for Uni-Modal Shift (ICML
2025)](https://proceedings.mlr.press/v267/chen25ch.html) shows negative transfer
when adapting unshifted modalities. **Closest neighbor:** backprop-free alignment
methods adapt aggregate features. **Tension:** shift localization may be possible
from disagreement without adapters. **Why not answered:** method space is crowded,
but a calibrated detection boundary could remain. **Cheapest test:** two-view
Gaussian/CIFAR features with exactly one shifted view.

## Theme F — evaluation methodology and RL with verifiable rewards

### W26 — contamination resistance versus semantic fidelity

**Recent result:** [The Emperor's New Clothes in Benchmarking? (ICML 2025)](https://openreview.net/forum?id=TuvDxubEfE)
finds no tested mitigation balances question-level fidelity and contamination
resistance across benchmarks. **Closest neighbor:** [How Much Can We Forget](https://proceedings.mlr.press/v267/bordt25a.html)
shows contamination can naturally decay. **Tension:** mitigation quality may
depend on when contamination occurred, not only rewrite type. **Why not answered:**
model training provenance is unavailable for most evaluated LLMs. **Cheapest
test:** intentionally contaminated tiny LM with exact rewrite transformations.

### W27 — verifier format false negatives

**Recent result:** [From Accuracy to Robustness: Rule- and Model-based Verifiers](https://openreview.net/forum?id=ZBhZT307xx)
finds rule verifiers reject equivalent answer formats. **Closest neighbor:**
[Multilingual Verifier Bias in RLVR](https://arxiv.org/abs/2608.20362) localizes
language-conditioned false negatives to the answer interface. **Tension:** static
verifier error and training harm need not align. **Why not answered:** controlled
training audits now cover much of this gap. **Cheapest test:** tiny policy over
equivalent answer strings with exact semantic labels.

### W28 — conflicting claims about RLVR reward noise

**Recent result:** [An Imperfect Verifier Is Good Enough (2026)](https://arxiv.org/abs/2604.07666)
reports robustness to moderate noise. **Closest neighbor:** [Quantifying Empirical
Compute-Supervision Tradeoffs](https://arxiv.org/abs/2605.25252) reports persistent
gaps and stronger false-negative harm. **Tension:** persistent versus resampled
noise and asymmetric versus symmetric errors differ. **Why not answered:** the
newer work explicitly crosses false-positive/false-negative noise, making simple
asymmetry studies a collision. **Cheapest test:** bandit/0.5B GRPO only if a new
noise-correlation boundary is identified.

### W29 — adaptation risk monitoring versus risk prevention

**Recent result:** [Monitoring Risks in Test-Time Adaptation (NeurIPS 2025)](https://openreview.net/forum?id=TzHX2RWUdE)
adds statistical alarms to TTA. **Closest neighbor:** entropy-ranking methods try
to prevent collapse. **Tension:** an alarm can detect failure without identifying
the causal stream statistic. **Why not answered:** whether class-diversity drift
predicts failure earlier than loss-risk monitoring is not central. **Cheapest
test:** controlled nonstationary streams with pre-registered lead-time metrics.

### W30 — clustered evaluation uncertainty

**Recent result:** [Handling Missing Responses under Cluster Dependence
(NeurIPS 2025)](https://openreview.net/forum?id=PdKhoj6goO) shows GenAI evaluation
requires cluster-aware inference. **Closest neighbor:** scaling-law guidance
emphasizes seed variance. **Tension:** benchmark-item clustering and model-seed
clustering interact in small comparisons. **Why not answered:** a design-effect
map for common multi-seed benchmark protocols is absent. **Cheapest test:**
semi-synthetic resampling from public per-item model outputs; no GPU required.

