# ARC-20260828-5060-011 — Executive summary

## Final verdict: CORPUS-GO

Candidate A and its key control structure reproduce on one distinct local
evaluation corpus under the frozen Pythia-160M protocol. The paper can now claim
that the phenomenon is **not specific to WikiText-2**, while remaining bounded
to two English corpora, small Pythia models, one tokenizer, and the operational
top-1 substitutability assay.

## Primary evidence

- HellaSwag ΔS: mean **-0.079264**, median -0.081391.
- Run-bootstrap 95% CI: **[-0.088509, -0.067672]**.
- Independent runs: **6/6 negative**; fixed evaluation resamples: 18/18 negative.
- No exclusions; every leave-one-run-out mean remains negative.
- Absolute effect-size ratio versus the nine-run WikiText-2 mean: **0.766**,
  95% CI [0.645, 0.880]. The effect is smaller, not absent.
- Fixed-confidence control: **30/30 negative**, mean -0.089488,
  CI [-0.100292, -0.074097].
- Magnitude-matched functional-damage contrast: **+0.040437**, 6/6 positive,
  CI [+0.037634, +0.043710].
- Damage-matched magnitude residual: **+0.002984**, CI
  [+0.001555, +0.004485]. Raw magnitude remains a small contributor on
  HellaSwag and must not be described as zero.

## Integrity and cost

- Pre-outcome corpus/protocol commit:
  `f0f2a329caf6e1c113ef38e938cb69ffb6935dee`.
- Six raw runs and 18 checkpoints complete; all endpoint and canonical tie
  harnesses pass.
- Independent recalculation, raw hashes, frozen matching, confidence rows, and
  four figures: PASS.
- Downloads, network use by ARC scripts, APIs, and external compute: zero.
- Recorded checkpoint runtime: 138.18 seconds; peak allocated VRAM 0.99 GiB.

## Paper decision

The empirical status advances from ARC-010 `PAPER-BORDERLINE` to `PAPER-GO`.
No further major experiment is required before drafting. Novelty is not yet
verified: the primary-source literature audit remains mandatory.

## One next action

Freeze the empirical story and begin manuscript drafting. Do not automatically
run another corpus, scale, intervention, or mechanism ARC.
