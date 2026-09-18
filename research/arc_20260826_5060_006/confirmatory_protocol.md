# Confirmatory targeting protocol freeze

Frozen after the outcome-blinded pilot and before any confirmatory targeting
forward pass.

## Target set and evaluator

- All 150 targets: runs 2/3/5/6/8 x checkpoints 14k/72k/143k x layers 1-10.
- Target metrics: retained block-deletion KL and NLL damage, averaged over
  evaluation selections 11/23/37.
- Noise directions: 101/202/303, averaged using the exact ARC-005 generator.
- Same WikiText-2 sequences, tokenizer, batch size, model revisions, precision,
  and intervention implementation as ARC-005.
- No `D_S` computation or logging during targeting.

## Frozen search

- Range and grid: `[0,.25,.50,.75,1.00,1.25]`.
- Objective: the equally weighted squared 10%-caliper-normalized KL/NLL error
  in `preregistration.md`.
- Bracket: adjacent fixed-grid points around the minimum grid objective.
- Golden refinements: 14; stop if bracket width <=0.0005.
- Tie: smaller beta.
- Re-evaluate the selected beta in an independent forward traversal before
  assigning its class.
- No range expansion, retargeting, or cell-specific objective changes.

## Match classes

- Class A: both relative 5% tolerances with absolute floors 0.005 KL and
  0.0075 NLL.
- Class B: not A, but both original relative 10% tolerances with floors 0.01 KL
  and 0.015 NLL.
- Class C: all other finite solutions.

Primary outcome analysis uses A only; A+B is sensitivity; C is excluded from
residual estimation but retained as targeting failure evidence.

## Prospective quality gate

Adequate identification requires all of:

1. at least 70/150 Class-A targets;
2. at least 113/150 Class-A+B targets;
3. at least 8 Class A and 20 A+B in every run (30 possible);
4. at least 30 A+B in every checkpoint (50 possible);
5. at least 2 Class A and 8 A+B at every layer index (15 possible);
6. zero duplicate/missing target IDs, all harnesses pass, all retained metrics
   finite, and selected beta verifies reproducibly;
7. median Class-A relative KL and NLL errors each <=5%.

Failure of any gate yields `TARGETING-NONIDENTIFIABLE` before inspecting the
revealed residual. These thresholds exceed ARC-005's 26/150 post-hoc coverage
and were selected from the 50% A / 87.5% A+B blinded pilot result.

## Reveal and analysis

Target raw data, Class labels, diagnostics, target manifest, frozen reveal and
analysis code, and SHA-256 hashes must be committed before reveal. Primary
residual, equivalence, shrinkage, interaction, heterogeneity, and final verdict
rules remain exactly as preregistered. No failed target or unfavorable run may
be removed after reveal.

