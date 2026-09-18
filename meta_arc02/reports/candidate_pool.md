# META-ARC-02 candidate pool

Fifteen one-sentence candidates were formed from the 30 wedges. No method names
or project branding are assigned.

## C01

**Research question:** At fixed duplicate count, token budget, and optimizer
steps, does the temporal burstiness of repeated examples control their damage to
fresh-distribution generalization?  
**H0:** Final generalization is invariant to duplicate spacing after averaging
seeds. **H1:** Massed duplicates cause more damage than evenly spaced duplicates.
**Why important:** Repetition scaling laws currently treat counts/fractions as the
main variables, yet real corpora have highly nonuniform duplicate spacing.
**Closest papers:** [Chudnovsky et al. 2026](https://arxiv.org/abs/2606.24998),
[Hernandez et al. 2022](https://arxiv.org/abs/2205.10487),
[Li & Hiratani 2025](https://proceedings.mlr.press/v267/li25z.html),
[Bordt et al. 2025](https://proceedings.mlr.press/v267/bordt25a.html).
**Exact novelty delta:** isolate spacing/burstiness while holding the complete
training multiset and compute fixed. **Cheapest experiment:** 1–3M parameter
sequence model, massed/even/random schedules, two generators, five seeds.
**Expected runtime:** 0.5 h. **Main confound:** learning-rate/time position rather
than spacing. **Immediate KILL:** massed-versus-even difference is <0.2 validation
loss SD or changes sign across generators. **Broader claim if positive:** duplicate
schedule, not merely duplicate count, is a missing variable in data-reuse laws.

## C02

**Research question:** Are parity-associative shortcuts in Transformer state
tracking one instance of a broader preference for low-complexity quotient-group
features? **H0:** quotient structure does not predict mechanism or OOD length
accuracy after group size/difficulty controls. **H1:** cheaply decodable quotient
features predict a characteristic exact-state generalization deficit.
**Why important:** it would turn a one-task mechanism into a falsifiable algebraic
law. **Closest papers:** [Li et al. 2025](https://proceedings.mlr.press/v267/li25r.html),
[Stander et al. 2024](https://proceedings.mlr.press/v235/stander24a.html),
[Huang et al. 2025](https://openreview.net/forum?id=yTAR011mOF),
[Schöne et al. 2025](https://openreview.net/forum?id=5EbiopWH6e).
**Exact novelty delta:** compare multiple finite groups/quotients rather than only
symmetric-group parity. **Cheapest experiment:** tiny product-sequence
Transformers over matched-order group families, quotient probes, held-out length.
**Expected runtime:** 2 h. **Main confound:** group complexity/commutativity.
**Immediate KILL:** quotient decodability fails to predict OOD after within-order
comparisons. **Broader claim if positive:** algebraic quotient structure predicts
which heuristic a sequence model learns.

## C03

**Research question:** Does irreducible target stochasticity determine whether
data repetition helps or harms at fixed update budget? **H0:** repeat optimum is
independent of target stochasticity. **H1:** increasing stochasticity shifts the
repeat optimum downward. **Why important:** it might reconcile harmful pretraining
repetition with helpful long-CoT SFT repetition. **Closest papers:**
[Chudnovsky et al. 2026](https://arxiv.org/abs/2606.24998),
[Kopiczko et al. 2026](https://arxiv.org/abs/2602.11149),
[Li et al. 2026](https://arxiv.org/abs/2608.14071),
[Yan et al. 2025](https://arxiv.org/abs/2511.13421).
**Exact novelty delta:** causally vary aleatoric target entropy rather than use
domain validation loss as a correlate. **Cheapest experiment:** synthetic
next-token generators at matched Bayes difficulty. **Expected runtime:** 0.75 h.
**Main confound:** ordinary noisy-label memorization. **Immediate KILL:** the
effect is fully predicted by classical label-noise baselines. **Broader claim if
positive:** conditional entropy is a control variable for repetition scaling.

## C04

**Research question:** Is visited latent-state coverage, rather than sequence
length itself, the causal variable controlling algorithmic length generalization
in Transformers and recurrent models? **H0:** coverage-matched length changes
still dominate. **H1:** performance follows state coverage when length and
coverage are factorially separated. **Why important:** it provides a structural
training-data quantity instead of another positional trick. **Closest papers:**
[Jelassi et al. 2025](https://openreview.net/forum?id=2OEb20dy7B),
[Huang et al. 2025](https://openreview.net/pdf?id=U49N5V51rU),
[Li et al. 2025](https://proceedings.mlr.press/v267/li25r.html),
[Izzo et al. 2026](https://proceedings.iclr.cc/paper_files/paper/2026/hash/4a765a1bbf8332154e58bf452fbf806c-Abstract-Conference.html).
**Exact novelty delta:** a 2×2 causal separation of token length and reachable
automaton-state coverage across architectures. **Cheapest experiment:** finite
automata with no-op loops and controlled start-state mixtures. **Expected runtime:**
1 h. **Main confound:** no-ops alter token statistics. **Immediate KILL:** result
depends on only one automaton construction. **Broader claim if positive:** state
coverage is a model-agnostic predictor of algorithmic extrapolation.

## C05

**Research question:** With a fixed number of contaminated exposures, does
spacing them through training preserve benchmark inflation longer than massing
them at one time? **H0:** only final exposure recency matters. **H1:** distributed
re-exposure slows forgetting beyond the last-exposure statistic. **Why important:**
contamination audits rarely know the full exposure schedule. **Closest papers:**
[Bordt et al. 2025](https://proceedings.mlr.press/v267/bordt25a.html),
[Jagielski et al. 2022](https://arxiv.org/abs/2207.00099),
[Sun et al. 2025](https://openreview.net/forum?id=TuvDxubEfE).
**Exact novelty delta:** spacing-last-exposure factorial control. **Cheapest
experiment:** intentionally contaminate a tiny LM and continue on clean data.
**Expected runtime:** 1.5 h. **Main confound:** small models may never exhibit
stable benchmark exploitation. **Immediate KILL:** contamination advantage is too
small before the scheduling comparison. **Broader claim if positive:** exposure
schedules are necessary metadata for contamination risk.

## C06

**Research question:** Do common-random-number pairs across model scales reduce
scaling-law extrapolation error more per run than independent seeds? **H0:** paired
seeds do not improve held-out-scale prediction intervals. **H1:** pairing data and
initialization randomness reduces slope uncertainty and held-out error.
**Why important:** low-compute scaling studies allocate large budgets to noisy
independent runs. **Closest papers:** [Choshen et al. 2025](https://proceedings.mlr.press/v267/choshen25a.html),
[Chudnovsky et al. 2026](https://arxiv.org/abs/2606.24998),
[Yan et al. 2025](https://arxiv.org/abs/2511.13421).
**Exact novelty delta:** treat cross-scale seed coupling as an experimental-design
variable. **Cheapest experiment:** fit synthetic-LM scaling curves under paired
versus independent seed allocations and predict a held-out size. **Expected
runtime:** 0.5 h. **Main confound:** architectures do not admit identical
initializations across widths. **Immediate KILL:** bootstrap coverage/error is no
better across two generators. **Broader claim if positive:** scaling experiments
can gain precision through design rather than more compute.

## C07

**Research question:** In test-time training, is target/pretraining alignment or
demonstration diversity the dominant control variable for adaptation benefit?
**H0:** only subspace alignment predicts gain. **H1:** diversity has an independent
interaction and can reverse the sign of TTT. **Why important:** current theory and
large-model results conflate the two. **Closest papers:** [Gozeten et al. 2025](https://proceedings.mlr.press/v267/gozeten25a.html),
[Akyürek et al. 2025](https://proceedings.mlr.press/v267/akyurek25a.html),
[Chen et al. 2025](https://proceedings.mlr.press/v267/chen25ch.html).
**Exact novelty delta:** nonlinear 2D phase diagram over alignment and demo
diversity. **Cheapest experiment:** tiny in-context regression Transformer with a
single test-time gradient step. **Expected runtime:** 1.5 h. **Main confound:**
diversity changes gradient magnitude. **Immediate KILL:** normalized-gradient
control removes the interaction. **Broader claim if positive:** TTT has a
measurable data-geometry failure boundary.

## C08

**Research question:** At equal teacher error, does feature-subspace alignment
control which wrong teacher knowledge a distilled student inherits? **H0:** error
inheritance depends only on teacher error/confidence. **H1:** aligned errors are
inherited more strongly. **Why important:** it would explain negative asymmetric
KD payoff. **Closest papers:** [Mason-Williams et al. 2026](https://openreview.net/forum?id=ja0tZJS3hM),
[Nagarajan et al. 2023](https://openreview.net/forum?id=uV3Z2IG6oj),
[Dong et al. 2025](https://proceedings.mlr.press/v267/dong25g.html).
**Exact novelty delta:** rotate error directions at fixed teacher performance.
**Cheapest experiment:** teacher/student MLPs on controlled subspaces. **Expected
runtime:** 0.3 h. **Main confound:** largely implied by existing linear theory.
**Immediate KILL:** linear baselines predict all nonlinear behavior. **Broader claim
if positive:** KD risk can be forecast from teacher-student feature alignment.

## C09

**Research question:** Does neural collapse causally reduce OOD generalization
when logits, margin, and calibration are held fixed? **H0:** collapse has no
independent effect. **H1:** feature collapse still changes transfer/OOD behavior.
**Why important:** it tests whether geometry is mechanism or correlate. **Closest
papers:** [Harun et al. 2025](https://openreview.net/forum?id=8AGdUCdDyI),
[Wu & Mondelli 2025](https://openreview.net/forum?id=ZrhGq664om),
[Yi et al. 2025](https://openreview.net/forum?id=GySIAKEwtZ).
**Exact novelty delta:** logit-preserving causal control. **Cheapest experiment:**
small image/latent models with invertible feature transforms. **Expected runtime:**
1 h. **Main confound:** transfer retraining breaks logit equivalence. **Immediate
KILL:** current control paper already subsumes the intervention. **Broader claim if
positive:** feature geometry affects reusable information beyond predictions.

## C10

**Research question:** Does tail-class center collapse predict which classes fail
under a subsequent orthogonal covariate shift? **H0:** collapse adds no predictive
information beyond class count/margin. **H1:** per-class collapse predicts shifted
error after those controls. **Why important:** it could connect long-tail geometry
to actionable OOD risk. **Closest papers:** [Yi et al. 2025](https://openreview.net/forum?id=GySIAKEwtZ),
[Harun et al. 2025](https://openreview.net/forum?id=8AGdUCdDyI),
[Reddy et al. 2026](https://openreview.net/forum?id=sFjxg8cyJS).
**Exact novelty delta:** per-class prospective prediction under controlled shift.
**Cheapest experiment:** Gaussian mixtures and CIFAR-LT features. **Expected
runtime:** 0.75 h. **Main confound:** synthetic geometry determines the answer.
**Immediate KILL:** count/margin baseline matches collapse. **Broader claim if
positive:** training geometry forecasts class-specific shift failures.

## C11

**Research question:** At fixed context length, is attention-retrieval failure
controlled by the number of near-tie distractors rather than raw distractor-token
count? **H0:** raw length predicts failure after score matching. **H1:** near-tie
key multiplicity is the sufficient variable. **Why important:** it would sharpen
attention dilution into a measurable law. **Closest papers:** [Li et al. 2025](https://arxiv.org/abs/2501.08570),
[Wang et al. 2024](https://arxiv.org/abs/2404.12224), [Izzo et al. 2026](https://proceedings.iclr.cc/paper_files/paper/2026/hash/4a765a1bbf8332154e58bf452fbf806c-Abstract-Conference.html).
**Exact novelty delta:** cross distinctness and multiplicity at identical length.
**Cheapest experiment:** trained tiny attention retrieval plus frozen-attention
analytic control. **Expected runtime:** 0.5 h. **Main confound:** near-tie count is
already explicit in recent score-dilution theory. **Immediate KILL:** analytic
softmax prediction explains everything. **Broader claim if positive:** effective
distractor count replaces context length in retrieval scaling.

## C12

**Research question:** Does long auxiliary-task training transfer length
generalization because it exposes positions or because it reuses an algorithm?
**H0:** matched long-position exposure is sufficient. **H1:** only related
algorithmic structure transfers. **Why important:** it clarifies an actionable
cause behind extrapolation by association. **Closest papers:** [Cai et al. 2025](https://arxiv.org/abs/2506.09251),
[Kazemnejad et al. 2023](https://arxiv.org/abs/2305.19466),
[Huang et al. 2026](https://openreview.net/pdf/e4271113e9b6eecc295b51d021fa84269a56fa98.pdf).
**Exact novelty delta:** unrelated-but-position-matched auxiliary control.
**Cheapest experiment:** tiny Transformer on paired string transductions.
**Expected runtime:** 1 h. **Main confound:** relatedness is hard to match.
**Immediate KILL:** prior ablations already include the decisive control.
**Broader claim if positive:** algorithm reuse, not position exposure, causes
cross-task length transfer.

## C13

**Research question:** Does temporally persistent verifier noise damage RLVR more
than independently resampled noise at the same false-positive/negative rates?
**H0:** only aggregate error rates matter. **H1:** persistent prompt-level errors
cause policy lock-in. **Why important:** real verifier errors are systematic.
**Closest papers:** [Plesner et al. 2026](https://arxiv.org/abs/2604.07666),
[Mitsuhashi et al. 2026](https://arxiv.org/abs/2605.25252),
[Zhou et al. 2026](https://arxiv.org/abs/2608.20362),
[Fuzzing RLVR Verifiers](https://arxiv.org/abs/2606.01066).
**Exact novelty delta:** temporal correlation at matched confusion matrix.
**Cheapest experiment:** bandit first, then 0.5B GRPO. **Expected runtime:** 4–6 h.
**Main confound:** recent systematic-error studies. **Immediate KILL:** direct
collision on prompt-persistent errors. **Broader claim if positive:** verifier
audits require error correlation, not just accuracy.

## C14

**Research question:** Is effective class diversity per adaptation window the
control variable for entropy-minimization TTA collapse? **H0:** collapse follows
shift severity. **H1:** a diversity threshold predicts collapse across shifts.
**Why important:** it would give an early warning statistic. **Closest papers:**
[Ranked Entropy Minimization](https://openreview.net/forum?id=lHaGLJ65J9),
[GOTTA be diverse](https://openreview.net/forum?id=6EwuwivLSp),
[Monitoring Risks in TTA](https://openreview.net/forum?id=TzHX2RWUdE).
**Exact novelty delta:** a cross-method diversity threshold. **Cheapest
experiment:** pretrained CIFAR model with controlled streams. **Expected runtime:**
0.5 h. **Main confound:** directly covered by diversity-aware memory. **Immediate
KILL:** the same threshold/claim appears in current TTA work. **Broader claim if
positive:** stream diversity predicts safe adaptation.

## C15

**Research question:** When mutual information between facts and language is
fixed, does tokenizer overlap independently cause representational unification and
cross-language transfer? **H0:** overlap has no independent effect. **H1:** shared
tokens lower the unification threshold. **Why important:** it separates data
association from interface sharing. **Closest papers:** [Blum et al. 2026](https://openreview.net/forum?id=EGf7dks3tw),
[Dong et al. 2025](https://proceedings.mlr.press/v267/dong25g.html),
[Scale and Prediction Geometry 2026](https://arxiv.org/abs/2605.17084).
**Exact novelty delta:** factorial token-overlap × fact-language mutual
information with held-out orthography. **Cheapest experiment:** tiny bilingual
synthetic LM. **Expected runtime:** 1 h. **Main confound:** the nearest paper
already manipulates tokenization and association. **Immediate KILL:** its existing
ablations imply the factorial result. **Broader claim if positive:** token sharing
causally sets the cross-lingual unification threshold.

