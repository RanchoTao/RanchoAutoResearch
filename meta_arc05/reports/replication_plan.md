# Replication plan — written before model evaluation

## Paper/result being replicated

[The Remarkable Robustness of LLMs: Stages of Inference?](https://proceedings.neurips.cc/paper_files/paper/2025/hash/bcad07d4bfab51243efaa08b8ed475b3-Abstract-Conference.html),
Lad, Gurnee, and Tegmark, NeurIPS 2025.

Official source snapshot: `external/Remarkable-Robustness-of-LLMs` at commit
`4ee3f29ecf3e812a20af111f8888cb57085fdbae`.

## Original figure/table

The paper’s layer-wise ablation/swap experiment (main intervention figure; official
`model_intervention.py`). The official implementation zeros `attn_out` and
`mlp_out` for one block, compares normal/intervened logits and per-token loss, and
records the two top-1 tokens.

## Original conditions and numbers

- Models include `EleutherAI/pythia-410m-deduped` and larger Pythia/GPT-2/Qwen/Llama.
- Text source: `EleutherAI/the_pile_deduplicated`.
- Official script default: 1,388 streamed text samples.
- Reported headline: deletion/swapping retains **72–95%** of original top-1
  predictions without fine-tuning; deeper models are more robust.

## Our replication conditions

- Exact paper model: `EleutherAI/pythia-410m-deduped`, final checkpoint.
- Delete a block by bypassing it, operationally equivalent to zeroing its
  attention and MLP residual updates.
- Evaluate every layer on fixed next-token sequences.
- Three independently sampled text shards (five if inference remains cheap).
- Metrics: top-1 agreement with the intact model, excess NLL, KL divergence, and
  intact baseline NLL/perplexity.

## Known deviations

- WikiText-2 raw test text replaces The Pile because the current isolated venv
  lacks the official streaming dataset dependency. This is deliberately a domain
  transfer, not hidden.
- Hugging Face Transformers is used directly rather than TransformerLens 1.18,
  avoiding a Python-3.13 compatibility install. The causal intervention is the
  same residual-block bypass.
- We use contiguous token shards rather than 1,388 variable-length documents to
  bound compute and prevent long-document weighting.

## Baseline competence requirement

Intact-model NLL ≤4.5 (perplexity ≤90) on every shard and at least 20,000 total
scored next-token positions. Failure is `INVALID-HARNESS`, with at most two cheap
repairs.

## Replication PASS

1. mean top-1 agreement across the middle 50% of layers ≥0.72;
2. mean agreement in the first/last 12.5% is at least 0.03 lower than the middle;
3. both statements hold directionally in all three shards; and
4. middle-layer excess NLL is lower than boundary-layer excess NLL.

## Replication FAIL

Competence passes, but any of the four criteria fails. Stop as
`REPLICATION-FAIL`; do not mechanism-hunt.

## Maximum GPU budget

45 GPU minutes for replication. Boundary work is separately capped at 75 GPU
minutes, keeping the entire selected project below the exceptional three-hour cap.

