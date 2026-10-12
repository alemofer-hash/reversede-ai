from __future__ import annotations

import json

import numpy as np
import pandas as pd
import pytest

from reversede import Reversede, ReversedeConfig
from reversede.blueprint import generate_blueprint


def test_tied_scores_are_selected_deterministically_by_column_name() -> None:
    signal = np.tile([0.0, 1.0], 20)
    frame = pd.DataFrame(
        {
            "target": signal,
            "z_signal": signal,
            "a_signal": signal,
        }
    )
    config = ReversedeConfig(max_features=1)
    first = Reversede(frame, target="target", task="regression", config=config)
    second = Reversede(frame, target="target", task="regression", config=config)
    assert first.selected_features_ == ["a_signal"]
    assert first.selected_features_ == second.selected_features_


def test_decimal_comma_numeric_strings_use_the_same_conversion_everywhere() -> None:
    frame = pd.DataFrame(
        {
            "target": [1.0, 2.0, 3.0, 4.0, 5.0],
            "medida": ["1,0", "2,0", "3,0", "4,0", "5,0"],
        }
    )
    result = Reversede(frame, target="target", task="regression")
    row = result.candidates_.set_index("column").loc["medida"]
    assert row["kind"] == "numeric_string"
    assert row["ranking_score"] == pytest.approx(1.0)

    namespace: dict[str, object] = {}
    exec(result.generate_blueprint(), namespace)
    transformed = namespace["FeatureExtractor"]().fit_transform(frame.drop(columns="target"))
    assert transformed.shape == (5, 1)
    assert np.isfinite(transformed).all()


def test_blueprint_configuration_is_rendered_from_reversede_config() -> None:
    categories = [f"level-{index}" for index in range(12)] * 5
    frame = pd.DataFrame(
        {
            "target": np.arange(len(categories), dtype=float),
            "category": categories,
        }
    )
    config = ReversedeConfig(
        max_features=1,
        high_cardinality_levels=5,
        max_categorical_levels=20,
        rare_category_fraction=0.02,
    )
    result = Reversede(frame, target="target", task="regression", config=config)
    namespace: dict[str, object] = {}
    exec(result.generate_blueprint(), namespace)
    assert namespace["CATEGORICAL_HIGH"] == ["category"]
    assert namespace["MIN_FREQUENCY"] == 0.02
    assert namespace["MAX_CATEGORIES"] == 20


def test_alert_newlines_cannot_escape_generated_comments() -> None:
    candidates = pd.DataFrame(
        [
            {
                "column": "feature\nname",
                "kind": "numeric",
                "selected": True,
                "unique_values": 4,
            }
        ]
    )
    stress = pd.DataFrame([{"column": "feature\nname", "iqr_outlier_fraction": 0.0}])
    code = generate_blueprint(
        candidates,
        stress,
        "target\nname",
        ["review this\nraise RuntimeError('must remain a comment')"],
        ReversedeConfig(),
    )
    namespace: dict[str, object] = {}
    exec(code, namespace)
    assert namespace["TARGET"] == "target\nname"
    assert namespace["NUMERIC_STANDARD"] == ["feature\nname"]


def test_nullable_dtypes_remain_json_serializable_and_input_is_unchanged() -> None:
    frame = pd.DataFrame(
        {
            "target": pd.Series([1.0, 2.0, 3.0, 4.0], dtype="Float64"),
            "nullable_integer": pd.Series([1, pd.NA, 3, 4], dtype="Int64"),
            "nullable_boolean": pd.Series([True, pd.NA, False, True], dtype="boolean"),
        }
    )
    before = frame.copy(deep=True)
    result = Reversede(frame, target="target", task="regression")
    json.dumps(result.summary(), ensure_ascii=False)
    pd.testing.assert_frame_equal(frame, before)
