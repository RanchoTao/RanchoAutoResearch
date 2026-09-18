# Recommended positioning

## Rejected framing

Do not frame the paper as discovering that Transformer layers become less
redundant over training. Garcia (2026) is a direct collision, and Lad et al.
already establish the underlying static layer-substitutability assay.

Do not frame `S`, `Delta S`, functional distance, or intervention-protocol
dependence as new concepts.

## Recommended thesis

**Intervention-conditioned training robustness.** Across independently
pretrained small Pythia runs, top-1 robustness to interior-block bypass declines
from competent early to late checkpoints on two corpora. Prospective controls
then show that raw displacement and matched KL/NLL damage do not make block
bypass and norm-controlled activation noise behaviorally interchangeable.

This is a replication-and-qualification thesis. It emphasizes what is unusually
well controlled, while keeping the claim inside the tested model family,
scales, corpora, and intervention definitions.

## Precise novelty delta

Prior work established static block deletion/swap robustness and next-token
agreement metrics, and recent work showed that output-grounded layer-
intervention gaps change across Pythia checkpoints. Candidate A adds
independent-pretraining-run replication of an early-to-late block-bypass
agreement decline on two corpora, plus prospective controls showing that raw
displacement and matched KL/NLL damage do not make block bypass and
norm-controlled activation noise behaviorally interchangeable.

## Claims safe for the paper

1. The frozen endpoint direction repeats across the reported independent Pythia
   runs, two small scales, and two evaluation streams.
2. Raw intervention magnitude is insufficient within the tested assay.
3. Matching KL/NLL damage does not eliminate all intervention-family structure.
4. The tested output-geometry features do not fully account for that residual.

## Claims to exclude

- a newly discovered general training law;
- universal layer specialization;
- functional-damage causality;
- downstream capability degradation;
- a fully identified internal mechanism;
- intervention-family invariance or generality beyond the two tested families.

## Closest-work placement

Garcia (2026) and Lad et al. belong in the Introduction, not only Related Work.
SteerCheck belongs in the Introduction when motivating matched functional
budgets. DTM, training-time PTQ fragility, and checkpoint fragility should be
used to delimit metric and training-dynamics novelty.
