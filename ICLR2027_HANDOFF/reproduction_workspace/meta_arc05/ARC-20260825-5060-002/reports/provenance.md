# Provenance and execution record

## Public source

- PolyPythias: Oskar van der Wal et al., *Stability and Outliers across Fifty
  Language Model Pre-Training Runs*, ICLR 2025, arXiv:2503.09543.
- Model repositories: `EleutherAI/pythia-{70,160}m-seed{1,2,3,4,5}`.
- Loaded model sizes: 70,426,624 parameters / 6 blocks and 162,322,944
  parameters / 12 blocks.
- The model cards describe `seed1` through `seed9` as different random seeds and
  separately expose `data-seed`/`weight-seed` variants. The combined seed runs
  used here vary both initialization and data order; these two sources of
  variation are not disentangled in this ARC.
- Every model supplies checkpoint branches through `step143000` (about 300B
  training tokens). The 50 evaluated branches resolved to 50 distinct commit
  hashes, stored in the raw JSON.

## Local environment

- GPU: NVIDIA GeForce RTX 5060 Laptop GPU, 7.96 GiB VRAM.
- Python 3.13.9.
- PyTorch 2.11.0+cu128; CUDA runtime 12.8.
- Transformers 4.56.2.
- Peak allocated CUDA memory: 0.99 GiB.
- No API calls and no paid services.

## Evaluation data

WikiText-2 training text cached by ARC-001. Each checkpoint uses exactly three
fixed resamples (selection seeds 11, 23, 37), each containing six sequences of
256 next-token positions. Evaluation resamples are controls and are never
counted as independent pretraining runs.

## Integrity checks

- 10 expected raw files found.
- 5 expected checkpoints in every file; 50 checkpoint records total.
- 50 unique resolved checkpoint commits.
- All intact NLL values finite.
- Tokenizer IDs were directly compared on fixed text for seed1, seed2 and the
  canonical Pythia tokenizer and were identical despite a tokenizer class-name
  metadata warning.
- One 160M seed2 step72k download ended with `IncompleteRead`. The run stopped;
  Hugging Face resumed the partial download, and that exact checkpoint was then
  evaluated. No checkpoint was skipped or substituted.
- Aggregate outputs regenerate deterministically from raw JSON.

## Raw SHA-256

```text
pythia-160m-seed1.json 055DE4B7133C339295BB8989618A2B3233FC00F0C5636E685AA99D242EF7AB13
pythia-160m-seed2.json 83C97045E8D6B1BE6345F8F954FFA5128E8772EBC322EA01614AC0C720AE207E
pythia-160m-seed3.json B300A161FD6AA29AD1BFA7E636624E2B626DD13168D4CFB16909E2303D296C39
pythia-160m-seed4.json 4BCDCF0ED647DA492023B18E0733AF159EC370E2998680E7EDDF35179477FC43
pythia-160m-seed5.json 89E193FB8E7E02502B7780E51ADA446572501184E29929C9E82F37A1C9CF4BA7
pythia-70m-seed1.json  664B866E54D8E6BF733ACAB28995E8011AB5198DF1CD7B9936F1486F06A42355
pythia-70m-seed2.json  4A85A9207172F9BB66F39FE4364F93E2957B5DAB979D88C8DDAB287DB98A592F
pythia-70m-seed3.json  71AAAE4A18534C71D37E27C7F963F00CA6F96A418E415AAB5A5D2004A7EA037A
pythia-70m-seed4.json  6B41369E59E86B34ADEF0960E83B051A21F772848CAF28E08264A1C131A950FF
pythia-70m-seed5.json  01BDC8CB27B039E760E87F993396E605B42A5177AF628B49F8EC387636743FA8
```
