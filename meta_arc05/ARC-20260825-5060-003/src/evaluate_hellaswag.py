"""Lightweight, auditable HellaSwag conditional-likelihood evaluator."""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
import os
import random
import re
import time
import urllib.request
from pathlib import Path

import numpy as np
import torch
import yaml

os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
os.environ.setdefault("HF_HUB_DOWNLOAD_TIMEOUT", "600")
from transformers import AutoModelForCausalLM, AutoTokenizer


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_DATA_SHA256 = "0AA3B88843990F3F10A97B9575C94D7B71FB2205240BA04AE4884D9E9C992588"


def preprocess(text: str) -> str:
    """Match the EleutherAI lm-evaluation-harness HellaSwag preprocessing."""
    text = text.strip().replace(" [title]", ". ")
    text = re.sub(r"\[.*?\]", "", text)
    return text.replace("  ", " ")


def load_documents(config: dict) -> tuple[list[dict], str]:
    path = ROOT / "data/hellaswag_val.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        urllib.request.urlretrieve(config["hellaswag_url"], path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest().upper()
    if digest != EXPECTED_DATA_SHA256:
        raise ValueError(f"Unexpected HellaSwag SHA256: {digest}")
    documents = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    if len(documents) != 10042:
        raise ValueError(f"Expected 10042 HellaSwag validation rows, found {len(documents)}")
    rng = random.Random(config["hellaswag_sample_seed"])
    indices = sorted(rng.sample(range(len(documents)), config["hellaswag_examples"]))
    return [{**documents[index], "dataset_index": index} for index in indices], digest


def processed_document(document: dict) -> tuple[str, list[str], int]:
    context = document["ctx_a"] + " " + document["ctx_b"].capitalize()
    query = preprocess(document["activity_label"] + ": " + context)
    # A separating space is the standard causal-LM continuation convention.
    choices = [" " + preprocess(ending) for ending in document["endings"]]
    return query, choices, int(document["label"])


def bootstrap_ci(values: list[int], seed: int, samples: int = 10000) -> list[float]:
    rng = np.random.default_rng(seed)
    array = np.asarray(values, dtype=float)
    means = np.mean(rng.choice(array, size=(samples, len(array)), replace=True), axis=1)
    return [float(value) for value in np.quantile(means, [0.025, 0.975])]


@torch.inference_mode()
def evaluate(config: dict, revision: str) -> dict:
    started = time.perf_counter()
    documents, dataset_sha = load_documents(config)
    tokenizer = AutoTokenizer.from_pretrained(config["model"], revision=revision)
    dtype = {"float16": torch.float16, "bfloat16": torch.bfloat16}[config["dtype"]]
    model = AutoModelForCausalLM.from_pretrained(
        config["model"], revision=revision, dtype=dtype,
    ).to("cuda").eval()
    torch.cuda.reset_peak_memory_stats()
    max_length = int(model.config.max_position_embeddings)
    records = []
    sanity = []
    truncated = 0

    flattened = []
    for example_index, document in enumerate(documents):
        query, choices, label = processed_document(document)
        query_ids = tokenizer.encode(query, add_special_tokens=False)
        if not query_ids:
            query_ids = [tokenizer.bos_token_id]
        choice_lengths = []
        for choice_index, choice in enumerate(choices):
            choice_ids = tokenizer.encode(choice, add_special_tokens=False)
            if not choice_ids:
                raise ValueError("Empty HellaSwag continuation after tokenization")
            available_context = max_length - len(choice_ids)
            used_query = query_ids[-available_context:]
            was_truncated = len(used_query) != len(query_ids)
            truncated += int(was_truncated)
            ids = used_query + choice_ids
            flattened.append({
                "example_index": example_index, "choice_index": choice_index,
                "ids": ids, "target_start": len(used_query),
                "target_length": len(choice_ids),
            })
            choice_lengths.append(len(choice_ids))
        if len(sanity) < 10:
            sanity.append({
                "dataset_index": document["dataset_index"], "query": query,
                "choices": choices, "gold": label,
                "query_tokens": len(query_ids), "choice_tokens": choice_lengths,
            })

    scores = [[None] * 4 for _ in documents]
    batch_size = config["hellaswag_batch_size"]
    for start in range(0, len(flattened), batch_size):
        batch = flattened[start : start + batch_size]
        width = max(len(row["ids"]) for row in batch)
        input_ids = torch.full(
            (len(batch), width), tokenizer.eos_token_id, dtype=torch.long, device="cuda"
        )
        attention_mask = torch.zeros((len(batch), width), dtype=torch.long, device="cuda")
        for index, row in enumerate(batch):
            ids = torch.tensor(row["ids"], dtype=torch.long, device="cuda")
            input_ids[index, : len(ids)] = ids
            attention_mask[index, : len(ids)] = 1
        log_probs = model(input_ids, attention_mask=attention_mask, use_cache=False).logits.float().log_softmax(-1)
        for index, row in enumerate(batch):
            sequence = input_ids[index, : len(row["ids"])]
            first_logit = row["target_start"] - 1
            last_logit = len(row["ids"]) - 1
            token_log_probs = log_probs[index, first_logit:last_logit].gather(
                -1, sequence[row["target_start"] :].unsqueeze(-1)
            ).squeeze(-1)
            total = float(token_log_probs.sum().item())
            scores[row["example_index"]][row["choice_index"]] = {
                "sum_logprob": total,
                "mean_logprob": total / row["target_length"],
                "tokens": row["target_length"],
            }
        if start % (batch_size * 16) == 0:
            print(json.dumps({"revision": revision, "choices_done": min(start + len(batch), len(flattened)), "choices_total": len(flattened)}), flush=True)

    raw_correct = []
    normalized_correct = []
    raw_predictions = []
    normalized_predictions = []
    for document, choice_scores in zip(documents, scores):
        gold = int(document["label"])
        raw_prediction = int(np.argmax([row["sum_logprob"] for row in choice_scores]))
        normalized_prediction = int(np.argmax([row["mean_logprob"] for row in choice_scores]))
        raw_predictions.append(raw_prediction)
        normalized_predictions.append(normalized_prediction)
        raw_correct.append(int(raw_prediction == gold))
        normalized_correct.append(int(normalized_prediction == gold))
        records.append({
            "dataset_index": document["dataset_index"], "gold": gold,
            "raw_prediction": raw_prediction,
            "normalized_prediction": normalized_prediction,
            "scores": choice_scores,
        })

    raw_counts = np.bincount(raw_predictions, minlength=4).tolist()
    normalized_counts = np.bincount(normalized_predictions, minlength=4).tolist()
    result = {
        "model": config["model"], "revision": revision,
        "dtype": config["dtype"],
        "commit_hash": getattr(model.config, "_commit_hash", None),
        "parameters": sum(parameter.numel() for parameter in model.parameters()),
        "n_layers": model.config.num_hidden_layers,
        "dataset_url": config["hellaswag_url"], "dataset_sha256": dataset_sha,
        "dataset_rows": 10042, "sample_seed": config["hellaswag_sample_seed"],
        "examples": len(documents), "raw_accuracy": float(np.mean(raw_correct)),
        "normalized_accuracy": float(np.mean(normalized_correct)),
        "raw_bootstrap_95_ci": bootstrap_ci(raw_correct, 20260826),
        "normalized_bootstrap_95_ci": bootstrap_ci(normalized_correct, 20260827),
        "raw_prediction_counts": raw_counts,
        "normalized_prediction_counts": normalized_counts,
        "distinct_normalized_labels": sum(count > 0 for count in normalized_counts),
        "max_normalized_label_fraction": max(normalized_counts) / len(documents),
        "truncated_choices": truncated,
        "sanity_examples": sanity, "per_example": records,
        "runtime_seconds": time.perf_counter() - started,
        "peak_cuda_bytes": torch.cuda.max_memory_allocated(),
    }
    del model
    gc.collect()
    torch.cuda.empty_cache()
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--revision", required=True)
    args = parser.parse_args()
    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    if args.revision not in config["revisions"]:
        raise ValueError("Revision is not preregistered")
    result = evaluate(config, args.revision)
    output = ROOT / config["output_dir"] / "competence" / f"hellaswag-{args.revision}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({
        "revision": args.revision, "raw_accuracy": result["raw_accuracy"],
        "normalized_accuracy": result["normalized_accuracy"],
        "normalized_ci": result["normalized_bootstrap_95_ci"],
        "prediction_counts": result["normalized_prediction_counts"],
        "output": str(output),
    }), flush=True)


if __name__ == "__main__":
    main()
