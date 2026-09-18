# Assay integrity

## Frozen-contract checks

| Check | Result |
|---|---|
| Models/run IDs | PASS: Pythia-160M seeds 1, 4, 6, 7, 8, 9 only |
| Checkpoints | PASS: 14k, 72k, 143k in every run |
| Tokenizer | PASS: cached GPTNeoX tokenizer, no special tokens |
| Sample manifest | PASS: 18 deterministic slices; token hashes verified before every run |
| Sequence/batch size | PASS: 6×256 per evaluation seed; batch 2 |
| Layers/alphas | PASS: layers 1–10; .25/.50/.75/1.0 |
| Alpha endpoints | PASS at every checkpoint: alpha0 equals intact; alpha1 equals literal deletion |
| Order/state leakage | PASS at every checkpoint |
| Top-1 tie rule | PASS: identical `torch.argmax`; synthetic exact tie returns lowest index 1 |
| Corpus/hash | PASS and identical in all six raw files |
| Statistical unit | PASS: independent pretraining run |
| Result-dependent filtering | None |
| Matching calipers | Independently checked: 161 A and 194 B pairs, zero violations/reuse |
| Network/model retrieval | Offline + `local_files_only=True`; zero downloads |

The ARC-006 inconsistency is not reproduced: intact and intervened outputs use
the same canonical top-1 implementation. `results/independent_validation.json`
independently recomputes every core ΔS, aggregate mean/median/CI, raw hashes,
matching validity, confidence signs, and figure existence.

## Code provenance

The residual-attenuation class, parameter/magnitude definitions, layer
replacement, and endpoint equivalence harness are imported from the frozen
ARC-004 local source. ARC-011 implements only the corpus input and canonical
top-1 evaluation path. DeepSeek/API strategy assistance was unavailable by
design because ARC-011's hard policy forbids all external API/network calls;
execution is logged as a policy-required Codex-only fallback.
