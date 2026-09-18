# Blinding audit

## Permitted calibration information

The frozen cell universe is copied into `sanitized_targets.csv` with only:

- `target_id`
- `run_id`
- `step`
- `layer`
- `match_class`
- `selected_beta`
- `target_kl`
- `target_nll_damage`

The one-purpose sanitizer selects fields by frozen header positions and writes
only Class A rows. It never names, maps, logs, summarizes, ranks, or emits any
outcome field. After this copy is created, every ARC-009 pilot, solver,
calibration, analysis, and validation process reads only the sanitized copy and
the outcome-blind ARC-008 calibration files.

## Forbidden information

ARC-009 code must not open the corrected ARC-006R result table after
sanitization. It must not open ARC-007R/008 files containing corrected
residuals, reversals, flips, or confirmatory outcomes. No confirm phase exists
in the ARC-009 runner.

## Audit controls

1. Record SHA-256 of the source and sanitized copy.
2. Assert the sanitized header exactly equals the eight-field allowlist.
3. Scan all ARC-009 CSV/JSON/Markdown/log artifacts for forbidden outcome
   column names before finalization.
4. Assert no `confirm_seed*` or outcome-result artifact exists.
5. Stop with `BLINDING_FAILURE` if any forbidden outcome is loaded or emitted.

