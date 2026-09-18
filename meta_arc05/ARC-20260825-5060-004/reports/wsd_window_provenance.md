# WSD-window provenance and commands

## Authoritative sources

- Official intermediate-checkpoint card:
  https://huggingface.co/HuggingFaceTB/SmolLM2-360M-intermediate-checkpoints
  — checkpoint cadence 160,000 steps and global batch 1,572,864 tokens/step.
- Official paper: https://arxiv.org/html/2502.02737v1
  — Section 6 reports 4T tokens, a single-stage data mixture, GQA, and WSD with
  20% decay for SmolLM2-360M.
- Branch identities were retrieved directly from the official Hugging Face Git
  remote using `git ls-remote --heads` before preregistration.

The exact decay-start step is not directly named in a released config. Step
2,048,000 is the best-supported inference from 20% decay and public final step
2,560,000. This distinction is preserved in every artifact.

## New immutable checkpoints

| Revision | Commit | Step | Tokens | Progress |
|---|---|---:|---:|---:|
| `step-2080000` | `94c6cef4a924c2c2edbf0da3b9d082010c1f2629` | 2,080,000 | 3,271,557,120,000 | 81.25% |
| `step-2240000` | `8f5f6865f1d1d368a03a55a9a3a90b458ab7b513` | 2,240,000 | 3,523,215,360,000 | 87.50% |
| `step-2400000` | `94a4fe6b676f6a84980793194d34798aabd24e48` | 2,400,000 | 3,774,873,600,000 | 93.75% |

The full public branch/commit schedule, including the non-public inferred
boundary row, is in `wsd_checkpoint_table.csv`.

## Frozen reuse

Raw BF16 records at steps 320k, 800k, 1.28M, 1.92M, and 2.56M are copied
unchanged into the ARC-004 full trajectory from:

`meta_arc05/ARC-20260825-5060-003/experiments/trajectory/raw_results.json`.

Their HellaSwag competence records are read directly from ARC-003. Only the
three new checkpoint revisions were downloaded and inferred in ARC-004.

## Exact commands

Run from the AutoResearchClaw repository root in PowerShell:

```powershell
$env:HTTPS_PROXY = 'http://127.0.0.1:7897'
$env:HTTP_PROXY = 'http://127.0.0.1:7897'
$env:HF_HUB_DISABLE_XET = '1'
$env:HF_HUB_DOWNLOAD_TIMEOUT = '600'
$py = '.\gap_mining\claim_evidence_execconfig_20260824\.venv\Scripts\python.exe'
$arc = '.\meta_arc05\ARC-20260825-5060-004'

& $py "$arc\src\run_wsd_window.py" `
  --config "$arc\configs\wsd_window.yaml"

foreach ($revision in 'step-2080000','step-2240000','step-2400000') {
  & $py "$arc\src\evaluate_wsd_competence.py" `
    --config "$arc\configs\wsd_window.yaml" --revision $revision
}

& $py "$arc\src\aggregate_wsd_window.py"
```

The first step2.40M download ended with an `IncompleteRead` after 656,721,000
bytes, leaving 66,953,912 bytes. The run stopped without writing that
checkpoint. The identical command resumed the Hugging Face partial artifact,
resolved the preregistered commit, and evaluated it. Completed step2.08M and
step2.24M records were detected and not rerun.

## Environment

- Repository: `https://github.com/aiming-lab/AutoResearchClaw.git`.
- Repository branch/commit: `main` /
  `e2e23c93b4943fd21cc531deb09850d8fda55357`.
- GPU: NVIDIA GeForce RTX 5060 Laptop GPU, 8,151 MiB reported VRAM.
- Driver 610.74; Python 3.13.9; PyTorch 2.11.0+cu128; CUDA runtime 12.8;
  Transformers 4.56.2.
- Existing dirty-worktree changes were preserved.
- No API calls, purchases, external messages, or paid services.

## SHA-256

```text
358F1036D565A350C9B8AEB63125BC1607E2F77C11639228B4D8C08A180F7AF4  reports/wsd_window_preregistration.md
6E4FA77DA66AF5DA33B9F3C3AADAE274E4228111CCFAB831121B04BD25C442E4  configs/wsd_window.yaml
5523AEAB1C2D266A04F447724A4A6262B2F9BA324EEDAF4C39A960B57E9C4FE8  wsd_checkpoint_table.csv
4E7B226EB5E022223A5D153AC8248CB3C681116FAA9A6BA3167C629820B4473C  src/aggregate_wsd_window.py (frozen before inference)
393240EAECAC38167B3F445C0F1903F4564066673421321E2E118E4FEBC32FFD  experiments/trajectory/raw_results.json
6E6A327B491F728BAC92897B2B888E641EA8A9070039AF5505F8166AC54EDB4A  experiments/competence/hellaswag-step-2080000.json
DA7966B6747869E72615461D5FE9F867F7054AEFBDC13D9EA70C7D169C42321B  experiments/competence/hellaswag-step-2240000.json
81B567A8913FDB88DCF3FD7DB87F45D28D7E2D85F490AD0BE48CAE2DA4F6FC83  experiments/competence/hellaswag-step-2400000.json
0CAD5014E617340FCA5D80E378216632FE46F8189AF3505AA367554B7252D2CC  results/wsd_window_summary.json
5EEB90B1EB37BA4062822E4C4ED12A7B57E299635065EE81C9C66ED7A74E5512  results/wsd_checkpoint_metrics.csv
82B83AE383EB024859852E12A53A9FD6D530831F1719D7AD9B76D3AEF037E6AD  results/adjacent_intervals.csv
DF5F07515ADF842BC878D2AB4D3FB6E75ABED380D615AFB5B9A7463BDFF17689  figures/dense_wsd_trajectory.png
82601AFD1A83261714211EE1B57502EC89CC4FCD5F99D3C61625B82BDE794947  figures/piecewise_pre_vs_decay.png
381A2143B6937713C84B118718189A63D6AFCD541962C34C24DFAF900E42A6EE  figures/final_checkpoint_excluded.png
```

