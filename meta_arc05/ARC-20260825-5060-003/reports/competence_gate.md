# Downstream competence gate

Evaluated before any cross-family deletion result was produced.

## Result: PASS

- Model: `HuggingFaceTB/SmolLM2-360M-intermediate-checkpoints`
- Revision: `step-2560000`
- Commit: `6587c7a7b6179794ee17a43d3e0376d560a49183`
- HellaSwag validation examples: 256, fixed sample seed 20260825.
- Evaluation dtype: native BF16.
- Length-normalized accuracy: **0.5508**, bootstrap 95% CI [0.4883, 0.6094].
- Raw conditional-log-likelihood accuracy: **0.4180**, bootstrap 95% CI
  [0.3594, 0.4805].
- Normalized prediction counts for labels 0–3: 65, 56, 67, 68.
- Distinct predicted labels: 4; maximum label fraction: 0.2656.
- Truncated choices: 0/1024.

All preregistered gates pass: normalized accuracy >=0.40, raw accuracy >=0.30,
at least three labels, and maximum label fraction <=0.60. The normalized score
is also close to the final base model's official 54.5 HellaSwag result, which
supports rather than substitutes for the local format/tokenizer validation.

Dataset: official `hellaswag_val.jsonl`, 10,042 rows, SHA-256
`0AA3B88843990F3F10A97B9575C94D7B71FB2205240BA04AE4884D9E9C992588`.
