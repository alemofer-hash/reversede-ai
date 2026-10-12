from __future__ import annotations

import math
from typing import Any

import numpy as np
import pandas as pd

from .types import numeric_view


def _eta_squared(values: pd.Series, groups: pd.Series) -> float:
    frame = pd.DataFrame(
        {"value": pd.to_numeric(values, errors="coerce"), "group": groups}
    ).dropna()
    if len(frame) < 3 or frame["group"].nunique() < 2 or frame["value"].nunique() < 2:
        return float("nan")
    overall = float(frame["value"].mean())
    between = 0.0
    for _, subset in frame.groupby("group", observed=True)["value"]:
        between += len(subset) * (float(subset.mean()) - overall) ** 2
    total = float(((frame["value"] - overall) ** 2).sum())
    return float(between / total) if total > 0 else float("nan")


def _cramers_v(left: pd.Series, right: pd.Series) -> float:
    table = pd.crosstab(left, right)
    n = int(table.to_numpy().sum())
    if n < 3 or min(table.shape) < 2:
        return float("nan")
    observed = table.to_numpy(dtype=float)
    expected = np.outer(observed.sum(axis=1), observed.sum(axis=0)) / n
    chi2 = float(
        np.divide(
            (observed - expected) ** 2, expected, out=np.zeros_like(expected), where=expected > 0
        ).sum()
    )
    phi2 = chi2 / n
    rows, cols = table.shape
    corrected = max(0.0, phi2 - ((cols - 1) * (rows - 1)) / max(n - 1, 1))
    rows_corr = rows - ((rows - 1) ** 2) / max(n - 1, 1)
    cols_corr = cols - ((cols - 1) ** 2) / max(n - 1, 1)
    denominator = min(cols_corr - 1, rows_corr - 1)
    return float(math.sqrt(corrected / denominator)) if denominator > 0 else float("nan")


def association(feature: pd.Series, target: pd.Series, kind: str, task: str) -> dict[str, Any]:
    frame = pd.DataFrame({"x": feature, "y": target}).dropna()
    valid_n = int(len(frame))
    coverage = float(valid_n / max(1, len(feature)))
    result: dict[str, Any] = {
        "metric": None,
        "value": float("nan"),
        "secondary_metric": None,
        "secondary_value": float("nan"),
        "ranking_score": float("nan"),
        "valid_n": valid_n,
        "coverage": coverage,
    }
    if valid_n < 3 or frame["y"].nunique() < 2 or frame["x"].nunique() < 2:
        return result

    if task == "regression":
        y = pd.to_numeric(frame["y"], errors="coerce")
        if kind in {"numeric", "numeric_string", "datetime"}:
            x = numeric_view(frame["x"])
            aligned = pd.DataFrame({"x": x, "y": y}).dropna()
            if len(aligned) >= 3 and aligned["x"].nunique() >= 2 and aligned["y"].nunique() >= 2:
                pearson = abs(float(aligned["x"].corr(aligned["y"], method="pearson")))
                # Spearman is Pearson correlation over average ranks. Computing
                # it directly keeps the core independent from SciPy, which
                # pandas otherwise imports for ``method="spearman"``.
                spearman = abs(float(aligned["x"].rank().corr(aligned["y"].rank())))
                result.update(
                    metric="abs_pearson",
                    value=pearson,
                    secondary_metric="abs_spearman",
                    secondary_value=spearman,
                    ranking_score=max(pearson, spearman),
                    valid_n=int(len(aligned)),
                    coverage=float(len(aligned) / max(1, len(feature))),
                )
        else:
            eta = _eta_squared(y, frame["x"].astype("string").fillna("<missing>"))
            result.update(metric="eta_squared", value=eta, ranking_score=eta)
    elif task == "classification":
        y_group = frame["y"].astype("string").fillna("<missing>")
        if kind in {"numeric", "numeric_string", "datetime"}:
            eta = _eta_squared(numeric_view(frame["x"]), y_group)
            result.update(metric="eta_squared", value=eta, ranking_score=eta)
        else:
            value = _cramers_v(frame["x"].astype("string").fillna("<missing>"), y_group)
            result.update(metric="cramers_v", value=value, ranking_score=value)
    return result


def structural_priority(series: pd.Series, kind: str) -> float:
    observed = series.dropna()
    coverage = float(series.notna().mean())
    if observed.empty:
        return 0.0
    if kind in {"numeric", "numeric_string", "datetime"}:
        numeric = numeric_view(observed).dropna()
        richness = min(1.0, numeric.nunique() / max(10.0, math.sqrt(max(len(numeric), 1))))
    else:
        frequencies = observed.astype("string").value_counts(normalize=True)
        if len(frequencies) <= 1:
            richness = 0.0
        else:
            entropy = float(-(frequencies * np.log(frequencies)).sum())
            richness = entropy / math.log(len(frequencies))
    return float(coverage * richness)
