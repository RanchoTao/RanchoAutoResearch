# Frozen protocol

## Reference chain

- Core definitions and statistical unit: ARC-003.
- Continuous residual-attenuation implementation and matched comparisons: ARC-004.
- Deterministic top-1 repair: ARC-006R.
- Paper-level selection and stop policy: ARC-010.

## Models and independent units

- Model family/scale: PolyPythias Pythia-160M only.
- Independent pretraining runs: seeds `1, 4, 6, 7, 8, 9`—the complete frozen
  ARC-004 run set, chosen before new outcomes.
- Pilot labels retained from ARC-004: `1, 4, 9`; confirmatory labels: `6, 7, 8`.
- Checkpoints: `step14000`, `step72000`, `step143000`.
- Primary endpoint contrast: step 143000 minus step 14000.
- Interior layers: all layers except the first and last; Pythia-160M layers 1–10.

ARC-003 used five trajectory checkpoints. ARC-011 retains the same early,
middle, and final anchors used by ARC-004 because only endpoints are primary and
the middle checkpoint is required for the frozen damage-matching comparison.
No continuous or monotonic training-law claim is tested.

## Samples and tokenization

- Tokenizer: the cached model tokenizer, `add_special_tokens=False`.
- Sequence construction: the unchanged stratified `choose_sequences` algorithm.
- Evaluation seeds: `11, 23, 37`.
- Six sequences per evaluation seed; sequence length 256 input/predicted-token
  positions plus one shifted target token.
- Batch size: 2.
- Total per checkpoint: 18 sequences and 4,608 predicted tokens, identical to
  the WikiText-2 assay.
- Exact token starts and slice hashes: `corpus_manifest.csv` and
  `data/selected_token_ids.json`.

## Intervention and outcome definitions

For each block output `b(x)`, residual attenuation uses
`b(x) - alpha * (b(x)-x)` at alpha `0.25, 0.50, 0.75, 1.00`. The alpha-1 path
returns `x` exactly and must pass the stored equivalence harness against literal
module-list deletion. Alpha 1 is the frozen core block-bypass intervention.

`S` is the mean token-level indicator that intact and intervened logits select
the same top-1 token, averaged over evaluation seeds and frozen interior layers.
`ΔS = S_step143000 - S_step14000`. The independent statistical unit is the
pretraining run, not token, layer, checkpoint, or evaluation resample.

- Top-1 rule: lowest token index among exact maximum logits, implemented by
  `torch.argmax` identically for intact and intervened outputs.
- Intact NLL: mean target-token cross entropy.
- NLL damage: intervened NLL minus intact NLL.
- KL: mean `KL(p_intact || p_intervened)`.
- Confidence: intact maximum softmax probability.
- Fixed confidence bins: `[0,.05), [.05,.1), [.1,.2), [.2,.4), [.4,1.01)`.
- Activation magnitude: ARC-004 local relative residual-change norm; secondary
  absolute RMS is retained but not a primary endpoint.

## Frozen matching

Magnitude-matched pairs require relative-magnitude ratio ≤1.10 and absolute KL
gap ≥0.03. Damage-matched pairs require KL gap ≤`max(.01, .10*mean_KL)` and NLL
gap ≤`max(.015, .10*mean_NLL)`, plus layer separation ≥3 or magnitude ratio
≥1.25. Greedy ordering, non-reuse, and tie ordering are copied from ARC-004.
No caliper may change after outcomes.

## Exclusion and competence

A run is excluded only for a missing/corrupt endpoint or intact NLL above 5.5 at
an endpoint. Technical failures remain in the run manifest. No unfavorable seed,
layer, sequence, or confidence bin may be removed.

