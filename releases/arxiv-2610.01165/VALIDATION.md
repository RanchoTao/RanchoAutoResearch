# Patch validation — 2026-10-07

Base: `e6bcfaf280022a8ac682157222e567ed4b9b58f5`. Tested in the existing Linux workspace, Python 3.12.14, exact direct display versions in `requirements-display.txt`. This was not a fresh environment installation.

- Cached display command: PASS; all four published display commands returned 0.
- 103 original ancillary entries: SHA-256 PASS, including the byte-identical restored NPZ.
- 1,759 legacy scientific files: SHA-256 PASS before and after generation.
- 101 numerical consistency checks: PASS.
- 11 generated table fragments: byte-identical to canonical arXiv v1 table fragments.
- 23 standalone panel PDFs plus dense Figures 1/11/12 and optional dense displays: generated; existing text/layout checks PASS. Original canonical figures are not overwritten; regenerated PDFs need not have identical metadata.
- Four boundary tests: PASS (tampered/missing inputs, manifest traversal, unsafe archive entries and duplicate archive paths).
- No existing scientific path changed in the patch; only the top-level README changes among previously tracked files.

[validation-receipt.json](validation-receipt.json) records the executed commands, package versions, output hashes and scope. Generated displays stay outside the repository. No inference, acquisition, statistical resampling, fitted-model refit, scientific hypothesis decision or legacy resealing command was run.

Fresh environment installation: **NOT_RUN**. Clean-room inference: **NOT_RUN**. Full offline model replay: **NOT_IMPLEMENTED**. Full transitive/GPU lock: **NOT_ESTABLISHED**. These original gaps are disclosed, not marked solved by cached display success.

Verification commands (repository root):

```bash
python reproduce.py --verify-only
python -m unittest discover -s tests -p test_cached_reproduction.py
python reproduce.py --output ../reproduced-arxiv-2610.01165
```

A new output directory is required on every execution. A failed attempt records FAIL when generation has begun. Hash or dependency failures stop before creating a display directory.
