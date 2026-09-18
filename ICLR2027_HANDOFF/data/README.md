# Data archive

## WikiText-2

- `wikitext2_train.txt`
- Frozen SHA-256 from ARC-011 audit: `9E9FA1AD55B1C2C95B08E37DD8E653F638FAC2C6DE904B79E813611EEFBC985F`
- Used by ARC-001 through ARC-009.

## HellaSwag-derived stream

- `ARC-011/hellaswag_correct_continuations.txt`: deterministic concatenation of validation contexts and labeled correct endings.
- `ARC-011/selected_token_ids.json`: exact evaluation token slices.
- `ARC-011/source_documents.csv`: source-document mapping.
- `ARC-011/corpus_manifest.csv`, `corpus_profile.json`: hashes, offsets, and profile.
- Derived text SHA-256: `EF75B67A0F3A316B6D465295E2DD58314738FD0E38BCF01790DBA7022C35468E`.

The original HellaSwag validation JSONL (`hellaswag_val.jsonl`, frozen expected SHA-256 `0AA3B88843990F3F10A97B9575C94D7B71FB2205240BA04AE4884D9E9C992588`) is not present in the current repository and could not be packaged. Exact evaluation remains possible from the preserved derived text and token IDs; re-derivation from the public source requires reacquisition and hash verification.

No model weights or Hugging Face caches are included.
