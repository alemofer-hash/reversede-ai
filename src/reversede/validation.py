from __future__ import annotations

import pandas as pd

from .config import ReversedeConfig

VALID_TASKS = {"auto", "regression", "classification"}


def validate_input(
    data: pd.DataFrame,
    target: str | None,
    task: str,
    config: ReversedeConfig,
) -> None:
    if not isinstance(data, pd.DataFrame):
        raise TypeError("data must be a pandas DataFrame")
    if data.empty or data.shape[1] == 0:
        raise ValueError("data must be a non-empty DataFrame")
    if not data.columns.is_unique:
        duplicates = data.columns[data.columns.duplicated()].tolist()
        raise ValueError(f"duplicate column names are not allowed: {duplicates}")
    if not all(isinstance(column, str) and column for column in data.columns):
        raise ValueError("all column names must be non-empty strings")
    if task not in VALID_TASKS:
        raise ValueError(f"task must be one of {sorted(VALID_TASKS)}")
    config.validate()
    unknown = (set(config.include_columns) | set(config.exclude_columns)) - set(data.columns)
    if unknown:
        raise ValueError(f"configured columns not present: {sorted(unknown)}")
    overlap = set(config.include_columns) & set(config.exclude_columns)
    if overlap:
        raise ValueError(f"columns cannot be both included and excluded: {sorted(overlap)}")
    if target is not None:
        if target not in data.columns:
            raise ValueError(f"target column not found: {target!r}")
        observed = data[target].dropna()
        if len(observed) < 2 or observed.nunique(dropna=True) < 2:
            raise ValueError(
                "target must have at least two observed values and two distinct values"
            )
        if target in config.exclude_columns or target in config.include_columns:
            raise ValueError("target cannot appear in include_columns or exclude_columns")
