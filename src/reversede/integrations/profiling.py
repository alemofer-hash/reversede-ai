"""Lazy adapter for the optional ydata-profiling dependency."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


def profile_with_ydata(
    data: pd.DataFrame,
    output_file: str | Path | None = None,
    **profile_kwargs: Any,
) -> Any:
    """Build a ydata-profiling report without making it a core dependency.

    Install ``reversede-ai[profiling]`` before calling this adapter. The input
    is copied so that the optional reporter cannot mutate the caller's frame.
    """
    try:
        from ydata_profiling import ProfileReport
    except ImportError as exc:
        raise ImportError(
            "profile_with_ydata requires the optional 'profiling' extra: "
            "pip install 'reversede-ai[profiling]'"
        ) from exc
    report = ProfileReport(data.copy(deep=True), **profile_kwargs)
    if output_file is not None:
        destination = Path(output_file)
        destination.parent.mkdir(parents=True, exist_ok=True)
        report.to_file(destination)
    return report
