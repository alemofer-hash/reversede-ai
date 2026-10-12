from __future__ import annotations

import warnings

import numpy as np
import pandas as pd

from reverseda_ai import ReversedaAutonoma


def legacy_frame(n: int = 120) -> pd.DataFrame:
    rng = np.random.default_rng(12)
    return pd.DataFrame(
        {
            "default_12m": np.arange(n) % 2,
            "annual_income": rng.lognormal(10, 0.7, n),
            "segment": rng.choice(["A", "B", "C"], n),
            "customer_id": np.arange(n),
        }
    )


def test_legacy_constructor_attributes_and_blueprint() -> None:
    frame = legacy_frame()
    before = frame.copy(deep=True)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        result = ReversedaAutonoma(frame, max_features=3, id_columns=["customer_id"])
    assert any(item.category is DeprecationWarning for item in caught)
    assert result.target_ == "default_12m"
    assert result.task_ == "classification"
    assert result.mode_ == "supervisionado"
    assert "customer_id" not in result.variaveis_estimadas_
    assert {"feature", "included", "screening_score"}.issubset(result.requisitos_)
    assert "feature" in result.estresse_
    code = result.gerar_blueprint_extrator(imprimir=False)
    compile(code, "legacy_generated_blueprint.py", "exec")
    assert result.resumo()["target"] == "default_12m"
    pd.testing.assert_frame_equal(frame, before)


def test_legacy_explicit_exclusion_is_respected() -> None:
    frame = legacy_frame()
    frame["post_event"] = np.arange(len(frame))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        result = ReversedaAutonoma(
            frame,
            target="default_12m",
            exclude_columns=["post_event"],
        )
    row = result.requisitos_.set_index("feature").loc["post_event"]
    assert not bool(row["included"])
    assert "explicitly excluded" in row["reason"]
