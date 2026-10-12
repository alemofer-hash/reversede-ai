from __future__ import annotations

import re
import unicodedata

import numpy as np
import pandas as pd
from pandas.api.types import is_bool_dtype, is_datetime64_any_dtype, is_numeric_dtype

ID_NAME = re.compile(r"(^|_)(id|uuid|guid|index|row|record|codigo|code|key)(_|$)", re.I)
DATE_NAME = re.compile(r"(^|_)(date|datetime|timestamp|time|year|month|day|data|hora)(_|$)", re.I)
TEXT_NAME = re.compile(
    r"(^|_)(text|comment|description|notes|message|body|title|descricao)(_|$)", re.I
)
LEAK_NAME = re.compile(
    r"(^|_)(post|after|future|outcome|result|approved|paid|death|final|discharge|label_proxy)(_|$)",
    re.I,
)
POSTAL_PHONE_NAME = re.compile(r"(^|_)(zip|postal|postcode|cep|phone|telefone)(_|$)", re.I)


def normalized_name(value: str) -> str:
    plain = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "_", plain.lower()).strip("_")


def numeric_view(series: pd.Series) -> pd.Series:
    if is_datetime64_any_dtype(series):
        return pd.Series(series.astype("int64", copy=False), index=series.index).replace(
            np.iinfo("int64").min, np.nan
        )
    candidate = series
    if not is_numeric_dtype(series):
        candidate = series.astype("string").str.strip().str.replace(",", ".", regex=False)
    return pd.to_numeric(candidate, errors="coerce").replace([np.inf, -np.inf], np.nan)


def infer_kind(name: str, series: pd.Series) -> tuple[str, dict[str, float | bool]]:
    """Infer a practical type and return traceable evidence."""
    key = normalized_name(name)
    observed = series.dropna()
    sample = observed.head(1000)
    evidence: dict[str, float | bool] = {}
    if is_bool_dtype(series):
        return "categorical", {"dtype_boolean": True}
    if is_datetime64_any_dtype(series):
        return "datetime", {"dtype_datetime": True}
    if is_numeric_dtype(series):
        return "numeric", {"dtype_numeric": True}
    if sample.empty:
        return "categorical", {"empty_observed_sample": True}

    as_text = sample.astype(str).str.strip()
    numeric = pd.to_numeric(as_text.str.replace(",", ".", regex=False), errors="coerce")
    numeric_ratio = float(numeric.notna().mean())
    evidence["numeric_parse_ratio"] = numeric_ratio
    if numeric_ratio >= 0.98 and not POSTAL_PHONE_NAME.search(key):
        return "numeric_string", evidence

    date_ratio = 0.0
    if DATE_NAME.search(key):
        parsed = pd.to_datetime(as_text, errors="coerce", utc=True)
        date_ratio = float(parsed.notna().mean())
    evidence["date_parse_ratio"] = date_ratio
    if date_ratio >= 0.90:
        return "datetime", evidence

    lengths = as_text.str.len()
    unique_fraction = float(as_text.nunique() / max(1, len(as_text)))
    evidence.update(
        {
            "mean_text_length": float(lengths.mean()),
            "text_unique_fraction": unique_fraction,
        }
    )
    if TEXT_NAME.search(key) or (
        len(as_text) >= 20 and unique_fraction >= 0.80 and lengths.mean() >= 24
    ):
        return "text", evidence
    return "categorical", evidence


def is_probable_id(
    name: str, series: pd.Series, kind: str, unique_fraction: float
) -> tuple[bool, str]:
    key = normalized_name(name)
    if ID_NAME.search(key):
        return True, "name contains an identifier token"
    observed = series.dropna()
    if kind in {"categorical", "text"} and len(observed) >= 20 and unique_fraction >= 0.98:
        return True, "string/categorical values are almost unique"
    if kind == "numeric" and len(observed) >= 20 and unique_fraction >= 0.98:
        numeric = pd.to_numeric(observed, errors="coerce")
        if numeric.notna().all() and numeric.is_monotonic_increasing:
            diffs = numeric.diff().dropna()
            if not diffs.empty and diffs.nunique() <= 2:
                return True, "numeric values are nearly unique and monotonic/sequential"
    return False, ""
