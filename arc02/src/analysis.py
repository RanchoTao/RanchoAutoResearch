from __future__ import annotations

import itertools
import math
from typing import Iterable

import numpy as np


def linear_cka(x: np.ndarray, y: np.ndarray) -> float:
    x = x - x.mean(axis=0, keepdims=True)
    y = y - y.mean(axis=0, keepdims=True)
    numerator = np.linalg.norm(x.T @ y, ord="fro") ** 2
    denominator = np.linalg.norm(x.T @ x, ord="fro") * np.linalg.norm(y.T @ y, ord="fro")
    return float(numerator / denominator) if denominator > 0 else float("nan")


def _information_criteria(y: np.ndarray, prediction: np.ndarray, k: int) -> dict[str, float]:
    n = len(y)
    rss = max(float(np.square(y - prediction).sum()), 1e-12)
    return {
        "rss": rss,
        "aic": float(n * math.log(rss / n) + 2 * k),
        "bic": float(n * math.log(rss / n) + k * math.log(n)),
    }


def fit_depth_models(depths: Iterable[int], values: Iterable[float]) -> dict:
    x = np.asarray(list(depths), dtype=float)
    y = np.asarray(list(values), dtype=float)
    output: dict[str, dict] = {}
    for name, degree in (("linear", 1), ("quadratic", 2)):
        coef = np.polyfit(x, y, degree)
        pred = np.polyval(coef, x)
        output[name] = {
            "coefficients": coef.tolist(),
            "predictions": pred.tolist(),
            **_information_criteria(y, pred, degree + 1),
        }
    candidates = []
    for breakpoint in x[1:-1]:
        design = np.column_stack([np.ones_like(x), x, np.maximum(0.0, x - breakpoint)])
        coef, *_ = np.linalg.lstsq(design, y, rcond=None)
        pred = design @ coef
        candidates.append((float(np.square(y - pred).sum()), float(breakpoint), coef, pred))
    _, breakpoint, coef, pred = min(candidates, key=lambda item: item[0])
    output["piecewise"] = {
        "breakpoint": breakpoint,
        "coefficients": coef.tolist(),
        "predictions": pred.tolist(),
        **_information_criteria(y, pred, 4),  # includes selected breakpoint
    }
    return output


def jaccard(a: set, b: set) -> float:
    union = a | b
    return len(a & b) / len(union) if union else 1.0

