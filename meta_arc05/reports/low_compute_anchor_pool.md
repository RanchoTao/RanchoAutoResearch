# Low-compute anchor pool

Screened 2026-08-25. Quantities below are taken from the linked primary paper
or its abstract/table when available. “Not stated in abstract” is recorded rather
than reconstructed. Cost estimates refer to the smallest scientifically competent
replication, not the full paper.

## ANCHOR-01 — single-layer deletion robustness

- **Source paper:** [The Remarkable Robustness of LLMs: Stages of Inference?](https://proceedings.neurips.cc/paper_files/paper/2025/hash/bcad07d4bfab51243efaa08b8ed475b3-Abstract-Conference.html)
- **Venue/year:** NeurIPS 2025.
- **Exact empirical anomaly:** deleting or swapping an entire Transformer block
  often preserves the original next-token prediction.
- **Reported quantitative result:** 72–95% of original top-1 predictions retained
  without fine-tuning; deeper models are more robust.
- **Why surprising:** each expensive block appears essential during normal
  inference, yet many can be removed independently.
- **Exact setup:** eight+ autoregressive LMs including Pythia-410M; The Pile;
  layer deletion/swap and top-1 agreement.
- **Estimated reproduction GPU time:** 10–25 min on Pythia-410M.
- **Code/data:** [official code](https://github.com/vdlad/Remarkable-Robustness-of-LLMs);
  model public; Pile/WikiText text public.
- **Candidate control variable:** pretraining progress/checkpoint age.
- **Why boundary may matter:** residual architecture predicts robustness at
  initialization, while learned redundancy predicts growth with competence.
- **Follow-up status:** pruning and redundancy work studies final models; no
  direct training-checkpoint boundary map was found in targeted search.
- **Likely Reviewer-2 objection:** top-1 agreement is inflated by easy tokens and
  says little about loss or downstream competence.

## ANCHOR-02 — zero-shot symmetry breaking in Neural ODEs

- **Source paper:** [Context-Informed Neural ODEs Unexpectedly Identify Broken Symmetries](https://proceedings.mlr.press/v267/huh25a.html)
- **Venue/year:** ICML 2025.
- **Exact empirical anomaly:** free-form context-conditioned NODEs trained only
  before a bifurcation recover post-bifurcation symmetry-broken dynamics.
- **Reported quantitative result:** zero-shot recovery is reported across the
  bifurcation; no single aggregate number is stated in the abstract.
- **Why surprising:** training data contains no broken-symmetry trajectory.
- **Exact setup:** localized pre-bifurcation dynamical trajectories and
  Landau–Khalatnikov systems.
- **Estimated reproduction GPU time:** 10–40 min.
- **Code/data:** paper equations sufficient for synthetic data; no official code
  link found on PMLR.
- **Candidate control variable:** span of pre-bifurcation context values.
- **Why boundary may matter:** coefficient/topology identifiability should vanish
  when the context range becomes too narrow.
- **Follow-up status:** the paper derives recovery/hallucination conditions, so a
  new sweep risks restating its theory.
- **Likely Reviewer-2 objection:** polynomial extrapolation, not learned topology.

## ANCHOR-03 — longer CE training can reduce pass@N

- **Source paper:** [Rethinking Fine-Tuning when Scaling Test-Time Compute](https://proceedings.neurips.cc/paper_files/paper/2025/hash/e8f4eae0a41cab67fdead3aa6b77f083-Abstract-Conference.html)
- **Venue/year:** NeurIPS 2025.
- **Exact empirical anomaly:** pass@1 rises while high-budget pass@N falls with
  additional cross-entropy fine-tuning.
- **Reported quantitative result:** on MATH/Llama-3-8B, epochs 1→4 change pass@1
  4.4%→7.4% but pass@4096 82.5%→63.0%.
- **Why surprising:** a better single-sample model becomes worse under search.
- **Exact setup:** 8B math fine-tuning, MATH and MiniF2F, direct answer/CoT/proof.
- **Estimated reproduction GPU time:** 20–60 min in a controlled small
  multi-answer classification analogue; exact LLM replication exceeds budget.
- **Code/data:** MATH public; exact small harness would be a deviation.
- **Candidate control variable:** target-answer multiplicity/entropy.
- **Why boundary may matter:** overconfidence is harmful only when multiple valid
  modes support search diversity.
- **Follow-up status:** the paper already proves a confidence/N relationship.
- **Likely Reviewer-2 objection:** a toy classification analogue is not math search.

## ANCHOR-04 — weak-to-strong learning in random features

- **Source paper:** [Weak-to-Strong Generalization Even in Random Feature Networks, Provably](https://proceedings.mlr.press/v267/medvedev25a.html)
- **Venue/year:** ICML 2025.
- **Exact empirical anomaly:** a larger random-feature student trained only on a
  weaker teacher’s outputs can outperform that teacher.
- **Reported quantitative result:** theory/experiments allow PGR approaching 1;
  ReLU error scales roughly as teacher-error^1.49 and linear anisotropic error as
  teacher-error^2 in the studied asymptotics.
- **Why surprising:** the student receives no labels better than the teacher’s.
- **Exact setup:** fixed random bottom layers, trained linear heads, early stopping.
- **Estimated reproduction GPU time:** <5 min; largely CPU.
- **Code/data:** analytically generated Gaussian data; no official repository found.
- **Candidate control variable:** alignment of teacher error with the student
  feature eigenspectrum.
- **Why boundary may matter:** equally sized teacher error may be correctable or
  inherited depending on its geometry.
- **Follow-up status:** paper proves broad limits for convex regularization;
  novelty space is narrow.
- **Likely Reviewer-2 objection:** a corollary of kernel regression spectral bias.

## ANCHOR-05 — temperature scaling worsens conformal set size

- **Source paper:** [On Temperature Scaling and Conformal Prediction of Deep Classifiers](https://proceedings.mlr.press/v267/dabah25a.html)
- **Venue/year:** ICML 2025.
- **Exact empirical anomaly:** temperature scaling improves class-conditional
  coverage of adaptive conformal prediction while increasing prediction-set size.
- **Reported quantitative result:** a non-monotonic temperature trade-off is
  reported across CIFAR/ImageNet classifiers; no single abstract scalar.
- **Why surprising:** standard calibration makes conformal predictions less efficient.
- **Exact setup:** saved deep-classifier logits, APS/RAPS-style conformal methods.
- **Estimated reproduction GPU time:** <5 min with public logits.
- **Code/data:** [official TS4CP code](https://github.com/lahavdabah/TS4CP).
- **Candidate control variable:** base-model over- versus under-confidence.
- **Why boundary may matter:** fitted temperature can cross 1 and reverse score
  concentration effects.
- **Follow-up status:** the paper’s theory already explains the non-monotonic curve.
- **Likely Reviewer-2 objection:** trivial consequence of the APS score definition.

## ANCHOR-06 — two-pass SGD can catastrophically overfit

- **Source paper:** [Rapid Overfitting of Multi-Pass SGD in Stochastic Convex Optimization](https://proceedings.mlr.press/v267/vansover-hager25a.html)
- **Venue/year:** ICML 2025.
- **Exact empirical anomaly:** one extra pass can turn minimax generalization into
  constant population excess risk.
- **Reported quantitative result:** with step size Θ(1/√n), excess risk moves from
  Θ(1/√n) after one pass to Ω(1) after two.
- **Why surprising:** severe overfitting normally suggests many epochs/capacity.
- **Exact setup:** constructed non-smooth convex stochastic optimization problems.
- **Estimated reproduction GPU time:** <1 min CPU.
- **Code/data:** analytic synthetic construction; no code needed in principle.
- **Candidate control variable:** smoothing strength.
- **Why boundary may matter:** the paper leaves smooth constrained SCO open.
- **Follow-up status:** without/with-replacement orderings are already covered.
- **Likely Reviewer-2 objection:** adversarial construction lacks neural relevance.

## ANCHOR-07 — grokking at linear-separability edge

- **Source paper:** [Grokking at the Edge of Linear Separability](https://proceedings.mlr.press/v267/beck25a.html)
- **Venue/year:** ICML 2025.
- **Exact empirical anomaly:** delayed generalization becomes arbitrarily long near
  the separability/interpolation boundary in logistic random features.
- **Reported quantitative result:** sharp separability probability occurs around
  sample-to-dimension ratio 1/2 in the analyzed random geometry.
- **Why surprising:** a perfect population solution exists throughout.
- **Exact setup:** binary logistic classification, random features, constant labels.
- **Estimated reproduction GPU time:** <5 min.
- **Code/data:** synthetic; paper gives tractable one-dimensional model.
- **Candidate control variable:** anisotropy of input covariance.
- **Why boundary may matter:** effective rather than raw dimension may set the edge.
- **Follow-up status:** separability is already the paper’s central explanation.
- **Likely Reviewer-2 objection:** merely replace dimension by effective rank.

## ANCHOR-08 — supercollapse of normalized learning curves

- **Source paper:** [Scaling Collapse Reveals Universal Dynamics](https://proceedings.mlr.press/v267/qiu25j.html)
- **Venue/year:** ICML 2025.
- **Exact empirical anomaly:** normalized loss curves across sizes become more
  similar than seed noise under learning-rate decay.
- **Reported quantitative result:** cross-model differences fall below the
  within-model random-seed noise floor (“supercollapse”).
- **Why surprising:** architectures, schedules, and model sizes differ strongly.
- **Exact setup:** compute-optimal models across datasets/architectures including LMs.
- **Estimated reproduction GPU time:** 1–3 h for a small CNN/Transformer family.
- **Code/data:** paper states code is public; exact link is not exposed in PMLR text.
- **Candidate control variable:** degree of horizon mis-scaling.
- **Why boundary may matter:** collapse is proposed as an optimality diagnostic.
- **Follow-up status:** suboptimal hyperparameter breakdown is already studied.
- **Likely Reviewer-2 objection:** normalization mathematically forces similarity.

## ANCHOR-09 — state coverage beats observed length in recurrent models

- **Source paper:** [Understanding and Improving Length Generalization in Recurrent Models](https://openreview.net/forum?id=2OEb20dy7B)
- **Venue/year:** ICML 2025.
- **Exact empirical anomaly:** expanding recurrent-state coverage can improve
  length generalization without simply extending train length.
- **Reported quantitative result:** qualitative multi-task gains; no single abstract scalar.
- **Why surprising:** sequence length is not the sufficient training-support variable.
- **Exact setup:** recurrent sequence models on algorithmic tasks.
- **Estimated reproduction GPU time:** 10–30 min.
- **Code/data:** synthetic tasks; public paper resources.
- **Candidate control variable:** state-space mixing time.
- **Why boundary may matter:** equal marginal coverage may not cover transitions.
- **Follow-up status:** closely overlaps the paper’s causal intervention.
- **Likely Reviewer-2 objection:** state coverage is engineered into the generator.

## ANCHOR-10 — sparse dependencies enable length generalization

- **Source paper:** [The Role of Sparsity for Length Generalization in LLMs](https://proceedings.mlr.press/v267/golowich25a.html)
- **Venue/year:** ICML 2025.
- **Exact empirical anomaly:** decoder Transformers length-generalize when each
  next token depends on only a fixed small number of prior tokens.
- **Reported quantitative result:** effect replicated on synthetic and natural
  language tasks; no aggregate scalar in abstract.
- **Why surprising:** total context length can grow while dependency count stays fixed.
- **Exact setup:** k-sparse planted correlations and Predictive Position Coupling.
- **Estimated reproduction GPU time:** 15–45 min.
- **Code/data:** synthetic generator specified; public paper.
- **Candidate control variable:** dependency overlap/reuse, not just k.
- **Why boundary may matter:** identical k can induce different attention collisions.
- **Follow-up status:** sparsity itself is fully central to the paper.
- **Likely Reviewer-2 objection:** a minor variant of their planted distribution.

## ANCHOR-11 — dropout hurts single-epoch LM pretraining

- **Source paper:** [Drop Dropout on Single Epoch Language Model Pretraining](https://aclanthology.org/2025.findings-acl.111/)
- **Venue/year:** Findings of ACL 2025.
- **Exact empirical anomaly:** no dropout outperforms standard and early dropout
  across LM and downstream tasks.
- **Reported quantitative result:** consistent direction on Pythia-160M/1.4B,
  BLiMP, SQuAD, MNLI; abstract gives no single delta.
- **Why surprising:** dropout is a canonical generalization regularizer.
- **Exact setup:** one-epoch BERT and autoregressive Pythia pretraining.
- **Estimated reproduction GPU time:** >3 h for faithful pretraining; public
  checkpoints could permit partial analysis.
- **Code/data:** standard corpora/models; code availability not confirmed.
- **Candidate control variable:** expected sample revisit count.
- **Why boundary may matter:** the regularizer should regain value when reuse begins.
- **Follow-up status:** single versus multi-epoch rationale is explicit.
- **Likely Reviewer-2 objection:** ordinary overfitting textbook behavior.

## ANCHOR-12 — simple time-series Transformers beat complex ones

- **Source paper:** [A Closer Look at Transformers for Time Series Forecasting](https://proceedings.mlr.press/v267/chen25f.html)
- **Venue/year:** ICML 2025.
- **Exact empirical anomaly:** simple intra-variate models match/beat models built
  to exploit inter-variate attention on popular benchmarks.
- **Reported quantitative result:** inter-variate dependencies contribute only a
  minor fraction in studied benchmarks; no abstract scalar.
- **Why surprising:** multivariate benchmarks nominally require cross-channel reasoning.
- **Exact setup:** point/patch/variate tokenization, synthetic MI controls, healthcare data.
- **Estimated reproduction GPU time:** 15–45 min on synthetic and small ETTh subset.
- **Code/data:** PMLR links software and public benchmarks.
- **Candidate control variable:** controlled cross-variate mutual information.
- **Why boundary may matter:** architecture ordering should reverse once cross-MI dominates.
- **Follow-up status:** the paper already performs this synthetic isolation.
- **Likely Reviewer-2 objection:** replotting their MI experiment.

## ANCHOR-13 — test-time training gives large few-shot gains

- **Source paper:** [The Surprising Effectiveness of Test-Time Training for Few-Shot Learning](https://proceedings.mlr.press/v267/akyurek25a.html)
- **Venue/year:** ICML 2025.
- **Exact empirical anomaly:** gradient updates on in-context examples far exceed
  prompting for structurally novel tasks.
- **Reported quantitative result:** ARC up to 6× and 53.0%; BBH 50.5%→57.8%.
- **Why surprising:** inference-time weight updates outperform a model trained for ICL.
- **Exact setup:** 8B LM, ARC/BBH, temporary fine-tuning per task.
- **Estimated reproduction GPU time:** exact result infeasible; small regression
  analogue <30 min but is not a faithful replication.
- **Code/data:** PMLR links software; ARC/BBH public.
- **Candidate control variable:** demonstration diversity at fixed alignment.
- **Why boundary may matter:** low-rank demos can make adaptation harmful.
- **Follow-up status:** theoretical 2025 work already studies TTT gains.
- **Likely Reviewer-2 objection:** small synthetic analogue does not anchor the LLM effect.

## ANCHOR-14 — entropy-minimization TTA collapses to one class

- **Source paper:** [Ranked Entropy Minimization for Continual Test-Time Adaptation](https://proceedings.mlr.press/v267/han25e.html)
- **Venue/year:** ICML 2025.
- **Exact empirical anomaly:** ordinary entropy minimization can converge to
  predicting one class for all continual-shift images.
- **Reported quantitative result:** widespread collapse across evaluated streams;
  no one scalar in abstract.
- **Why surprising:** a standard adaptation objective destroys the classifier.
- **Exact setup:** pretrained image classifier and continual corruption streams.
- **Estimated reproduction GPU time:** 20–60 min with CIFAR-C and a small ResNet.
- **Code/data:** PMLR software link; CIFAR-C public.
- **Candidate control variable:** class-transition/mixing rate in the stream.
- **Why boundary may matter:** collapse may require persistent low-diversity batches.
- **Follow-up status:** stability is central, but temporal mixing boundary is less clear.
- **Likely Reviewer-2 objection:** batch class imbalance trivially drives entropy collapse.

## ANCHOR-15 — higher-quality generated images are easier to detect

- **Source paper:** [Are High-Quality AI-Generated Images More Difficult for Models to Detect?](https://proceedings.mlr.press/v267/xiao25g.html)
- **Venue/year:** ICML 2025.
- **Exact empirical anomaly:** higher human-preference scores correlate with
  *higher* detector accuracy.
- **Reported quantitative result:** consistent quality–detectability trend across
  generators/detectors; no scalar in abstract.
- **Why surprising:** photorealism should hide synthetic origin.
- **Exact setup:** public generated images, preference scorers, off-the-shelf detectors.
- **Estimated reproduction GPU time:** 20–60 min inference; downloads dominate.
- **Code/data:** [official code/data](https://github.com/Coxy7/AIGI-Detection-Quality-Paradox).
- **Candidate control variable:** image downsampling/compression.
- **Why boundary may matter:** high-frequency generator artifacts and semantic
  quality respond oppositely to resolution.
- **Follow-up status:** prompt length/saturation/texture already analyzed.
- **Likely Reviewer-2 objection:** preference model and detector share visual biases.

## ANCHOR-16 — moderate corruption training improves self-repair, heavy hurts

- **Source paper:** [Error dynamics of symbolic context in small transformers](https://openreview.net/forum?id=Hnk3AHcqzG)
- **Venue/year:** ICLR 2026 submission (not accepted archival evidence).
- **Exact empirical anomaly:** moderate corruption fine-tuning improves spontaneous
  context repair but heavy corruption weakens it.
- **Reported quantitative result:** robustness half-points τ50 around 27–34% corruption.
- **Why surprising:** more corruption exposure does not monotonically improve robustness.
- **Exact setup:** small arithmetic Transformers and label-preserving corruption.
- **Estimated reproduction GPU time:** 15–45 min.
- **Code/data:** synthetic; supplementary availability unclear.
- **Candidate control variable:** mutual information remaining after corruption.
- **Why boundary may matter:** sign may track identifiability rather than noise fraction.
- **Follow-up status:** weak archival status and method-specific metrics lower priority.
- **Likely Reviewer-2 objection:** generated corruption defines the elbow.

## ANCHOR-17 — looped shallow Transformers rival deep untied models

- **Source paper:** [Reasoning with Latent Thoughts: On the Power of Looped Transformers](https://proceedings.iclr.cc/paper_files/paper/2025/hash/2676109d49d1eb26d6bc584a8f556305-Abstract-Conference.html)
- **Venue/year:** ICLR 2025.
- **Exact empirical anomaly:** k layers looped L times nearly match or beat kL
  independently parameterized layers on several tasks.
- **Reported quantitative result:** near-match on addition/p-hop/math; no scalar in abstract.
- **Why surprising:** severe parameter tying does not erase depth benefits.
- **Exact setup:** synthetic reasoning plus language-model downstream tasks.
- **Estimated reproduction GPU time:** 20–60 min on addition/p-hop.
- **Code/data:** public conference artifacts; synthetic generation.
- **Candidate control variable:** per-iteration input novelty/state change.
- **Why boundary may matter:** repeated computation should fail when steps require
  heterogeneous transformations.
- **Follow-up status:** loop count/task family are already broadly evaluated.
- **Likely Reviewer-2 objection:** recurrent weight sharing is an old result.

## ANCHOR-18 — longer context SFT improves short-context tasks

- **Source paper:** [When Long Helps Short](https://aclanthology.org/2025.emnlp-main.522/)
- **Venue/year:** EMNLP 2025.
- **Exact empirical anomaly:** long-context SFT improves short-context aggregate
  performance, opposite to long-context continued-pretraining behavior.
- **Reported quantitative result:** measurable aggregate gains; abstract supplies
  no single delta.
- **Why surprising:** longer examples appear less matched to the target tasks.
- **Exact setup:** LLM SFT with long/short mixtures, MHA/FFN ablations.
- **Estimated reproduction GPU time:** faithful result >3 h; small-model proxy risky.
- **Code/data:** paper/public benchmarks; compute-heavy.
- **Candidate control variable:** contextual versus parametric answer dependence.
- **Why boundary may matter:** preference bias should reverse by knowledge source.
- **Follow-up status:** paper already identifies that bias and hybrid solution.
- **Likely Reviewer-2 objection:** token budget is not matched by example count.

## ANCHOR-19 — corrective rationales hurt learning from mistakes

- **Source paper:** [No Need for Explanations](https://aclanthology.org/2025.emnlp-main.1686/)
- **Venue/year:** EMNLP 2025.
- **Exact empirical anomaly:** incorrect answers without rationales help math
  reasoning more than incorrect answers with detailed correction rationales.
- **Reported quantitative result:** consistent across model sizes and exceeds CoT;
  no scalar in abstract.
- **Why surprising:** more explicit supervision hurts in-context correction.
- **Exact setup:** prompted LLMs on math tasks.
- **Estimated reproduction GPU time:** >1 h with 1B-class model; competence uncertain.
- **Code/data:** paper tasks public; exact generations needed.
- **Candidate control variable:** rationale lexical overlap with target solution.
- **Why boundary may matter:** overconstraint may depend on shared solution form.
- **Follow-up status:** paper already controls context length/diversity and finds overfit.
- **Likely Reviewer-2 objection:** prompt formatting/model-specific artifact.

## ANCHOR-20 — mitigating a different subgroup can improve target fairness

- **Source paper:** [Subgroups Matter for Robust Bias Mitigation](https://proceedings.mlr.press/v267/alloula25a.html)
- **Venue/year:** ICML 2025.
- **Exact empirical anomaly:** target-group fairness can improve most when
  mitigation uses a different subgroup partition.
- **Reported quantitative result:** empirical/theoretical examples across tasks;
  no abstract scalar.
- **Why surprising:** the observed disparity need not identify the right intervention group.
- **Exact setup:** controlled subgroup correlations and fairness mitigation methods.
- **Estimated reproduction GPU time:** 5–20 min.
- **Code/data:** PMLR software; small tabular/image tasks.
- **Candidate control variable:** conditional correlation between observed and latent groups.
- **Why boundary may matter:** mitigation target should switch at a correlation threshold.
- **Follow-up status:** this is essentially the paper’s theoretical contribution.
- **Likely Reviewer-2 objection:** boundary follows directly from the causal graph.

## ANCHOR-21 — critical batch size evolves during LM training

- **Source paper:** [Critical Batch Size Revisited](https://proceedings.neurips.cc/paper_files/paper/2025/hash/a99f732df9b668284b449da0214a3286-Abstract-Conference.html)
- **Venue/year:** NeurIPS 2025.
- **Exact empirical anomaly:** the batch size beyond which scaling is inefficient
  changes substantially during training and transfers across model scale.
- **Reported quantitative result:** trend reported for 1B and 7B models; abstract
  provides no scalar.
- **Why surprising:** critical batch size is often treated as a task/model constant.
- **Exact setup:** empirical batch sweeps at LM checkpoints.
- **Estimated reproduction GPU time:** faithful test >3 h.
- **Code/data:** paper resources; requires large training runs.
- **Candidate control variable:** gradient-noise scale versus validation loss.
- **Why boundary may matter:** training progress may be a better coordinate than tokens.
- **Follow-up status:** evolution is already the paper’s focus.
- **Likely Reviewer-2 objection:** known gradient-noise-scale behavior.

## ANCHOR-22 — model scaling changes adversarial robustness non-uniformly

- **Source paper:** [Scaling Trends in Language Model Robustness](https://proceedings.mlr.press/v267/howe25a.html)
- **Venue/year:** ICML 2025.
- **Exact empirical anomaly:** robustness does not inherit a single clean scaling
  law across attacks/tasks/model families.
- **Reported quantitative result:** extensive multi-family trends; no abstract scalar.
- **Why surprising:** capability scaling does not straightforwardly imply robustness scaling.
- **Exact setup:** LM classification tasks, attacks, multiple open model families.
- **Estimated reproduction GPU time:** 1–3 h on ≤1B subset.
- **Code/data:** PMLR resources and open models.
- **Candidate control variable:** clean-task margin.
- **Why boundary may matter:** scale effect may reverse at matched clean confidence.
- **Follow-up status:** scaling lens already central; small subset underpowered.
- **Likely Reviewer-2 objection:** attack strength is not comparable across scales.

## ANCHOR-23 — horizon reduction improves longer-horizon generalization

- **Source paper:** [On Training LMs for Long-Horizon Tasks](https://openreview.net/forum?id=PnHfrCMKtp)
- **Venue/year:** ICML 2026.
- **Exact empirical anomaly:** reducing training horizon improves inference on
  longer-horizon variants.
- **Reported quantitative result:** controlled cross-horizon gains; no abstract scalar.
- **Why surprising:** less exposure to long trajectories yields better long-horizon behavior.
- **Exact setup:** controlled task constructions and language models.
- **Estimated reproduction GPU time:** 30–120 min in the smallest task.
- **Code/data:** OpenReview resources; availability to verify.
- **Candidate control variable:** per-step error correlation.
- **Why boundary may matter:** horizon reduction only helps when local errors compound.
- **Follow-up status:** very recent; nearest follow-up unclear.
- **Likely Reviewer-2 objection:** reduced horizon simply increases effective sample count.

## ANCHOR-24 — quantization robustness is non-monotonic over training

- **Source paper:** [Training Dynamics Impact Quantization Degradation](https://neurips.cc/virtual/2025/126559)
- **Venue/year:** NeurIPS 2025.
- **Exact empirical anomaly:** quantization degradation depends jointly on learning
  rate decay and validation loss, contradicting a monotone training-quality story.
- **Reported quantitative result:** validated with 160M models trained up to 100B
  tokens and open trajectories; no abstract scalar.
- **Why surprising:** later/better checkpoints need not be more quantization-robust.
- **Exact setup:** weight quantization over LM training trajectories.
- **Estimated reproduction GPU time:** 15–45 min inference using public Pythia checkpoints.
- **Code/data:** open checkpoints; conference resources.
- **Candidate control variable:** learning-rate phase at matched validation loss.
- **Why boundary may matter:** schedule position may reverse the loss–robustness relation.
- **Follow-up status:** the paper itself isolates this interplay.
- **Likely Reviewer-2 objection:** quantizer calibration artifact.

## ANCHOR-25 — equal per-layer next-token improvement law

- **Source paper:** [A law of next-token prediction in large language models](https://journals.aps.org/pre/abstract/10.1103/5rn3-49lc)
- **Venue/year:** Physical Review E 2025.
- **Exact empirical anomaly:** layers reportedly contribute approximately equally
  to next-token prediction improvement across diverse LMs.
- **Reported quantitative result:** claimed architecture/data-independent layerwise
  equality; abstract gives no deviation statistic.
- **Why surprising:** layer-deletion work finds strongly non-uniform early/final sensitivity.
- **Exact setup:** open autoregressive LMs, per-layer decoding/progress metrics.
- **Estimated reproduction GPU time:** 10–30 min on ≤410M models.
- **Code/data:** open models; code availability unclear.
- **Candidate control variable:** decoding basis/normalization method.
- **Why boundary may matter:** apparent equality may disappear with causal deletion.
- **Follow-up status:** directly tensions ANCHOR-01 but risks metric-artifact work.
- **Likely Reviewer-2 objection:** logit-lens calibration creates the law.

## Screening summary

Seven anchors pass a minimal “real phenomenon + ≤3 h + competent small setup”
screen: 01, 02, 04, 05, 06, 14, and 24. Anchors 07, 08, 09, 10, 12, 17,
20, and 25 are cheap but too close to their source paper’s own explanatory sweep.
The remainder require large-model competence, expensive pretraining, weak archival
evidence, or an unfaithful toy proxy.
