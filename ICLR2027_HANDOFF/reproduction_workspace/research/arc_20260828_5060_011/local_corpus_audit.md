# Local corpus audit

Audit timestamp: 2026-08-28 (Asia/Shanghai). The audit inspected only local
metadata, text structure, size, hashes, and frozen-tokenizer compatibility. No
candidate-corpus intervention outcome, ΔS, KL/NLL effect, or replication result
was computed before selection.

| Candidate | Local identity | Approx. size | Language/domain | Frozen-tokenizer compatibility | Decision |
|---|---|---:|---|---|---|
| WikiText-2 train | `meta_arc05/ARC-20260825-5060-001/data/wikitext2_train.txt` | 10.30 MiB; 2,447,746 tokens | English Wikipedia articles | PASS | Reference corpus; ineligible as the new corpus. |
| HellaSwag validation | `meta_arc05/ARC-20260825-5060-003/data/hellaswag_val.jsonl` | 11.68 MiB; 10,042 records | English everyday-event descriptions from ActivityNet/WikiHow-style sources | PASS; 860,324 tokens after deterministic correct-continuation extraction | **SELECTED before outcomes** |
| `zcxi/suju` cache | Hugging Face local cache, commit `8468629d...` | Hundreds of MiB | Chinese A-share tabular time series | Not an English text corpus | Reject. |
| Project prompts/reports | Various repository Markdown/JSON | Sufficient bytes collectively | Research artifacts and generated project text | Tokenizable | Reject: non-natural, outcome/project leakage risk, and no stable public corpus identity. |

## Selection rationale

HellaSwag is the only locally available candidate satisfying all preregistered
criteria: English text, sufficient size, materially different source/domain,
stable local identity, frozen-tokenizer compatibility, and no download or
special model. It is selected because of those properties, not because of any
Candidate A outcome.

The derived corpus concatenates each validation context with its labeled correct
ending and separates records by two newline characters. It excludes distractor
endings, labels, activity names, and metadata. This is a deterministic format
conversion necessary to obtain a natural continuation stream; no result-based
filtering occurs.

## Frozen identities

- Source SHA-256: `0AA3B88843990F3F10A97B9575C94D7B71FB2205240BA04AE4884D9E9C992588`
- Derived text SHA-256: `EF75B67A0F3A316B6D465295E2DD58314738FD0E38BCF01790DBA7022C35468E`
- WikiText-2 SHA-256: `9E9FA1AD55B1C2C95B08E37DD8E653F638FAC2C6DE904B79E813611EEFBC985F`
- Tokenizer: cached `EleutherAI/pythia-160m-seed1@main`, `GPTNeoXTokenizerFast`
- Evaluation subset: 18 deterministic sequences, 4,608 predicted tokens per checkpoint

## Pre-outcome data-quality finding

The selected corpus is large enough and structurally valid. Its principal risk
is domain/format: short event descriptions are concatenated into a stream, while
WikiText-2 contains longer encyclopedia passages. This is the intended
distribution change, but cross-record boundaries and benchmark-source
contamination remain limitations to report rather than reasons to alter the
frozen assay.

