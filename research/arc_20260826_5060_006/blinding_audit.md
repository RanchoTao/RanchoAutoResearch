# Blinding audit

## Before pilot

- `targets/pilot_targets.csv` and `targets/confirmatory_targets.csv` contain
  exactly target ID, run, checkpoint, progress, layer, target KL, and target NLL
  damage. Confirmatory values exactly reproduce ARC-005's retained anchor
  KL/NLL cells.
- `src/run_targeting.py` contains none of: `argmax`, `top1`, `agreement`,
  `confidence_bins`, `top1_damage`, or `top1_agreement`.
- Targeting output schema and raw pilot JSON contain no such field and no
  `D_S`/`Delta S` field.
- Targeting stdout exposes only stage, run/checkpoint, target count, match-class
  counts, runtime, peak allocation, and harness status.

## Pilot inspection boundary

Inspected: beta, KL, NLL damage, objective, relative/absolute errors, class,
boundary status, monotonicity, verification reproducibility, runtime, and
memory. Not inspected or generated: any new-family top-1 outcome.

## Required pre-reveal repeat

After confirmation, repeat the source-token and raw-schema audit, verify all
150 target keys, freeze the manifest and quality gate, hash every targeting raw
file, and commit before executing the separate reveal script.

## Confirmatory pre-reveal audit

- 150/150 unique targets completed; 15/15 checkpoint harnesses passed.
- Targeting source and all confirmatory raw JSON again contained none of the
  forbidden top-1/outcome fields.
- Sealed targeting classes: A=103, B=31, C=16; all prospective overall,
  run, checkpoint, layer, balance, and reproducibility gates passed.
- Zero beta-boundary solutions; all numeric targeting values were finite.
- `target_manifest.csv` and `match_diagnostics/targeting_quality.json` were
  generated before any reveal execution.
