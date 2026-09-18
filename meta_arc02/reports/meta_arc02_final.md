# META-ARC-02 final report

## Funnel

- Literature wedges: **30**, spanning optimization dynamics, data reuse,
  algorithmic/length generalization, representation geometry, distillation/TTA,
  and evaluation/RLVR.
- Candidate questions: **15**.
- Novelty RED: **4** (`C09`, `C12`, `C13`, `C14`).
- Reviewer-2 rejected: **4** (`C03`, `C08`, `C10`, `C15`).
- Compute-feasibility rejected: **2** (`C05`, `C11`).
- Survivors: **5** (`C01`, `C02`, `C06`, `C04`, `C07`).

## Final TOP-5

1. `C01` — Does temporal burstiness control repetition damage at a fixed complete
   training multiset and compute budget?
2. `C02` — Are parity-associative shortcuts a general preference for cheap
   quotient-group features?
3. `C06` — Can paired randomness across model scales reduce scaling-law
   extrapolation error per training run?
4. `C04` — Is latent-state coverage a better causal predictor of algorithmic
   length generalization than training length?
5. `C07` — Does demonstration diversity independently control the sign of
   test-time-training gains at fixed task alignment?

## MVP 1 — ARC-22

**KILL.** Across five seeds, massed-minus-spaced fresh NLL was +0.00835 ±
0.00072 on a Markov generator but -0.02180 ± 0.08623 on a held-out recurrence
generator. Early/middle/late controls showed that block position and recovery
time, not burstiness alone, generated the signal.

## MVP 2 — ARC-23

**INCONCLUSIVE, therefore KILL.** In order-12 and held-out order-24 group cohorts,
abelianization compression perfectly rank-ordered the quotient-first learning
gap. But it also almost perfectly rank-ordered exact-task failure (rho -0.949 and
-0.975); every non-abelian group failed the 95% mastery control, while OOD exact
accuracy was approximately chance and unrelated to gap (rho -0.095). The
experiment therefore does not isolate a quotient-shortcut mechanism.

## Final decision

**KILL.** Both permitted MVPs produced useful negative evidence but neither
survived its predefined controls. No candidate is locked for promotion, and no
paper-scale expansion should begin from this run.

## Resource accounting

- Real training runs: 105 (60 ARC-22 + 45 ARC-23).
- Sum of measured per-run GPU train/eval timers: **792.6 seconds (13.2 minutes)**.
- Peak allocated CUDA memory: **86,420,992 bytes (~82 MiB)**.
- End-to-end wall time: approximately **one hour**.
- Paid API cost: **USD 0**.

## Strongest negative evidence

The two most attractive laws each collapsed under the first decisive control:
duplicate burstiness under held-out generator/position controls, and quotient
compression under exact-task mastery controls. In ARC-23, a perfect replicated
rank correlation was specifically *not* accepted because the causal confound was
larger and the behavioral target remained at chance.

## Recommended action

Stop this META-ARC and preserve its artifacts. Do not promote ARC-22 or ARC-23.
If a future independent run revisits the quotient question, it must first create
matched-difficulty non-abelian tasks that all reach ≥95% ID accuracy; longer
training on the present benchmark would be post-hoc rescue rather than evidence.
