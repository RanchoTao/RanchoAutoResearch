"""Execute one real classification experiment and emit a resolved-config receipt."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

import numpy as np
from sklearn.datasets import load_breast_cancer, load_digits, load_iris, load_wine
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


DEFAULTS = {
    "scaler": "standard",
    "C": 0.1,
    "metric": "balanced_accuracy",
    "seed": 17,
    "test_size": 0.3,
}

ENV_KEYS = {
    "scaler": "EXECCONFIG_SCALER",
    "C": "EXECCONFIG_C",
    "metric": "EXECCONFIG_METRIC",
    "seed": "EXECCONFIG_SEED",
}


def _coerce(key: str, value: object) -> object:
    if key == "C" or key == "test_size":
        return float(value)
    if key == "seed":
        return int(value)
    return str(value)


def resolve(args: argparse.Namespace) -> tuple[dict[str, object], dict[str, object]]:
    """Resolve defaults < JSON config < environment < explicit CLI."""
    resolved = dict(DEFAULTS)
    sources: dict[str, str] = {key: "default" for key in resolved}

    if args.config:
        payload = json.loads(Path(args.config).read_text(encoding="utf-8"))
        for key, value in payload.items():
            if key in resolved:
                resolved[key] = _coerce(key, value)
                sources[key] = "config"

    for key, env_key in ENV_KEYS.items():
        if env_key in os.environ:
            resolved[key] = _coerce(key, os.environ[env_key])
            sources[key] = "environment"

    cli_values = {
        "scaler": args.scaler,
        "C": args.c_value,
        "metric": args.metric,
        "seed": args.seed,
    }
    for key, value in cli_values.items():
        if value is not None:
            resolved[key] = _coerce(key, value)
            sources[key] = "cli"
    return resolved, sources


def load_dataset(name: str) -> tuple[np.ndarray, np.ndarray]:
    loaders = {
        "iris": load_iris,
        "wine": load_wine,
        "breast_cancer": load_breast_cancer,
        "digits": load_digits,
    }
    bunch = loaders[name]()
    return np.asarray(bunch.data), np.asarray(bunch.target)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True, choices=["iris", "wine", "breast_cancer", "digits"])
    parser.add_argument("--config")
    parser.add_argument("--scaler", choices=["standard", "none"])
    parser.add_argument("--C", dest="c_value", type=float)
    parser.add_argument("--metric", choices=["accuracy", "balanced_accuracy"])
    parser.add_argument("--seed", type=int)
    parser.add_argument("--receipt", required=True)
    args = parser.parse_args()

    resolved, sources = resolve(args)
    X, y = load_dataset(args.dataset)
    dataset_hash = hashlib.sha256(X.tobytes() + y.tobytes()).hexdigest()
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=float(resolved["test_size"]),
        random_state=int(resolved["seed"]),
        stratify=y,
    )
    steps: list[tuple[str, object]] = []
    if resolved["scaler"] == "standard":
        steps.append(("scaler", StandardScaler()))
    steps.append(
        (
            "classifier",
            LogisticRegression(C=float(resolved["C"]), max_iter=500, random_state=int(resolved["seed"])),
        )
    )
    model = Pipeline(steps)
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    metric_fn = accuracy_score if resolved["metric"] == "accuracy" else balanced_accuracy_score
    score = float(metric_fn(y_test, pred))

    receipt = {
        "schema": "execconfig-receipt-v1",
        "dataset": args.dataset,
        "dataset_sha256": dataset_hash,
        "resolved": resolved,
        "winning_source": sources,
        "n_train": int(len(y_train)),
        "n_test": int(len(y_test)),
        "score": score,
        "score_sha256": hashlib.sha256(f"{score:.17g}".encode()).hexdigest(),
    }
    path = Path(args.receipt)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()

