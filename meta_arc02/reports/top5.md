# META-ARC-02 TOP-5

Scores are 1–5. `Priority` is the requested product divided by estimated decisive
MVP hours; it is a guardrail, not the final ranking criterion.

| Rank | ID | N | I | F | R | C | G | P | T (h) | Priority |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | C01 | 4 | 4 | 5 | 5 | 5 | 4 | 4 | 0.5 | 32,000 |
| 2 | C02 | 4 | 5 | 4 | 4 | 4 | 5 | 5 | 2.0 | 16,000 |
| 3 | C06 | 3 | 3 | 5 | 5 | 5 | 4 | 3 | 0.5 | 13,500 |
| 4 | C04 | 3 | 4 | 5 | 5 | 5 | 4 | 4 | 1.0 | 12,000 |
| 5 | C07 | 3 | 4 | 4 | 4 | 4 | 4 | 4 | 1.5 | 4,096 |

## 1. C01 — duplicate burstiness

1. **Question:** Does temporal burstiness control repetition damage when the
   complete training multiset and compute are fixed?
2. **Strongest novelty evidence:** 2026 repetition laws sweep repeat count and
   fraction; no direct fixed-multiset spacing experiment was found.
3. **Biggest collision risk:** generic SGD order/curriculum and contamination
   recency results could make the result seem expected.
4. **Exact MVP:** two exact synthetic sequence generators; one tiny Transformer;
   clean, random-duplicate, evenly spaced, massed-early, massed-middle, and
   massed-late schedules; five seeds; constant LR; same batches as a multiset.
5. **GO threshold:** massed versus evenly spaced changes fresh validation loss by
   at least 0.5 pooled SD in the same direction in ≥4/5 seeds on both generators,
   and the average of early/middle/late massed schedules preserves the effect.
6. **KILL threshold:** effect <0.2 pooled SD, changes sign across generators, or is
   explained solely by massed block position.
7. **Path:** MVP → TinyStories/character LM at 10–30M → proxy-size scaling and
   naturally duplicated corpus audit → repetition-schedule scaling law.
8. **Promoted compute:** roughly 20–50 GPU-hours, dominated by 10–100M-token
   natural-language proxy runs.

## 2. C02 — quotient shortcuts in state tracking

1. **Question:** Is the parity-associative mechanism a special case of a general
   preference for low-complexity quotient-group features?
2. **Strongest novelty evidence:** state-tracking work isolates parity in `S_n`,
   while coset work studies grokked multiplication; no cross-group quotient law
   was found.
3. **Biggest collision risk:** group difficulty, commutativity, and output-space
   size can masquerade as quotient effects.
4. **Exact MVP:** matched-order finite groups; train product-sequence Transformers;
   measure exact and quotient accuracy at seen/held-out lengths plus quotient
   linear probes; reserve one group family as held out.
5. **GO threshold:** quotient decodability predicts exact OOD deficit across
   within-order pairs, ≥3 seeds, and held-out family, beyond train accuracy/order.
6. **KILL threshold:** association vanishes within order or reverses in held-out
   family.
7. **Path:** MVP → reproduce full permutation-state task → causal suppression of
   quotient feature → natural state-tracking code/text tasks.
8. **Promoted compute:** 30–80 GPU-hours including mechanism validation.

## 3. C06 — paired-seed scaling experiments

1. **Question:** Can cross-scale common-random-number pairing reduce scaling-law
   extrapolation error per training run?
2. **Strongest novelty evidence:** ICML 2025 emphasizes seed allocation but does
   not establish cross-scale coupling as an experimental-design variable.
3. **Biggest collision risk:** widths cannot share an exactly equivalent
   initialization, making “paired” ambiguous.
4. **Exact MVP:** nested-width MLP/Transformer initialization, shared data streams,
   independent control, repeated subsampling, held-out largest scale; two
   generators.
5. **GO threshold:** paired design reduces median held-out log-loss prediction
   error ≥25% and improves 90% interval coverage in both generators.
6. **KILL threshold:** <10% improvement or poor coverage in either generator.
7. **Path:** MVP → standard small LM suite → retrospective public checkpoint
   analysis → recommended scaling-law experimental protocol.
8. **Promoted compute:** 10–30 GPU-hours.

## 4. C04 — latent-state coverage law

1. **Question:** Is latent-state coverage a better causal predictor of algorithmic
   length generalization than training length?
2. **Strongest novelty evidence:** coverage interventions exist for recurrent
   models, but a factorial Transformer/GRU comparison was not found.
3. **Biggest collision risk:** no-op loops and start-state mixtures change token
   distributions or effective difficulty.
4. **Exact MVP:** two automata families, 2×2 length/coverage design, Transformer
   and GRU, five seeds, token-frequency-matched no-op controls.
5. **GO threshold:** coverage predicts held-out accuracy after length matching in
   both architectures and held-out automaton family, ≥0.5 pooled SD.
6. **KILL threshold:** only recurrent models respond, or effect disappears under
   token-frequency matching.
7. **Path:** MVP → broader automata → state-space models → program execution and
   real code state tracking.
8. **Promoted compute:** 20–60 GPU-hours.

## 5. C07 — TTT alignment × diversity boundary

1. **Question:** Does demonstration diversity independently determine when
   test-time training helps or hurts at a fixed pretrain-target alignment?
2. **Strongest novelty evidence:** current theory quantifies alignment and
   empirical work shows gains, but a nonlinear factorial boundary is missing.
3. **Biggest collision risk:** diversity merely rescales or conditions the
   adaptation gradient.
4. **Exact MVP:** tiny in-context regression Transformer; cross target-subspace
   angle and demonstration covariance rank; one normalized test-time gradient;
   held-out nonlinear teacher.
5. **GO threshold:** a replicated alignment×diversity interaction remains after
   gradient-norm/Hessian controls and predicts sign of TTT gain held out.
6. **KILL threshold:** normalized update removes the interaction or nonlinear
   held-out teacher reverses it.
7. **Path:** MVP → TabPFN/small pretrained LM → few-shot real tasks → adaptive TTT
   safety criterion.
8. **Promoted compute:** 30–80 GPU-hours.

## Selection

C01 is selected because it has the best information-per-engineering-hour ratio,
uses no pretrained model or paid API, admits exact budget matching, and has an
informative null: a null would show that repeat-count scaling laws need not model
within-run spacing in the tested regime.

