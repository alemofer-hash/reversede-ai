from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from .config import ReversedeConfig
from .types import numeric_view

SENTINELS = {-999999, -9999, -999, -99, 999, 9999, 99999}


def _numeric_stress(series: pd.Series) -> dict[str, Any]:
    raw_numeric = pd.to_numeric(series, errors="coerce")
    infinite_count = int(np.isinf(raw_numeric.to_numpy(dtype=float, na_value=np.nan)).sum())
    numeric = raw_numeric.replace([np.inf, -np.inf], np.nan).dropna()
    if numeric.empty:
        return {
            "infinite_count": infinite_count,
            "variance": float("nan"),
            "skewness": float("nan"),
            "kurtosis": float("nan"),
            "iqr_outlier_count": 0,
            "iqr_outlier_fraction": float("nan"),
            "robust_z_outlier_count": 0,
            "robust_z_outlier_fraction": float("nan"),
            "negative_count": 0,
            "zero_count": 0,
            "sentinel_count": 0,
            "minimum": float("nan"),
            "maximum": float("nan"),
            "q01": float("nan"),
            "median": float("nan"),
            "q99": float("nan"),
        }
    q1, q3 = numeric.quantile([0.25, 0.75])
    iqr = float(q3 - q1)
    if iqr > 0:
        iqr_mask = (numeric < q1 - 1.5 * iqr) | (numeric > q3 + 1.5 * iqr)
    else:
        iqr_mask = pd.Series(False, index=numeric.index)
    median = float(numeric.median())
    mad = float((numeric - median).abs().median())
    if mad > 0:
        robust_z = 0.6745 * (numeric - median).abs() / mad
        robust_mask = robust_z > 3.5
    else:
        robust_mask = pd.Series(False, index=numeric.index)
    return {
        "infinite_count": infinite_count,
        "variance": float(numeric.var()) if len(numeric) > 1 else 0.0,
        "skewness": float(numeric.skew()) if numeric.nunique() > 2 else 0.0,
        "kurtosis": float(numeric.kurt()) if numeric.nunique() > 3 else 0.0,
        "iqr_outlier_count": int(iqr_mask.sum()),
        "iqr_outlier_fraction": float(iqr_mask.mean()),
        "robust_z_outlier_count": int(robust_mask.sum()),
        "robust_z_outlier_fraction": float(robust_mask.mean()),
        "negative_count": int((numeric < 0).sum()),
        "zero_count": int((numeric == 0).sum()),
        "sentinel_count": int(numeric.isin(SENTINELS).sum()),
        "minimum": float(numeric.min()),
        "maximum": float(numeric.max()),
        "q01": float(numeric.quantile(0.01)),
        "median": median,
        "q99": float(numeric.quantile(0.99)),
    }


def build_stress(
    data: pd.DataFrame, candidates: pd.DataFrame, config: ReversedeConfig
) -> pd.DataFrame:
    eligible = candidates[candidates["eligible"]]
    numeric_columns = eligible.loc[
        eligible["kind"].isin(["numeric", "numeric_string"]), "column"
    ].tolist()
    correlation = pd.DataFrame()
    if len(numeric_columns) >= 2:
        numeric_frame = pd.DataFrame(
            {column: numeric_view(data[column]) for column in numeric_columns}
        )
        # Pairwise Pearson correlation over ranks is Spearman correlation and
        # avoids making SciPy an undeclared core dependency.
        correlation = numeric_frame.rank().corr(method="pearson").abs()

    rows: list[dict[str, Any]] = []
    for candidate in eligible.to_dict(orient="records"):
        column = str(candidate["column"])
        series = data[column]
        kind = str(candidate["kind"])
        observed = series.dropna()
        counts = observed.astype("string").str.strip().value_counts(dropna=False)
        rare_levels = (
            int((counts / max(1, len(observed)) < config.rare_category_fraction).sum())
            if len(counts)
            else 0
        )
        empty_count = (
            int(observed.astype("string").str.strip().eq("").sum()) if len(observed) else 0
        )
        conversion_failure = 0
        numeric_stats: dict[str, Any] = {
            "infinite_count": 0,
            "variance": float("nan"),
            "skewness": float("nan"),
            "kurtosis": float("nan"),
            "iqr_outlier_count": 0,
            "iqr_outlier_fraction": float("nan"),
            "robust_z_outlier_count": 0,
            "robust_z_outlier_fraction": float("nan"),
            "negative_count": 0,
            "zero_count": 0,
            "sentinel_count": 0,
            "minimum": float("nan"),
            "maximum": float("nan"),
            "q01": float("nan"),
            "median": float("nan"),
            "q99": float("nan"),
        }
        if kind in {"numeric", "numeric_string"}:
            numeric_stats = _numeric_stress(series)
            if kind == "numeric_string":
                conversion_failure = int(pd.to_numeric(observed, errors="coerce").isna().sum())

        top_partner = None
        top_correlation = float("nan")
        if column in correlation.columns:
            values = correlation[column].drop(labels=[column], errors="ignore").dropna()
            if not values.empty:
                top_partner = str(values.idxmax())
                top_correlation = float(values.max())

        suspicious_date_count = 0
        if kind == "datetime":
            dates = pd.to_datetime(observed, errors="coerce", utc=True)
            suspicious_date_count = int(((dates.dt.year < 1900) | (dates.dt.year > 2100)).sum())

        dominant_fraction = (
            float(counts.iloc[0] / max(1, len(observed))) if len(counts) else float("nan")
        )
        scale_ratio = float("nan")
        if pd.notna(numeric_stats["q99"]) and pd.notna(numeric_stats["q01"]):
            scale_ratio = float(abs(numeric_stats["q99"] - numeric_stats["q01"]))
        rows.append(
            {
                "column": column,
                "kind": kind,
                "selected": bool(candidate["selected"]),
                "null_count": int(series.isna().sum()),
                "null_fraction": float(series.isna().mean()),
                "non_null_count": int(series.notna().sum()),
                "unique_values": int(observed.nunique()),
                "dominant_fraction": dominant_fraction,
                "rare_level_count": rare_levels,
                "empty_string_count": empty_count,
                "numeric_conversion_failure_count": conversion_failure,
                "suspicious_date_count": suspicious_date_count,
                "top_collinear_partner": top_partner,
                "top_abs_spearman": top_correlation,
                "scale_span_q01_q99": scale_ratio,
                **numeric_stats,
            }
        )
    return pd.DataFrame(rows)
