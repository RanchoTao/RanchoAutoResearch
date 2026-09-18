# Research question and claim boundary

## 1. Original question

The original line asked whether single-interior-layer substitutability declines over language-model pretraining. That broad phenomenon is not a defensible novelty claim because nearby work already studies training-dependent, protocol-dependent layer equivalence.

## 2. Most reliable current question

In a frozen small-Pythia assay, can training-conditioned top-1 responses to interior-block interventions be summarized by raw perturbation magnitude or by matched output-level predictive damage, or does intervention construction retain measurable structure after these controls?

## 3. Interventions actually used

- **Literal block bypass / deletion-equivalent path:** the block returns its residual input.
- **Residual attenuation:** for block output `b(x)` and residual input `x`, `b_alpha(x) = b(x) - alpha [b(x)-x]`, with `alpha in {0.25, 0.50, 0.75, 1.00}`; `alpha=1` is bypass.
- **Norm-controlled additive activation noise:** a frozen random direction is added after the intact block, scaled by local activation norm; direction IDs `101, 202, 303` were used in the confirmatory family experiment.
- **Continuous-alpha direction counterfactuals:** attempted in ARC-008/009 only for identification feasibility. The support gates failed and no top-1 causal outcome was revealed.

No weight perturbation, skip fine-tuning, learned adapter, pruning retraining, or production intervention is part of the validated thesis.

## 4. Intervention-strength matching

Within residual attenuation, deterministic non-reuse matching compares interventions within run and checkpoint:

- magnitude matching: relative-magnitude ratio at most `1.10` while KL differs by at least `0.03`;
- damage matching: KL difference at most `max(0.01, 0.10*mean_KL)` and NLL-damage difference at most `max(0.015, 0.10*mean_NLL)`, with layer separation at least 3 or magnitude ratio at least 1.25.

Across block and noise families, each block cell defines a joint KL/NLL target. Outcome-blind search chooses noise strength from KL, NLL, and technical diagnostics. Strict Class A requires both frozen relative calipers. Canonical strict support is 103/150 cells; A+B support is 134/150.

## 5. Role of KL, NLL, and other metrics

- `KL(p_intact || p_intervened)` and target-token NLL increase describe output-level predictive damage.
- They are matching/control variables and severity descriptors, not proven causes or complete measures of function.
- `S` is the fraction of identical next-token argmax predictions between intact and intervened models on fixed teacher-forced positions.
- `D_S = 1-S` is top-1 damage; `Delta S = S_late-S_early` is the training endpoint change.
- Relative residual-change norm is the raw local magnitude descriptor; absolute activation RMS is secondary.
- Output-logit norm, margins, and boundary-alignment features are an associational geometry block.

## 6. Main empirical phenomenon

Top-1 agreement under block bypass falls from competent early to late checkpoints across independent Pythia runs. More importantly for the current thesis, block bypass and norm-controlled activation noise retain different top-1 damage after prospective joint KL/NLL matching. The corrected mean family residual is `-0.016833044`, with 5/5 negative run medians.

## 7. What is general within current evidence

- Directional replication across the tested independent Pythia pretraining runs.
- Directional replication at 70M and 160M and on two fixed English evaluation streams.
- Within the frozen attenuation design, predictive damage is more informative than raw displacement.
- In the corrected 160M WikiText-2 matched comparison, KL/NLL matching is insufficient to remove all block/noise structure.

These are bounded replications, not universal laws.

## 8. Inconsistency and directional exceptions

The paper-level family residual is aggregate and seed-stable, but 24 of 103 strict matched cells reverse sign (`23.3%`). Layer effects are heterogeneous and layer 7 has only three strict matches. Therefore the evidence does not support a uniform cellwise or layer-invariant family ordering. The “about 20%” statement should be written as the exact `24/103` result, not rounded into a stronger claim.

## 9. Safest conclusion boundary

In the tested Pythia-160M/WikiText-2 assay, equality or close matching on forward KL and target-token NLL does not guarantee equality of the teacher-forced top-1-damage response across block bypass and norm-controlled activation noise. Raw magnitude and the tested output geometry also do not fully summarize the aggregate response.

This does not establish semantic non-equivalence, downstream non-equivalence, causal mediation, universal intervention-family dependence, or an internal mechanism.

## 10. Evaluation of the proposed core sentence

> Output-level distributional similarity / matched degradation does not necessarily imply functional equivalence of different internal interventions.

This is **too broad if “functional equivalence” means equality of the full model function or downstream behavior**. The experiment matched two selected output-level damage summaries (forward KL and target-token NLL), not the entire output distribution, and then observed a residual in another logit-derived endpoint (`D_S`).

A faithful version is:

> In the tested small-Pythia assay, prospectively matched forward-KL and target-token-NLL damage does not guarantee equal teacher-forced top-1 damage for block bypass and norm-controlled activation noise.

That statement matches the actual experiment without overclaiming.
