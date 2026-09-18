# Reproduction guide

## Scope and current limitation

The package preserves exact code, configs, raw/processed results, data derivatives, and commands. It does **not** include Hugging Face model weights/caches. The historical pipeline also used split GPU and CPU environments. Therefore aggregation/figures and paper build are reproducible immediately; fresh GPU inference requires public checkpoint retrieval and a cleaned environment.

For scripts with relative imports, use `reproduction_workspace/`, which preserves the original directory layout. Run all commands from that directory.

## 1. Environment installation

Historical Windows/Python versions are recorded in `ENVIRONMENT.md`. A practical reconstruction is:

```powershell
cd ICLR2027_HANDOFF\reproduction_workspace
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r ..\requirements.txt
```

`requirements.txt` is a reconstructed unified environment, not a byte-for-byte historical lock. For maximum fidelity, see `requirements-gpu.txt` and `requirements-analysis.txt` and keep inference/analysis environments separate.

## 2. Data preparation

WikiText-2 is already present at:

`meta_arc05/ARC-20260825-5060-001/data/wikitext2_train.txt`

ARC-011 derived HellaSwag files are already present at:

`research/arc_20260828_5060_011/data/`

Exact selected tokens and corpus hashes should be checked against `corpus_manifest.csv`, `corpus_profile.json`, and `local_corpus_audit.md`. The original `hellaswag_val.jsonl` is missing, so do not rerun `prepare_corpus.py` until the public source is reacquired and its frozen SHA-256 `0AA3B88843990F3F10A97B9575C94D7B71FB2205240BA04AE4884D9E9C992588` is verified.

## 3. Model preparation

Required public repositories include `EleutherAI/pythia-160m-seed1` through `seed9` and `pythia-70m-seed1` through `seed5`, at the revisions in the frozen configs. Model weights are not packaged.

The actual resilient 160M prefetcher is preserved at `meta_arc05/ARC-20260826-5060-003/src/prefetch_weights.py`. Example used pattern:

```powershell
.\.venv\Scripts\python.exe meta_arc05\ARC-20260826-5060-003\src\prefetch_weights.py --seed 6 --steps 14000 36000 72000 107000 143000
```

It fetches `pytorch_model.bin` with byte/range checks. Config/tokenizer files must also be available in the Hugging Face cache. Do not enable offline mode until all exact revisions and tokenizer/config files resolve successfully. The package does not contain a fully tested fresh-machine downloader for every 70M/160M artifact; this is the principal end-to-end reproduction blocker.

## 4. Core independent-run inference

After cache preparation:

```powershell
$env:HF_HUB_OFFLINE='1'
$env:TRANSFORMERS_OFFLINE='1'

foreach ($seed in 6,7,8) {
  .\.venv\Scripts\python.exe meta_arc05\ARC-20260826-5060-003\src\run_independent.py `
    --config meta_arc05\ARC-20260826-5060-003\configs\independent_runs.yaml `
    --scale 160 --run-id $seed
}

.\.venv\Scripts\python.exe meta_arc05\ARC-20260826-5060-003\src\analyze_independent.py --mode discovery

.\.venv\Scripts\python.exe meta_arc05\ARC-20260826-5060-003\src\run_independent.py `
  --config meta_arc05\ARC-20260826-5060-003\configs\independent_runs.yaml `
  --scale 160 --run-id 9

.\.venv\Scripts\python.exe meta_arc05\ARC-20260826-5060-003\src\analyze_independent.py --mode final
```

Seed 9 was historically held out before its weights were inspected. A new reproduction verifies, rather than recreates, that prospective status.

## 5. Matched attenuation mechanism experiment

```powershell
foreach ($seed in 1,4,9) {
  .\.venv\Scripts\python.exe research\arc_20260826_5060_004\src\run_mechanism.py `
    --config research\arc_20260826_5060_004\configs\mechanism.yaml `
    --stage pilot --run-id $seed
}

python research\arc_20260826_5060_004\src\analyze_mechanism.py --mode feasibility

foreach ($seed in 6,7,8) {
  .\.venv\Scripts\python.exe research\arc_20260826_5060_004\src\run_mechanism.py `
    --config research\arc_20260826_5060_004\configs\mechanism.yaml `
    --stage confirmatory --run-id $seed
}

python research\arc_20260826_5060_004\src\analyze_mechanism.py --mode final
```

## 6. Activation-noise family

```powershell
$runner='research\arc_20260826_5060_005\src\run_activation_noise.py'
$config='research\arc_20260826_5060_005\configs\confirmatory.yaml'
foreach($runId in 2,3,5,6,8){
  .\.venv\Scripts\python.exe $runner --config $config --run-id $runId
}
python research\arc_20260826_5060_005\src\analyze_confirmatory.py --mode final
```

## 7. Correct matching outcome and geometry

Never analyze original ARC-006 outcomes. Regenerate the corrected outcome and geometry from preserved artifacts:

```powershell
python research\arc_20260827_5060_006R\src\reseal_arc006.py
python research\arc_20260827_5060_007R\src\prepare_geometry_blind.py
python research\arc_20260827_5060_007R\src\analyze_geometry.py
```

## 8. Cross-corpus experiment

Use the preserved derived text and selected-token manifest; do not rerun corpus preparation unless the missing source JSONL is restored.

```powershell
foreach($runId in 1,4,6,7,8,9){
  $stage = if($runId -in 1,4,9){'pilot'}else{'confirmatory'}
  .\.venv\Scripts\python.exe research\arc_20260828_5060_011\src\run_cross_corpus.py `
    --config research\arc_20260828_5060_011\configs\cross_corpus.yaml `
    --run-id $runId --stage $stage
}

python research\arc_20260828_5060_011\src\analyze_cross_corpus.py
python research\arc_20260828_5060_011\src\validate_results.py
```

## 9. Aggregation and plotting without GPU reruns

All raw/processed outputs are already preserved. The `analyze_*.py`, `reseal_arc006.py`, and geometry/validation scripts regenerate summary JSON/CSV and figures deterministically from those files. Run them in ARC order: 003, 004, 005, 006R, 007R, 011. Compare SHA-256/integrity files in each ARC.

## 10. Paper build

From `ICLR2027_HANDOFF/paper/current`:

```powershell
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

The frozen source previously passed a clean extracted pdfLaTeX/BibTeX build with zero undefined references/citations and zero overfull boxes. The expected PDF SHA-256 is `C4157787DE4BE436E94AE66888135C862C1AAD93987C7D86655BE86CD7999421`.
