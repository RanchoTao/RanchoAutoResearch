# Provenance and commands

## Frozen evidence sources

- Candidate A and ARC-003/004/005 definitions and raw artifacts were read from
  the existing repository research directories.
- Confirmatory anchors were copied deterministically from the frozen ARC-005
  block-deletion cells; all 150 eligible run-checkpoint-layer cells were used.
- Model checkpoints were read from the existing local Hugging Face cache.
- Evaluation data and token ordering were inherited unchanged from the frozen
  assay.

## Environment

- Repository environment: `.venv`, Python 3.13.9.
- PyTorch 2.11.0+cu128; CUDA runtime 12.8; Transformers 4.56.2.
- GPU: NVIDIA GeForce RTX 5060 Laptop GPU, 8,151 MiB reported VRAM.
- Analysis: system Python with Pandas, SciPy, and Matplotlib.

## Execution sequence

Commands were executed from the repository root. The exact configs named below
contain every search and evaluation parameter.

```powershell
.venv\Scripts\python.exe research\arc_20260826_5060_006\src\prepare_targets.py
.venv\Scripts\python.exe research\arc_20260826_5060_006\src\run_targeting.py --config research\arc_20260826_5060_006\configs\pilot.yaml
.venv\Scripts\python.exe research\arc_20260826_5060_006\src\run_targeting.py --config research\arc_20260826_5060_006\configs\pilot_refined.yaml
.venv\Scripts\python.exe research\arc_20260826_5060_006\src\run_targeting.py --config research\arc_20260826_5060_006\configs\confirmatory.yaml
python research\arc_20260826_5060_006\src\build_target_manifest.py
git commit -m "research: seal ARC-006 targets before reveal"
.venv\Scripts\python.exe research\arc_20260826_5060_006\src\run_reveal.py --config research\arc_20260826_5060_006\configs\reveal.yaml
python research\arc_20260826_5060_006\src\analyze_reveal.py
```

## Freeze commits

| Stage | Commit |
| --- | --- |
| Pilot preregistration | `49116b63b48f2a94e0ea519c5b485eb91ac84b39` |
| Confirmatory freeze | `8cc3c952a6eca994caea09b83d84165064a4bb24` |
| Target seal before reveal | `282b3663dd541aedffd4c4bca4e2b7683deb452c` |

`initial_freeze.sha256`, `confirmatory_freeze.sha256`, and
`sealed_manifest.sha256` preserve stage-specific hashes. The final integrity
manifest covers the complete ARC result. Raw reveal hashes are additionally
embedded in `results/inverse_targeting_summary.json`.

## Blinding audit

The targeting source and raw targeting outputs were searched for outcome fields.
The targeting routine contains no top-1 agreement calculation and its outputs
contain no `D_S`, agreement, or top-1-damage field. The reveal and analysis
scripts were written, compiled, hashed, and committed before any reveal run.

## Cost and external actions

No API, paid service, external compute, model download, upload, or external
communication was used. The project remained on the local RTX 5060.
