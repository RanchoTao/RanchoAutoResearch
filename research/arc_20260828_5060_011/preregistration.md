# Preregistration

This file is frozen before any HellaSwag Candidate A model outcome is computed.
Its sealing commit is recorded in `preregistration_commit.txt`; post-outcome
changes, if any, must go only to `posthoc_notes.md`.

## Question and selected corpus

Does Candidate A replicate when the evaluation corpus changes from WikiText-2
to locally cached HellaSwag validation correct continuations while the
Pythia-160M model, run set, checkpoints, intervention, samples per checkpoint,
metrics, matching, and statistical unit remain frozen?

- Source path: `meta_arc05/ARC-20260825-5060-003/data/hellaswag_val.jsonl`
- Source SHA-256: `0AA3B88843990F3F10A97B9575C94D7B71FB2205240BA04AE4884D9E9C992588`
- Derived SHA-256: `EF75B67A0F3A316B6D465295E2DD58314738FD0E38BCF01790DBA7022C35468E`
- Source records: 10,042; derived tokenizer tokens: 860,324.
- Deterministic transformation: `ctx + " " + endings[label]`, records joined by
  two newlines; no outcome-based filtering.

## Frozen execution

- Runs: `1, 4, 6, 7, 8, 9`.
- Checkpoints: 14k, 72k, 143k; primary contrast 143k minus 14k.
- Evaluation seeds: 11, 23, 37; six 256-token sequences each.
- Layers 1–10; alphas `.25, .50, .75, 1.00`; batch size 2.
- Primary core endpoint: alpha-1 `ΔS`, averaged within run over layers and
  evaluation seeds.
- Secondary endpoints: change in NLL damage, change in KL, intact NLL and
  confidence, magnitude-matched contrast, damage-matched contrast, and fixed-bin
  confidence control.
- Statistical uncertainty: 100,000 run-level bootstrap resamples, seed 20260828.
- Effect-size ratio: absolute new-corpus mean ΔS divided by the stored nine-run
  WikiText-2 mean; its interval bootstraps the two run sets independently. It is
  descriptive and not an equality gate.

## Frozen primary criteria

### Core replication pass

All must hold:

1. at least five of six eligible independent runs have `ΔS < 0`;
2. run-bootstrap 95% CI for mean ΔS is wholly below zero;
3. every leave-one-run-out mean ΔS is below zero;
4. at least five of six runs have negative ΔS in at least two of three fixed
   evaluation resamples;
5. at least five eligible runs pass the frozen intact-NLL competence gate.

### Functional-damage alignment pass

- Magnitude-matched contrast: at least five of six run medians are positive and
  its run-bootstrap 95% CI is wholly above zero.
- Damage-matched raw-magnitude alternative is weakened if its run-bootstrap CI
  includes zero **or** its absolute mean run-median contrast is less than half
  the magnitude-matched functional-damage contrast.
- Original matching calipers are immutable. A matching shortfall is reported,
  not rescued.

### Confidence-control pass

- At least three frozen confidence bins are eligible with ≥100 early and late
  observations per run-bin.
- At least 75% of eligible run-bin ΔS values are negative.
- Mean run-bin ΔS is negative and the run-bootstrap CI over per-run mean bin
  effects is wholly below zero.

## Verdict mapping

- `CORPUS-GO`: core, functional-damage, and confidence criteria all pass; assay
  integrity passes; no single seed drives the result.
- `CORPUS-PARTIAL`: the core criteria pass, but functional-damage or confidence
  structure materially weakens/fails, or an interpretable corpus boundary is
  required.
- `CORPUS-NO`: the core direction/CI criteria fail in an otherwise comparable
  assay.
- `CORPUS-NONCOMPARABLE`: fewer than five competent runs, fewer than three
  usable confidence bins across the run set, insufficient frozen samples, or a
  material regime mismatch prevents the primary comparison.
- `ASSAY-INTEGRITY-FAILURE`: deterministic top-1, alpha endpoint equivalence,
  tokenizer, checkpoint, sample manifest, or statistical unit cannot be held.
- `011-INCOMPLETE`: the absolute 60-minute/resource limit is reached.

The 0.05 magnitude threshold from earlier discovery is not a cross-corpus gate;
numerical equality is not required. A small but stable effect can be PARTIAL if
control structure changes materially.

## Missing data and stopping

Raw output is checkpoint-resumable. Missing/OOM/corrupt runs are retained in
`run_manifest.csv` with technical evidence. Stop before 60 minutes, any network
download, package change, model-cache miss, or hardware escalation. Do not run
the optional second intervention family or any mechanism branch.

