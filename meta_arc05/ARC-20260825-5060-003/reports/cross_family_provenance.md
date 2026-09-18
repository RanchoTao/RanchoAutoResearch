# Cross-family provenance and execution record

## Public trajectory

- Repository: `HuggingFaceTB/SmolLM2-360M-intermediate-checkpoints`.
- Official checkpoint card:
  https://huggingface.co/HuggingFaceTB/SmolLM2-360M-intermediate-checkpoints
- Official final model card:
  https://huggingface.co/HuggingFaceTB/SmolLM2-360M
- Training paper: Ben Allal et al., *SmolLM2: When Smol Goes Big —
  Data-Centric Training of a Small Language Model*, arXiv:2502.02737:
  https://arxiv.org/abs/2502.02737
- Public facts used in selection: checkpoints every 160,000 steps; global batch
  size 1,572,864 tokens; 360M member trained for 4T tokens with a single-stage
  high-quality mixture, GQA, Nanotron, BF16, and WSD with 20% decay.
- Loaded model: 361,821,120 parameters, 32 blocks.

## Immutable checkpoint identities

| Revision | Commit SHA | Training tokens |
|---|---|---:|
| `step-320000` | `24f9f6ba2ae2a79fe893df62646dffe67a794f50` | 503,316,480,000 |
| `step-800000` | `e1871f370b015aecd2a7bcdde726faf4e4778261` | 1,258,291,200,000 |
| `step-1280000` | `ed07699cbec92fa63564cd46abdf52e262080bc3` | 2,013,265,920,000 |
| `step-1920000` | `af134f51feb3a2bfcbc06b3e37f3337d0f3281ae` | 3,019,898,880,000 |
| `step-2560000` | `6587c7a7b6179794ee17a43d3e0376d560a49183` | 4,026,531,840,000 |

Each selected revision exposed a 723,674,912-byte `model.safetensors` file.
No model-size substitution or cross-run checkpoint mixing was used.

## Local environment

- Host GPU: NVIDIA GeForce RTX 5060 Laptop GPU, 8,151 MiB reported VRAM.
- Driver: 610.74.
- Python: 3.13.9.
- PyTorch: 2.11.0+cu128; bundled CUDA runtime 12.8.
- Transformers: 4.56.2.
- NumPy: 2.5.2; Matplotlib: 3.10.6; PyYAML: 6.0.3.
- Execution environment:
  `gap_mining/claim_evidence_execconfig_20260824/.venv`.
- Repository branch/commit during execution:
  `main` / `e2e23c93b4943fd21cc531deb09850d8fda55357`.
- Upstream remote: `https://github.com/aiming-lab/AutoResearchClaw.git`.
- Existing dirty-worktree changes were not reset, overwritten, or committed.
- API calls / paid services: none; cost USD 0.

## Evaluation data

- WikiText-2 text: reused unchanged from
  `meta_arc05/ARC-20260825-5060-001/data/wikitext2_train.txt`.
- HellaSwag validation source:
  `https://raw.githubusercontent.com/rowanz/hellaswag/master/data/hellaswag_val.jsonl`.
- HellaSwag rows: 10,042; bytes: 12,246,618.
- HellaSwag SHA-256:
  `0AA3B88843990F3F10A97B9575C94D7B71FB2205240BA04AE4884D9E9C992588`.
- Fixed HellaSwag sample: 256 rows without replacement, seed 20260825.
- The local scorer follows the public lm-evaluation-harness HellaSwag document
  preprocessing, adds the standard separating space to continuations, and
  scores continuation tokens only. Both raw-sum and token-length-normalized
  conditional log likelihood are stored per example.

## Exact commands

Run from the AutoResearchClaw repository root in PowerShell:

```powershell
$py = '.\gap_mining\claim_evidence_execconfig_20260824\.venv\Scripts\python.exe'
$arc = '.\meta_arc05\ARC-20260825-5060-003'

& $py "$arc\src\evaluate_hellaswag.py" `
  --config "$arc\configs\cross_family.yaml" `
  --revision step-2560000

& $py "$arc\src\run_cross_family.py" `
  --config "$arc\configs\cross_family.yaml"

'step-320000','step-800000','step-1280000','step-1920000','step-2560000' |
  ForEach-Object {
    & $py "$arc\src\evaluate_hellaswag.py" `
      --config "$arc\configs\cross_family.yaml" --revision $_
  }

& $py "$arc\src\aggregate_cross_family.py"
```

The valid commands above were run with `dtype: bfloat16`. The same full sweep
was initially attempted with FP16; its nonfinite results were moved to
`experiments/invalid_fp16/` before rerunning every valid evaluation from
scratch. See `reports/precision_incident.md`.

## Integrity and artifact hashes

```text
3EE80E8CF7E298689CA9DDB9112AFA4311AF90B7741C244A5B6438E09E588437  experiments/trajectory/raw_results.json
FFDE3D0DA07596240C5178710FFBC5ECB7A8047AB21C00B36A3D22A7F70E735C  experiments/invalid_fp16/trajectory_raw_results_fp16.json
788A766C01D6AB1CA4C1C544E7481577917AFFDED0E73318B723D443CBD044CA  experiments/competence/hellaswag-step-320000.json
7E71B6E6674A96BDB94A57CD69B6107C6E1A1027161832575CBDE8FD033B83AD  experiments/competence/hellaswag-step-800000.json
168D1C825A7931C3B7EC9A7AAA685B689EBDDCCA75814266ACC1C960BAA11831  experiments/competence/hellaswag-step-1280000.json
22B44FEA11A3001420364B5FF0F1C349CC1B4D408C3CE50396FF6F0482974207  experiments/competence/hellaswag-step-1920000.json
E177C3655FF555FF4B4992B6DAFD10B2126848B9F483398381187F525FD7F0EF  experiments/competence/hellaswag-step-2560000.json
0AA3B88843990F3F10A97B9575C94D7B71FB2205240BA04AE4884D9E9C992588  data/hellaswag_val.jsonl
DAFDEFDB524A93C553943A6094324EAE761FAEB96749C2DBCA46CA6375419C3A  results/cross_family_summary.json
C79498CA9ED53A6B67CF42115DDC64823A0E3F154470027F0491E8EDBD08C716  results/per_checkpoint_results.csv
6275B00D9CC8340AE0170533A692324C6396FB2B7597B276A1B936B21B30AE7F  figures/cross_family_trajectory.png
5492BDDF9D4E077C28692AA3432B1C6B15D6108933267F6AC49827624972927B  figures/competence_and_confidence.png
```

All five valid trajectory records and all five competence records identify
native BF16, the expected revision, a distinct resolved commit, 361,821,120
parameters, and finite primary/secondary measurements.

## Resource accounting

- Valid deletion trajectory: 92.618 seconds.
- Valid five-checkpoint HellaSwag evaluation: 80.952 seconds.
- Preserved invalid FP16 deletion attempt: 670.873 seconds.
- Preserved invalid FP16 HellaSwag attempt: 118.836 seconds.
- Total evaluator wall/GPU upper bound: 963.279 seconds (0.2676 hours).
- Peak allocated CUDA memory: 1,947,464,192 bytes (1.814 GiB).
- ARC artifact size before reports: 14,856,538 bytes.
- SmolLM2 intermediate-checkpoint cache footprint: 3,635,260,953 bytes
  (3.386 GiB).
- ARC creation to validated aggregate: 25.45 minutes.
