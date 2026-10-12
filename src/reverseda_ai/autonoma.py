"""Deprecated adapter from ``reverseda_ai`` to the Reversede public API."""

from __future__ import annotations

import warnings
from collections.abc import Sequence
from typing import Any

import pandas as pd

from reversede import Reversede, ReversedeConfig


class ReversedaAutonoma:
    """Compatibility shim for the 0.1.x constructor and public attributes."""

    def __init__(
        self,
        data: pd.DataFrame,
        target: str | None = None,
        *,
        task: str = "auto",
        max_features: int = 20,
        id_columns: Sequence[str] | None = None,
        exclude_columns: Sequence[str] | None = None,
        max_levels: int = 50,
        cat_high_cardinality: int = 25,
    ) -> None:
        warnings.warn(
            "reverseda_ai.ReversedaAutonoma is deprecated; migrate to "
            "reversede.Reversede and ReversedeConfig.",
            DeprecationWarning,
            stacklevel=2,
        )
        excluded = tuple(dict.fromkeys([*(id_columns or ()), *(exclude_columns or ())]))
        config = ReversedeConfig(
            max_features=max_features,
            max_categorical_levels=max_levels,
            high_cardinality_levels=cat_high_cardinality,
            exclude_columns=excluded,
        )
        self._analysis = Reversede(data, target=target, task=task, config=config)
        self.data_ = data.copy(deep=True)
        self.target_input_ = target
        self.target_ = self._analysis.target_
        self.target_confidence_ = self._analysis.target_confidence_
        self.target_candidates_ = self._analysis.target_candidates_
        self.task_ = self._analysis.task_ or "unsupervised"
        self.mode_ = "supervisionado" if self.target_ is not None else "nao_supervisionado"
        self.warnings_ = list(self._analysis.alerts_)
        self.variaveis_estimadas_ = list(self._analysis.selected_features_)
        self.requisitos_ = self._analysis.candidates_.rename(
            columns={
                "column": "feature",
                "selected": "included",
                "association_value": "association",
                "ranking_score": "screening_score",
            }
        ).copy(deep=True)
        self.estresse_ = self._analysis.stress_.rename(columns={"column": "feature"}).copy(
            deep=True
        )
        self.diagnostico_ = {
            "target": self.target_,
            "target_confidence": self.target_confidence_,
            "target_candidates": self.target_candidates_,
            "task": self.task_,
            "mode": self.mode_,
            "selected_features": self.variaveis_estimadas_,
            "warnings": self.warnings_,
        }

    def gerar_blueprint_extrator(self, *, imprimir: bool = True) -> str:
        """Return the new generated blueprint under the historical method name."""
        return self._analysis.generate_blueprint(print_code=imprimir)

    def resumo(self) -> dict[str, Any]:
        """Return a serializable compatibility summary."""
        return {
            **self.diagnostico_,
            "estimated_requirements": self.requisitos_.to_dict(orient="records"),
            "stress": self.estresse_.to_dict(orient="records"),
        }
