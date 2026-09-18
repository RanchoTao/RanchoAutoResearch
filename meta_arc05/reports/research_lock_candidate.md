# Research lock candidate

## Original anchor

Single-layer deletion/swapping preserves 72–95% of intact LM top-1 predictions.

## Source

[Lad, Gurnee & Tegmark, “The Remarkable Robustness of LLMs: Stages of
Inference?”, NeurIPS 2025](https://proceedings.neurips.cc/paper_files/paper/2025/hash/bcad07d4bfab51243efaa08b8ed475b3-Abstract-Conference.html).

## Replicated phenomenon

On the paper’s Pythia-410M model and a held-out WikiText domain, middle-block
deletion retains 0.759–0.764 top-1 agreement across three 6,912-token shards.
Early/final boundary agreement is 0.589–0.600 and deletion has much larger excess
NLL. Intact perplexity is 28.7–30.1. The preregistered replication gate passes.

## New boundary law

After early LM competence appears, continued Pythia pretraining monotonically
*reduces* single-middle-block deletion robustness. On Pythia-160M, mean agreement
falls 0.694→0.665→0.651→0.568 from steps 1k→10k→50k→143k, strictly in all three
text shards. On prospectively held-out Pythia-70M it falls 0.397→0.274 from 1k to
143k; each shard declines by 0.107–0.131.

## Current evidence

- Published anchor and official intervention code inspected.
- Exact paper model family/member replicated on 20,736 tokens.
- Five-checkpoint discovery sweep, fixed architecture/data/seeds.
- Confidence control: Pythia-160M 1k→143k agreement declines in all five
  confidence bins (0.015–0.290; first four 0.233–0.290).
- Intact NLL improves sharply while robustness declines; 50k→143k robustness
  drops another 0.082 while intact NLL is nearly flat (3.75→3.78).
- Held-out scale and magnitude prediction passes on Pythia-70M; final intact NLL
  4.33–4.43 passes competence.

## Exact supported claim

For Pythia-70M and Pythia-160M on WikiText-2, after step1000, continued
pretraining reduces the fraction of intact top-1 predictions preserved by deleting
a middle Transformer block. This decline is replicated across three text shards
and is not eliminated by conditioning on intact top-1 confidence bins.

## Exact claim NOT supported

- The law is not yet shown outside the Pythia family or on downstream tasks.
- It does not show that overall representations become less redundant.
- It does not establish a causal mechanism for specialization.
- It does not imply later checkpoints are worse models; intact NLL improves.
- It is not a phase transition and no sharp boundary step is claimed.

## Required realistic validation

Repeat prospective early/final checkpoint comparisons on a non-Pythia family
with public trajectories (e.g. OLMo) and add one downstream multiple-choice task
where the intact model is competent.

## Required baselines

1. random block deletion versus zeroing only attention or only MLP;
2. equal-norm random residual perturbation;
3. weight interpolation between early/final checkpoints;
4. matched intact-NLL checkpoints across model sizes;
5. token-frequency and token-type stratification.

## Required ablations

- Swap versus deletion;
- multiple-block deletion;
- confidence, entropy, margin, and token-frequency matching;
- early/middle/final layer groups;
- pre-LN versus post-LN architecture if a checkpoint family is available.

## Required theory/mechanism analysis

Test whether growth in block update norm, residual-stream alignment, or reduced
cross-block substitutability predicts the agreement decline better than checkpoint
step. A useful theory should jointly explain the early rise from random logits and
the post-competence decline.

## Estimated full-project compute

Approximately 20–50 GPU-hours using only ≤1B public checkpoints; no training from
scratch is needed for the first cross-family study.

## Biggest threat

Top-1 agreement may remain an inference metric artifact even after confidence
stratification. Cross-architecture or downstream-task failure would kill the paper.

## Potential paper story

Layer redundancy is not a static property of residual architecture: causal
single-block substitutability peaks early and erodes during continued pretraining,
despite improving language-model loss. If cross-family validation succeeds, this
connects training dynamics to pruning windows and specialization.

## Independent-run validation update — ARC-20260825-5060-002

**Anchor phenomenon:** competent later checkpoints are less functionally robust
to bypassing one middle Transformer block than competent early checkpoints.

**Original source:** Lad, Gurnee & Tegmark, *The Remarkable Robustness of LLMs:
Stages of Inference?*, NeurIPS 2025.

**Previous evidence:** one canonical Pythia-160M trajectory plus a held-out
canonical Pythia-70M trajectory, with three evaluation/data resamples at each
scale. Those resamples were not independent pretraining runs.

**Independent-run evidence:** PolyPythias combined initialization/data-order
seed1–5, evaluated at steps 14k/36k/72k/107k/143k with the intervention, data,
layers and thresholds frozen before ARC-002 results.

**Number of genuine pretraining runs:** 10 total; 5 at 70M and 5 at 160M.

**70M result:** 5/5 late<early; mean agreement 0.4255→0.2891; median endpoint
delta -0.1433; bootstrap 95% CI for the mean [-0.1539, -0.1103].

**160M result:** 5/5 late<early; mean agreement 0.6568→0.5584; median endpoint
delta -0.0903; bootstrap 95% CI for the mean [-0.1097, -0.0898].

**Median late-early agreement delta:** -0.1433 at 70M; -0.0903 at 160M.

**NLL-damage trend:** increased in 5/5 runs at both scales; mean 1.2507→1.8552
at 70M and 0.4292→0.7539 at 160M.

**KL trend:** increased in 5/5 runs at both scales; mean 1.1949→1.8261 at 70M
and 0.3986→0.7252 at 160M.

**Confidence-matched result:** all 50 eligible fixed-bin run comparisons were
negative (25/25 per scale); every bin at both scales declined on average.

**Strongest counterexample:** 70M seed5 has the smallest endpoint decline
(-0.0873), a nonmonotonic intermediate trajectory, and a slight final intact-NLL
worsening. 70M seed4 also rebounds from step107k to step143k. Strict checkpoint
monotonicity is unsupported.

**Current exact supported claim:** across ten independent PolyPythias runs at
70M/160M on WikiText-2, a competent final checkpoint preserves fewer intact
top-1 predictions after one middle-block bypass than a competent ~10%-progress
checkpoint. The direction holds for all runs and resamples, agrees with NLL/KL
damage, and survives fixed confidence bins and simple NLL adjustment.

**Claims still unsupported:** cross-family or downstream-task generality;
universal monotonicity; layer specialization or a causal mechanism; separate
effects of initialization versus data order; pruning recommendations.

**Recommended next validation:** **CROSS-FAMILY** using a public non-Pythia
checkpoint trajectory plus one competent downstream task.

## Cross-family validation update — ARC-20260825-5060-003

**External family:** SmolLM2-360M, a 361,821,120-parameter Llama/GQA model
trained with Nanotron on a non-Pile recipe. Five checkpoints from one public
run were evaluated at 12.5%, 31.25%, 50%, 75%, and 100% progress.

**Competence:** the final model passes the preregistered 256-example HellaSwag
gate with length-normalized accuracy 0.5508 (bootstrap 95% CI
[0.4883, 0.6094]); all five checkpoints exceed the 0.40 threshold.

**Primary result:** middle-block bypass agreement declines 0.8302→0.7888,
delta -0.04135. All three fixed resample deltas are negative and their
bootstrap interval excludes zero. All five fixed confidence bins decline.

**Functional result:** deleted-minus-intact NLL rises 0.2061→0.3321 and KL
rises 0.2009→0.3302.

**Why verdict is MIXED:** the primary effect misses the preregistered -0.05
magnitude gate. The middle trajectory is almost flat, and 58.7% of the primary
decline plus effectively all secondary damage growth occurs in the final
interval. SmolLM2-360M uses WSD with a final 20% decay phase, which the selected
75% and 100% checkpoints straddle.

**Current exact supported claim:** one competent non-Pythia trajectory has the
same endpoint direction under the frozen WikiText-2 block-bypass assay, but the
effect is smaller than preregistered and may be specific to the learning-rate
decay regime.

**Current claim NOT supported:** a general cross-family training law, smooth or
monotonic erosion, downstream deletion sensitivity, or a mechanism.

**Recommended next validation:** prospectively resolve the public SmolLM2
80–100% WSD decay window at 81.25%, 87.5%, and 93.75% before testing another
family. If the late-window pattern is incoherent, retire the cross-family law.

## WSD-window resolution update — ARC-20260825-5060-004

**Verdict: PROMOTE-BROAD under the frozen contract.**

The best-supported WSD decay boundary is step2.048M (80%), inferred from the
official 20% decay statement and public final step2.56M; no exact boundary
checkpoint exists. New measurements at 81.25%, 87.5%, and 93.75% were combined
with the exact ARC-003 BF16 records.

Pre-decay agreement declines 0.8302→0.8131, delta -0.01708, with all three
resamples negative and bootstrap 95% CI [-0.02250, -0.00866]. It accounts for
41.3% of the total endpoint decline. The total excluding the final checkpoint
remains negative (-0.02252, CI [-0.03234, -0.00953]).

Confirmed decay agreement declines 0.8157→0.7888, delta -0.02685, all three
resamples negative, CI [-0.03032, -0.02335]. Excluding final, the decay decline
remains -0.00802, CI [-0.00846, -0.00775]. The final interval is nevertheless
the largest and supplies 77.6% of the boundary-bracketing decline.

NLL damage and KL do not robustly increase pre-decay; their growth is
concentrated during decay and survives final exclusion. The eight-point
NLL-adjusted progress association is weak. Therefore the supported broad claim
is limited to top-1 block substitutability, not every functional metric.

**Current supported claim:** the SmolLM2 primary effect precedes final WSD
decay, while a steeper late-phase change may amplify it. This is temporal
association, not WSD causality.

**Recommended next validation:** test block-bypass sensitivity on the already
validated downstream HellaSwag task at a small frozen checkpoint/layer subset;
do not begin mechanism claims until downstream relevance is known.
