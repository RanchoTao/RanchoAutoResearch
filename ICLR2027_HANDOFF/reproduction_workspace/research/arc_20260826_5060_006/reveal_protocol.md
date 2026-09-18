# Reveal protocol

The following order is mandatory:

1. Complete every confirmatory targeting run without computing `D_S`.
2. Build `target_manifest.csv` with alpha/beta, achieved KL/NLL, errors, match
   class, failures, and provenance.
3. Run source-token, schema, coverage, balance, numerical-stability, and target
   key audits.
4. Freeze and git-commit the targeting raw data, diagnostics, manifest, scripts,
   configs, hashes, and confirmatory analysis/reveal code.
5. Record the commit hash in `sealed_manifest.sha256`.
6. Only after the commit exists, execute `src/run_reveal.py`.
7. Analyze all revealed outcomes with the already-frozen rules.

If `D_S`, agreement, top-1, `argmax`, or confidence outcomes appear in any
targeting artifact before step 4, the blind is broken and must be reported.

