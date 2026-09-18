#!/usr/bin/env python3
"""Prepare and freeze the locally cached HellaSwag corpus without model outcomes."""

from __future__ import annotations

import bisect
import csv
import hashlib
import json
import os
import random
from pathlib import Path

import yaml

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("HF_DATASETS_OFFLINE", "1")
os.environ.setdefault("WANDB_MODE", "offline")
from transformers import AutoTokenizer


ROOT = Path(__file__).resolve().parents[1]
CONFIG = yaml.safe_load((ROOT / "configs" / "cross_corpus.yaml").read_text(encoding="utf-8"))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def choose_starts(token_count: int, seed: int, count: int, length: int) -> list[int]:
    rng = random.Random(seed)
    usable = token_count - length - 1
    if usable <= 0:
        raise ValueError("evaluation text is too short")
    width = usable // count
    return [i * width + rng.randrange(max(1, width - length)) for i in range(count)]


def profile(tokens: list[int], text: str) -> dict:
    counts: dict[int, int] = {}
    for token in tokens:
        counts[token] = counts.get(token, 0) + 1
    ordered = sorted(counts.values(), reverse=True)
    return {
        "characters": len(text),
        "utf8_bytes": len(text.encode("utf-8")),
        "tokens": len(tokens),
        "unique_token_ids": len(counts),
        "unique_token_fraction": len(counts) / len(tokens),
        "top_10_token_fraction": sum(ordered[:10]) / len(tokens),
        "top_100_token_fraction": sum(ordered[:100]) / len(tokens),
        "characters_per_token": len(text) / len(tokens),
        "newline_count": text.count("\n"),
    }


def main() -> None:
    source = (ROOT / CONFIG["source_corpus_file"]).resolve()
    reference = (ROOT / "../../meta_arc05/ARC-20260825-5060-001/data/wikitext2_train.txt").resolve()
    data_dir = ROOT / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    derived = (ROOT / CONFIG["derived_text_file"]).resolve()

    documents = []
    text_parts = []
    char_cursor = 0
    with source.open(encoding="utf-8") as handle:
        for row_index, line in enumerate(handle):
            item = json.loads(line)
            label = int(item["label"])
            endings = item["endings"]
            if not 0 <= label < len(endings):
                raise ValueError(f"invalid label at row {row_index}: {label}")
            document = item["ctx"].strip() + " " + endings[label].strip()
            if row_index:
                text_parts.append("\n\n")
                char_cursor += 2
            start = char_cursor
            text_parts.append(document)
            char_cursor += len(document)
            documents.append({
                "document_index": row_index,
                "ind": item["ind"],
                "source_id": item["source_id"],
                "split_type": item["split_type"],
                "activity_label": item["activity_label"],
                "label": label,
                "char_start": start,
                "char_end_exclusive": char_cursor,
            })
    text = "".join(text_parts)
    derived.write_text(text, encoding="utf-8", newline="\n")

    tokenizer = AutoTokenizer.from_pretrained(
        "EleutherAI/pythia-160m-seed1", revision="main", local_files_only=True
    )
    encoded = tokenizer(
        text, add_special_tokens=False, return_offsets_mapping=True
    )
    tokens = list(encoded["input_ids"])
    offsets = encoded["offset_mapping"]
    if len(tokens) != len(offsets):
        raise RuntimeError("token/offset length mismatch")

    doc_starts = [row["char_start"] for row in documents]
    manifest_rows = []
    selected_slices = []
    for seed in CONFIG["evaluation_seeds"]:
        starts = choose_starts(
            len(tokens), seed, CONFIG["sequences_per_seed"], CONFIG["sequence_length"]
        )
        for sequence_index, start in enumerate(starts):
            end = start + CONFIG["sequence_length"] + 1
            token_slice = tokens[start:end]
            first_char = offsets[start][0]
            last_char = offsets[end - 1][1]
            first_doc = max(0, bisect.bisect_right(doc_starts, first_char) - 1)
            last_doc = max(0, bisect.bisect_right(doc_starts, max(first_char, last_char - 1)) - 1)
            manifest_rows.append({
                "evaluation_seed": seed,
                "sequence_index": sequence_index,
                "token_start": start,
                "token_end_exclusive": end,
                "token_count": len(token_slice),
                "token_ids_sha256": sha256_bytes(
                    json.dumps(token_slice, separators=(",", ":")).encode("ascii")
                ),
                "first_document_index": first_doc,
                "last_document_index": last_doc,
                "first_source_id": documents[first_doc]["source_id"],
                "last_source_id": documents[last_doc]["source_id"],
            })
            selected_slices.append({
                "evaluation_seed": seed,
                "sequence_index": sequence_index,
                "token_ids": token_slice,
            })

    with (ROOT / "corpus_manifest.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(manifest_rows[0]))
        writer.writeheader()
        writer.writerows(manifest_rows)
    with (data_dir / "selected_token_ids.json").open("w", encoding="utf-8") as handle:
        json.dump(selected_slices, handle, indent=2)
        handle.write("\n")
    with (data_dir / "source_documents.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(documents[0]))
        writer.writeheader()
        writer.writerows(documents)

    wiki_text = reference.read_text(encoding="utf-8")
    wiki_tokens = tokenizer(
        wiki_text, add_special_tokens=False, return_tensors=None
    )["input_ids"]
    output = {
        "selected_corpus": "HellaSwag validation correct continuations",
        "source_path": str(source),
        "source_sha256": sha256_file(source),
        "source_rows": len(documents),
        "derived_path": str(derived),
        "derived_sha256": sha256_file(derived),
        "tokenizer": "EleutherAI/pythia-160m-seed1@main",
        "tokenizer_class": tokenizer.__class__.__name__,
        "top1_outcomes_inspected": False,
        "intervention_outcomes_inspected": False,
        "selected": profile(tokens, text),
        "reference_wikitext2": {
            "path": str(reference),
            "sha256": sha256_file(reference),
            **profile(wiki_tokens, wiki_text),
        },
        "evaluation_sequences": len(manifest_rows),
        "evaluation_tokens_per_checkpoint": (
            len(CONFIG["evaluation_seeds"])
            * CONFIG["sequences_per_seed"]
            * CONFIG["sequence_length"]
        ),
    }
    (ROOT / "corpus_profile.json").write_text(
        json.dumps(output, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
