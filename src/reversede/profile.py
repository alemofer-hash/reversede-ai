from __future__ import annotations

from typing import Any

import pandas as pd

from .association import association, structural_priority
from .config import ReversedeConfig
from .types import LEAK_NAME, infer_kind, is_probable_id, normalized_name


def build_profile(data: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    duplicate_rows = int(data.duplicated(keep=False).sum())
    for column in data.columns:
        series = data[column]
        kind, evidence = infer_kind(column, series)
        observed = series.dropna()
        unique = int(observed.nunique())
        unique_fraction = float(unique / max(1, len(observed)))
        dominant = (
            float(observed.value_counts(normalize=True).iloc[0]) if len(observed) else float("nan")
        )
        probable_id, id_reason = is_probable_id(column, series, kind, unique_fraction)
        rows.append(
            {
                "column": column,
                "dtype": str(series.dtype),
                "kind": kind,
                "rows": int(len(series)),
                "non_null_count": int(series.notna().sum()),
                "null_count": int(series.isna().sum()),
                "null_fraction": float(series.isna().mean()),
                "unique_values": unique,
                "unique_fraction": unique_fraction,
                "dominant_fraction": dominant,
                "probable_id": probable_id,
                "id_reason": id_reason,
                "name_leakage_signal": bool(LEAK_NAME.search(normalized_name(column))),
                "duplicate_rows_dataset": duplicate_rows,
                "type_evidence": evidence,
            }
        )
    return pd.DataFrame(rows)


def build_candidates(
    data: pd.DataFrame,
    profile: pd.DataFrame,
    target: str | None,
    task: str | None,
    config: ReversedeConfig,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    forced = set(config.include_columns)
    excluded = set(config.exclude_columns)
    for profile_row in profile.to_dict(orient="records"):
        column = str(profile_row["column"])
        series = data[column]
        kind = str(profile_row["kind"])
        unique = int(profile_row["unique_values"])
        dominant = float(profile_row["dominant_fraction"])
        eligible = True
        reason = "eligible for screening"
        if column == target:
            eligible, reason = False, "target is forbidden as an input feature"
        elif column in excluded:
            eligible, reason = False, "explicitly excluded by user/domain contract"
        elif unique <= 1:
            eligible, reason = False, "constant or entirely missing"
        elif bool(profile_row["probable_id"]):
            eligible, reason = False, f"possible identifier: {profile_row['id_reason']}"
        elif bool(profile_row["name_leakage_signal"]):
            eligible, reason = (
                False,
                "name suggests post-event/outcome information; review as possible leakage",
            )
        elif kind == "text":
            eligible, reason = False, "free text requires a separately validated NLP branch"
        elif float(profile_row["null_fraction"]) >= 0.995:
            eligible, reason = False, "at least 99.5% missing"
        elif kind == "categorical" and unique > config.max_categorical_levels:
            eligible, reason = False, "categorical cardinality exceeds configured tabular limit"
        if column in forced and column != target:
            eligible, reason = True, "forced inclusion by explicit user/domain override"

        assoc: dict[str, Any] = {
            "metric": None,
            "value": float("nan"),
            "secondary_metric": None,
            "secondary_value": float("nan"),
            "ranking_score": float("nan"),
            "valid_n": 0,
            "coverage": 0.0,
        }
        missing_signal = float("nan")
        if eligible and target is not None and task is not None:
            assoc = association(series, data[target], kind, task)
            if 0 < float(profile_row["null_fraction"]) < 1:
                missing_assoc = association(
                    series.isna().astype("string"), data[target], "categorical", task
                )
                missing_signal = float(missing_assoc["ranking_score"])
            scores = [
                value for value in (assoc["ranking_score"], missing_signal) if pd.notna(value)
            ]
            score = max(scores) if scores else float("nan")
            basis = (
                "normalized univariate screening; association is not causality or joint importance"
            )
        elif eligible:
            score = structural_priority(series, kind)
            basis = "structural priority from coverage/variation; not predictive importance"
            assoc["metric"] = "structural_priority"
        else:
            score = float("nan")
            basis = "not eligible"

        rows.append(
            {
                **{key: value for key, value in profile_row.items() if key != "type_evidence"},
                "association_metric": assoc["metric"],
                "association_value": assoc["value"],
                "secondary_metric": assoc["secondary_metric"],
                "secondary_value": assoc["secondary_value"],
                "missingness_signal": missing_signal,
                "ranking_score": score,
                "valid_n": int(assoc["valid_n"]),
                "coverage": float(assoc["coverage"]),
                "eligible": bool(eligible),
                "selected": False,
                "selection_basis": basis,
                "reason": reason,
                "forced": column in forced,
                "near_constant": bool(
                    pd.notna(dominant) and dominant >= config.near_constant_threshold
                ),
            }
        )
    report = pd.DataFrame(rows)
    eligible = report[report["eligible"] & report["ranking_score"].notna()].sort_values(
        ["ranking_score", "column"], ascending=[False, True], kind="mergesort"
    )
    selected_index = eligible.head(config.max_features).index
    selected_index = selected_index.union(report.index[report["forced"] & report["eligible"]])
    report.loc[selected_index, "selected"] = True
    report.loc[report["selected"] & ~report["forced"], "reason"] = (
        "prioritized candidate; validate semantics, timing, interactions, and out-of-sample effect"
    )
    report.loc[report["eligible"] & ~report["selected"], "reason"] = (
        "eligible but outside configured shortlist; remains visible for review"
    )
    return report.sort_values(
        ["selected", "eligible", "ranking_score", "column"],
        ascending=[False, False, False, True],
        na_position="last",
        kind="mergesort",
    ).reset_index(drop=True)
