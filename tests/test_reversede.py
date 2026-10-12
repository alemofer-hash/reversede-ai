from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from reversede import Reversede, ReversedeConfig


def regression_frame(n: int = 160, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    x = rng.normal(size=n)
    return pd.DataFrame(
        {
            "critical_temp": 15 + 4 * x + rng.normal(scale=0.4, size=n),
            "signal": x,
            "noise": rng.normal(size=n),
            "batch": rng.choice(["a", "b", "rare"], size=n, p=[0.60, 0.38, 0.02]),
        }
    )


def test_numeric_target_regression_and_original_metrics_are_kept() -> None:
    result = Reversede(regression_frame(), target="critical_temp", task="regression")
    row = result.candidates_.set_index("column").loc["signal"]
    assert result.task_ == "regression"
    assert row["association_metric"] == "abs_pearson"
    assert row["secondary_metric"] == "abs_spearman"
    assert row["ranking_score"] > 0.9
    assert row["valid_n"] == 160


@pytest.mark.parametrize("classes", [2, 3])
def test_binary_and_multiclass_targets(classes: int) -> None:
    rng = np.random.default_rng(5)
    y = np.arange(120) % classes
    labels = np.array(["alpha", "beta", "gamma"])
    frame = pd.DataFrame(
        {"label": y, "numeric": y + rng.normal(0, 0.1, 120), "category": labels[y]}
    )
    result = Reversede(frame, target="label", task="classification")
    assert result.task_ == "classification"
    assert set(result.candidates_["association_metric"].dropna()) >= {"eta_squared", "cramers_v"}


def test_named_target_is_inferred_with_warning() -> None:
    result = Reversede(regression_frame(), task="auto")
    assert result.target_ == "critical_temp"
    assert result.target_source_ == "inferred"
    assert 0.88 <= result.target_confidence_ < 1
    assert any("inferred heuristically" in warning for warning in result.alerts_)


def test_ambiguous_target_abstains_and_is_structural() -> None:
    frame = regression_frame().rename(columns={"critical_temp": "outcome"})
    frame["target"] = frame["outcome"]
    result = Reversede(frame)
    assert result.target_ is None
    assert result.target_source_ == "abstained"
    assert len(result.target_candidates_) == 2
    assert result.candidates_["selection_basis"].str.contains("not predictive").any()


def test_no_target_name_uses_structural_priority() -> None:
    frame = regression_frame().rename(columns={"critical_temp": "measurement"})
    result = Reversede(frame)
    assert result.target_ is None
    assert set(result.candidates_.loc[result.candidates_["eligible"], "association_metric"]) == {
        "structural_priority"
    }


def test_constant_id_rare_null_infinite_numeric_string_date_and_text() -> None:
    frame = regression_frame(120)
    frame["constant"] = 1
    frame["record_id"] = np.arange(len(frame))
    frame["numeric_as_text"] = [str(value) for value in np.arange(len(frame))]
    frame.loc[0, "numeric_as_text"] = None
    frame["event_date"] = pd.date_range("2020-01-01", periods=len(frame)).astype(str)
    frame["free_text"] = [
        f"long descriptive sentence for sample number {i}" for i in range(len(frame))
    ]
    frame["batch"] = np.where(
        np.arange(len(frame)) == 0, "rare", np.where(np.arange(len(frame)) % 2, "a", "b")
    )
    frame.loc[0, "signal"] = np.inf
    frame.loc[1, "signal"] = np.nan
    result = Reversede(
        frame, target="critical_temp", task="regression", config=ReversedeConfig(max_features=20)
    )
    candidates = result.candidates_.set_index("column")
    assert not bool(candidates.loc["constant", "eligible"])
    assert not bool(candidates.loc["record_id", "eligible"])
    assert not bool(candidates.loc["free_text", "eligible"])
    assert candidates.loc["numeric_as_text", "kind"] == "numeric_string"
    assert candidates.loc["event_date", "kind"] == "datetime"
    stress = result.stress_.set_index("column")
    assert stress.loc["signal", "infinite_count"] == 1
    assert stress.loc["signal", "null_count"] == 1
    assert stress.loc["batch", "rare_level_count"] >= 1


def test_duplicate_rows_are_alerted() -> None:
    frame = regression_frame(30)
    frame = pd.concat([frame, frame.iloc[[0]]], ignore_index=True)
    result = Reversede(frame, target="critical_temp", task="regression")
    assert any("Duplicate rows" in warning for warning in result.alerts_)


def test_empty_dataframe_rejected() -> None:
    with pytest.raises(ValueError, match="non-empty"):
        Reversede(pd.DataFrame())


def test_duplicate_columns_rejected() -> None:
    frame = pd.DataFrame([[1, 2], [3, 4]], columns=["x", "x"])
    with pytest.raises(ValueError, match="duplicate column"):
        Reversede(frame)


def test_missing_or_degenerate_target_rejected() -> None:
    with pytest.raises(ValueError, match="not found"):
        Reversede(regression_frame(), target="missing")
    frame = regression_frame()
    frame["only"] = 1
    with pytest.raises(ValueError, match="two distinct"):
        Reversede(frame, target="only")


def test_invalid_arguments_rejected() -> None:
    with pytest.raises(ValueError, match="task"):
        Reversede(regression_frame(), task="clustering")
    with pytest.raises(ValueError, match="max_features"):
        Reversede(regression_frame(), config=ReversedeConfig(max_features=0))


def test_input_is_not_mutated() -> None:
    frame = regression_frame()
    before = frame.copy(deep=True)
    result = Reversede(frame, target="critical_temp", task="regression")
    result.profile_.loc[:, "column"] = "changed"
    pd.testing.assert_frame_equal(frame, before)


def test_blueprint_compiles_and_smoke_fits_without_target() -> None:
    frame = regression_frame()
    result = Reversede(
        frame, target="critical_temp", task="regression", config=ReversedeConfig(max_features=4)
    )
    code = result.generate_blueprint()
    compile(code, "generated_blueprint.py", "exec")
    namespace: dict[str, object] = {}
    exec(code, namespace)
    extractor = namespace["FeatureExtractor"]()
    transformed_train = extractor.fit_transform(
        frame.iloc[:100].drop(columns="critical_temp"), frame.iloc[:100]["critical_temp"]
    )
    transformed_test = extractor.transform(frame.iloc[100:].drop(columns="critical_temp"))
    assert transformed_train.shape[0] == 100
    assert transformed_test.shape[0] == len(frame) - 100
    assert "critical_temp" not in result.selected_features_


def test_summary_is_json_serializable(tmp_path) -> None:
    result = Reversede(regression_frame(), target="critical_temp", task="regression")
    paths = result.save_report(tmp_path)
    assert set(paths) == {
        "profile",
        "candidates",
        "stress",
        "prescriptions",
        "summary",
        "blueprint",
    }
    assert (tmp_path / "reversede_summary.json").is_file()
