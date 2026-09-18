# External trajectory selection

Frozen before downloading model weights or inspecting cross-family deletion
results.

## Selected trajectory

`HuggingFaceTB/SmolLM2-360M-intermediate-checkpoints`.

This is a legitimate external trajectory because all selected revisions are
checkpoints of the same 360M-parameter run, not different parameter scales. The
model is a 32-block Llama-style decoder trained with Nanotron on a SmolLM2 data
mixture, independent of Pythia's GPT-NeoX architecture and Pile recipe. The
official repository releases a checkpoint every 160,000 steps and gives a
global batch size of 1,572,864 tokens, allowing exact token-progress mapping.

Selected immutable branches:

| Revision | Commit | Tokens | Normalized progress |
|---|---|---:|---:|
| step-320000 | 24f9f6ba2ae2a79fe893df62646dffe67a794f50 | 503,316,480,000 | 0.125 |
| step-800000 | e1871f370b015aecd2a7bcdde726faf4e4778261 | 1,258,291,200,000 | 0.3125 |
| step-1280000 | ed07699cbec92fa63564cd46abdf52e262080bc3 | 2,013,265,920,000 | 0.5 |
| step-1920000 | af134f51feb3a2bfcbc06b3e37f3337d0f3281ae | 3,019,898,880,000 | 0.75 |
| step-2560000 | 6587c7a7b6179794ee17a43d3e0376d560a49183 | 4,026,531,840,000 | 1.0 |

Each branch exposes a 723,674,912-byte `model.safetensors` file and matching
tokenizer/config files.

## Rejected alternatives

- OLMo-1B has an excellent public trajectory but is approximately 1B+ and uses
  a larger hidden state; it is scientifically valid but less compute-efficient.
- TinyLlama-1.1B has a valid Llama-family trajectory but is larger and would
  make the 30-layer intervention sweep substantially more expensive.
- Final-only small models were rejected because different model sizes cannot
  serve as early/late training checkpoints.

## Minimal unavoidable adaptation

The block container changes from Pythia's `model.gpt_neox.layers` to SmolLM2's
`model.model.layers`. The intervention remains module-list bypass of exactly one
block. The tokenizer necessarily changes, so fixed seeds select positions from
the same WikiText-2 text after SmolLM2 tokenization; this is documented rather
than presented as token-identical evaluation.

