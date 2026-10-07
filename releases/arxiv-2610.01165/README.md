# arXiv:2610.01165 — public v1 release

**Persistent Depth Ordering amid Shifting Block-Bypass Responses in Language Model Pretraining**
Shengye Tao, Yinzhu Cheng, Haihua Xie. Submitted 2026-10-01, 06:43:19 UTC. 24 pages, 12 figures. Subjects: cs.LG, cs.CL. This is an arXiv preprint; no conference acceptance is asserted.

[Abstract](https://arxiv.org/abs/2610.01165) · [v1 PDF](https://arxiv.org/pdf/2610.01165v1) · [Public source](https://arxiv.org/src/2610.01165v1) · [Metadata](publication.json) · [Citation](citation.bib)

## One cached reproduction command

From the repository root, using Python 3.12 (tested: 3.12.14):

```bash
python -m venv ../arxiv-display-env
# Linux/macOS; on Windows use ..\arxiv-display-env\Scripts\python.exe
../arxiv-display-env/bin/python -m pip install -r requirements-display.txt
../arxiv-display-env/bin/python reproduce.py --output ../reproduced-arxiv-2610.01165
```

The output directory must not exist and must be outside the repository. The command never downloads model weights or corpora. It verifies the exact included public source archive and 1,759 pre-existing scientific files, extracts a disposable copy, verifies all 103 ancillary manifest entries, and runs only these existing public commands in order:

| Command, relative to the extracted source | Purpose | Exported output |
|---|---|---|
| `anc/source/analysis/make_tables.py` | Check saved summaries and format 11 tables; no resampling | `generated/tables/`, `validation/numerical_checks.json` |
| `anc/source/analysis/plot_figures.py` | Render standalone panels for Figures 2–10 | `generated/figures/`, `validation/figure_text_bounds.json` |
| `anc/source/dense/build_dense_figures.py` | Render Figures 11–12 and optional dense overview displays | `dense/`, `qa/` |
| `anc/source/overview/build_overview.py` | Compose Figure 1 using the saved empirical vector input | `generated/figures/fig1_dense.pdf`, `validation/overview_geometry.json` |

The runner checks that all 11 generated table files are byte-identical to canonical v1 tables, checks figure coverage, and verifies that cached scientific inputs and canonical assets in the disposable copy stay unchanged. Generated display hashes, logs, package versions and the exact scope go into `receipt.json`. Original repository files are read only, and the original freeze/preregistration/provenance records are preserved. The runner does not invoke `reanalyze_broad.py`, legacy resealing scripts, acquisition, model inference, bootstraps, regression fitting or hypothesis decisions. Table checks recompute simple descriptive quantities only to validate saved summaries.

For integrity checks alone (standard library, no display packages required):

```bash
python reproduce.py --verify-only
python -m unittest discover -s tests -p test_cached_reproduction.py
```

Exact direct display versions are pinned in `../../requirements-display.txt`. These are not a full transitive environment lock or a unified historical GPU lock. `--allow-version-mismatch` permits a diagnostic display run and records each mismatch. Missing or hash-mismatched caches fail; the runner does not infer substitutes. Python socket access is blocked in the four display processes and Hugging Face offline flags are set.

## Publication versus historical freeze

The final public v1 source archive is separate from the historical Candidate A/ICLR records. Its import and arXiv-expanded NPZ restoration are documented in [SOURCE_IMPORT.md](SOURCE_IMPORT.md). No old manuscript title, experiment, seal, provenance or preregistration is rewritten to pretend that it was the final publication. See `publication.json` for the historical freeze identity and the observed absence of advertised remote tags; no tag was recreated or moved.

## Central dependency and environment inventory

[dependencies.json](dependencies.json) consolidates 14 focal checkpoint/tokenizer revision references, 55 broad checkpoint labels across 11 panels, available source/context hashes, 70 historical raw checkpoint references, corpus hashes, excluded external inputs, and distinct historical inference environments. Broad immutable model SHAs and weight-file hashes that were not exported remain `null` with an unresolved status; today's mutable model heads are not substituted. The existing corpus and model records retain their original hash semantics.

The public v1 package omits model weights, benchmark text, focal raw token/boundary activations and acquisition implementation. Historical HellaSwag source JSONL is also absent from the old handoff, although its derived text is present. These do not block cached displays. They do block treating this as a complete offline inference capsule.

`VALIDATION.md` records only the checks actually performed for this patch. **Fresh environment installation, clean-room inference, and independent regeneration of saved uncertainty estimates: NOT_RUN.**
