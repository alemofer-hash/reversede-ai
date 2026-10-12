from __future__ import annotations

import math
import re
from typing import Any

import pandas as pd
from pandas.api.types import is_bool_dtype, is_numeric_dtype

from .config import ReversedeConfig
from .types import ID_NAME, normalized_name

TARGET_EXACT = {
    "target",
    "label",
    "class",
    "outcome",
    "response",
    "y",
    "critical_temp",
}
TARGET_TOKEN = re.compile(
    r"(^|_)(target|label|class|outcome|response|default|churn|fraud|survived|critical_temp|temperature)(_|$)",
    re.I,
)


def infer_target(
    data: pd.DataFrame, config: ReversedeConfig
) -> tuple[str | None, float, list[dict[str, Any]]]:
    candidates: list[dict[str, Any]] = []
    for column in data.columns:
        key = normalized_name(column)
        if ID_NAME.search(key) or not TARGET_TOKEN.search(key):
            continue
        series = data[column]
        observed = series.dropna()
        if len(observed) < 3 or observed.nunique() < 2:
            continue
        score = 0.96 if key in TARGET_EXACT else 0.88
        unique = int(observed.nunique())
        if is_bool_dtype(series) or unique <= min(50, max(2, int(math.ceil(0.10 * len(observed))))):
            score += 0.03
        missing = float(series.isna().mean())
        if missing > 0.50:
            score -= 0.08
        candidates.append(
            {
                "column": column,
                "confidence": round(min(0.99, score), 4),
                "reason": "name suggests an outcome; cardinality/missingness adjust confidence",
                "non_null": int(len(observed)),
                "unique": unique,
            }
        )
    candidates.sort(key=lambda item: (-item["confidence"], item["column"]))
    if not candidates:
        return None, 0.0, candidates
    best = candidates[0]
    runner_up = candidates[1]["confidence"] if len(candidates) > 1 else 0.0
    if best["confidence"] < config.target_confidence_threshold:
        return None, float(best["confidence"]), candidates
    if best["confidence"] - runner_up < config.target_margin:
        return None, float(best["confidence"]), candidates
    return str(best["column"]), float(best["confidence"]), candidates


def resolve_task(series: pd.Series | None, requested: str) -> str | None:
    if requested != "auto":
        return requested
    if series is None:
        return None
    observed = series.dropna()
    if is_bool_dtype(series) or not is_numeric_dtype(series):
        return "classification"
    threshold = min(20, max(2, int(math.ceil(0.05 * len(observed)))))
    return "classification" if observed.nunique() <= threshold else "regression"
