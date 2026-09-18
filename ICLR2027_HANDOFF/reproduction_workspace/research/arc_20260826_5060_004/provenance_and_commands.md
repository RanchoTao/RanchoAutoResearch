# Provenance and commands

## Inputs

- Prior frozen evaluator:
  `meta_arc05/ARC-20260825-5060-002/src/run_stability.py`.
- Prior primary raw data:
  ARC-002 seeds 1/4 and ARC-003 seeds 6/7/8/9.
- Models: cached immutable Hugging Face revisions of
  `EleutherAI/pythia-160m-seed{1,4,6,7,8,9}` at step14k, step72k, step143k.
- Corpus: cached ARC-001 WikiText-2 train text.
- Repository base commit: `e2e23c93b4943fd21cc531deb09850d8fda55357`.
- Preregistration and source hashes: `preregistration_manifest.sha256` and
  `execution_manifest.sha256`.

No checkpoint was downloaded, changed, or duplicated. Model loading used
`HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1`.

## Formal inference

```powershell
$env:HF_HUB_OFFLINE='1'
$env:TRANSFORMERS_OFFLINE='1'

foreach ($seed in 1,4,9) {
  .venv\Scripts\python.exe research/arc_20260826_5060_004/src/run_mechanism.py `
    --config research/arc_20260826_5060_004/configs/mechanism.yaml `
    --stage pilot --run-id $seed
}

python research/arc_20260826_5060_004/src/analyze_mechanism.py --mode feasibility

foreach ($seed in 6,7,8) {
  .venv\Scripts\python.exe research/arc_20260826_5060_004/src/run_mechanism.py `
    --config research/arc_20260826_5060_004/configs/mechanism.yaml `
    --stage confirmatory --run-id $seed
}
```

Only the feasibility JSON—pair counts and balance—was inspected before the
confirmatory runs. Hypothesis-direction results were unsealed afterward.

## Deterministic analysis and figure regeneration

```powershell
python research/arc_20260826_5060_004/src/analyze_mechanism.py --mode final
```

The project venv is used for CUDA inference. The system Python scientific stack
(pandas 2.3.3, scipy 1.16.3, matplotlib 3.10.7) is used for CPU aggregation and
figures. API cost is zero.

## Raw integrity

Raw SHA-256 values are embedded in `results/mechanism_summary.json`. The active
alpha endpoint was independently compared with 540 retained old assay cells;
top-1, NLL-damage, and KL maximum differences were all zero.

