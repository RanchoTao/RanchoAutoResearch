# ARC-20260828-5060-012 — Executive summary

## Final verdict

# NOVELTY-BORDERLINE

**Confidence: HIGH.** All required conceptual clusters were covered, including
recent 2025–2026 work, and ten T3–T5 papers were checked against primary
records. No local PDF, model, dataset, code, or package download was made.

## Which claim overlaps

The broad version of Claim 1 overlaps substantially with Gabriel Garcia's 2026
*No Free Swap*: output-grounded layer-equivalence/protocol gaps are already
shown to change across Pythia training checkpoints. Lad et al. already use the
same static block-deletion/swapping and top-1 agreement family, while DTM is
mathematically equivalent to `1 - S` on identical positions. SteerCheck also
establishes that KL-matched intervention controls can retain protocol/direction
structure in an adjacent setting.

Therefore Candidate A cannot defensibly claim:

- discovery that layer redundancy changes during training;
- novelty of `S` or `Delta S` as a metric contribution;
- first evidence that intervention protocol matters after functional matching.

## What remains novel

No inspected work jointly establishes:

1. the frozen early-to-late block-bypass top-1 decline across independent
   Pythia pretraining runs;
2. bounded replication at 70M/160M and on WikiText-2 plus a HellaSwag-derived
   evaluation stream;
3. prospective raw-magnitude and KL/NLL matching between block bypass and
   norm-controlled activation noise;
4. a corrected, seed-stable family residual after functional-damage matching.

This is a **moderate controlled-replication and qualification delta**, not a
strong new-phenomenon claim.

## Closest paper

**Gabriel Garcia, “No Free Swap: Protocol-Dependent Layer Redundancy in
Transformers,” arXiv:2605.16234v2 (2026).** It is the TOP-1 novelty threat and
must be discussed in the Introduction.

## Strongest novelty dimension

Controlled replication scope: independent pretraining runs, two evaluation
streams, and prospective cross-intervention damage matching in one frozen
assay.

## Weakest novelty dimension

Metric novelty is **NONE**; broad phenomenon novelty is **WEAK**.

## Recommended revised thesis

Across independently pretrained small Pythia runs, top-1 robustness to
interior-block bypass declines from competent early to late checkpoints on two
corpora. This extends prior single-trajectory protocol-gap evidence. Under
prospective controls, raw displacement and matched KL/NLL damage do not make
block bypass and norm-controlled activation noise behaviorally interchangeable,
supporting an intervention-conditioned—not protocol-free—interpretation of
training fragility.

## Significance and risk

The result can inform how layer interventions are interpreted, but ICLR
significance is not guaranteed. The strongest reviewer attack is that this is a
careful replication/qualification of Garcia plus Lad et al., with small Pythia
models and no downstream endpoint. The paper should state that limitation
plainly rather than seek a broader mechanism claim.

## Resource account

- Scientific experiments: 0
- GPU time: 0
- Paid API cost: USD 0
- Local PDFs: 0
- Wall time to seal: approximately 24 minutes
- Conservative system-wide network-counter delta: 602.6 MB decimal; attribution
  to this ARC is unavailable and may include unrelated host traffic

## Decision-directed next step

Reposition the paper under the narrow thesis above. Do not run another
scientific ARC automatically. Begin Draft 0 only after the human accepts the
claim-level repositioning.
