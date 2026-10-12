from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .blueprint import generate_blueprint
from .config import ReversedeConfig
from .prescriptions import build_prescriptions
from .profile import build_candidates, build_profile
from .stress import build_stress
from .target import infer_target, resolve_task
from .validation import validate_input

logger = logging.getLogger(__name__)


def _json_ready(value: Any) -> Any:
    if value is pd.NA or value is pd.NaT:
        return None
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_ready(item) for item in value]
    if isinstance(value, tuple):
        return [_json_ready(item) for item in value]
    if isinstance(value, (np.ndarray, pd.Index)):
        return [_json_ready(item) for item in value.tolist()]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        return None if pd.isna(value) or np.isinf(value) else float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if isinstance(value, (pd.Timestamp, np.datetime64)):
        return None if pd.isna(value) else pd.Timestamp(value).isoformat()
    if isinstance(value, (pd.Timedelta, np.timedelta64)):
        return None if pd.isna(value) else str(value)
    if isinstance(value, np.generic):
        return _json_ready(value.item())
    return value


class Reversede:
    """Profile a DataFrame and produce reviewable candidates and prescriptions."""

    def __init__(
        self,
        data: pd.DataFrame,
        target: str | None = None,
        task: str = "auto",
        config: ReversedeConfig | None = None,
    ) -> None:
        self.config = config or ReversedeConfig()
        validate_input(data, target, task, self.config)
        logger.debug(
            "Starting Reversede analysis rows=%d columns=%d target_supplied=%s task=%s",
            data.shape[0],
            data.shape[1],
            target is not None,
            task,
        )
        self._data = data.copy(deep=True)
        self.target_input_ = target
        self.target_candidates_: list[dict[str, Any]] = []
        self.alerts_: list[str] = []

        if target is not None:
            self.target_ = target
            self.target_confidence_ = 1.0
            self.target_source_ = "explicit"
        else:
            inferred, confidence, candidates = infer_target(self._data, self.config)
            self.target_ = inferred
            self.target_confidence_ = confidence
            self.target_candidates_ = candidates
            self.target_source_ = "inferred" if inferred is not None else "abstained"
            if inferred is None:
                self.alerts_.append(
                    "No target was adopted: structural priority is not predictive importance."
                )
            else:
                self.alerts_.append(
                    f"Target {inferred!r} was inferred heuristically; "
                    "confirm the business/scientific contract."
                )

        self.task_ = resolve_task(
            self._data[self.target_] if self.target_ is not None else None, task
        )
        self.task_source_ = "explicit" if task != "auto" else "heuristic"
        if task == "auto" and self.target_ is not None:
            self.alerts_.append(
                f"Task {self.task_!r} was inferred heuristically from target dtype/cardinality."
            )

        self.profile_ = build_profile(self._data)
        self.candidates_ = build_candidates(
            self._data, self.profile_, self.target_, self.task_, self.config
        )
        self.stress_ = build_stress(self._data, self.candidates_, self.config)
        self.prescriptions_ = build_prescriptions(self.candidates_, self.stress_, self.config)
        self.selected_features_ = self.candidates_.loc[
            self.candidates_["selected"], "column"
        ].tolist()
        if self.profile_["duplicate_rows_dataset"].max() > 0:
            self.alerts_.append("Duplicate rows were observed; inspect grouping and split leakage.")
        if self.candidates_["name_leakage_signal"].any():
            self.alerts_.append("Name-based leakage signals are warnings, not proof of leakage.")
        logger.debug(
            "Completed Reversede analysis mode=%s selected_features=%d alerts=%d",
            "supervised" if self.target_ is not None else "structural",
            len(self.selected_features_),
            len(self.alerts_),
        )

    def generate_blueprint(
        self, path: str | Path | None = None, *, print_code: bool = False
    ) -> str:
        code = generate_blueprint(
            self.candidates_,
            self.stress_,
            self.target_,
            self.alerts_,
            self.config,
        )
        compile(code, "reversede_blueprint.py", "exec")
        if path is not None:
            destination = Path(path)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(code, encoding="utf-8")
        if print_code:
            print(code)
        return code

    def summary(self) -> dict[str, Any]:
        mode = "supervised_screening" if self.target_ is not None else "structural_unsupervised"
        return _json_ready(
            {
                "mode": mode,
                "target": self.target_,
                "target_source": self.target_source_,
                "target_confidence": self.target_confidence_,
                "target_candidates": self.target_candidates_,
                "task": self.task_,
                "task_source": self.task_source_,
                "selected_features": self.selected_features_,
                "alerts": self.alerts_,
                "profile": self.profile_.to_dict(orient="records"),
                "candidates": self.candidates_.to_dict(orient="records"),
                "stress": self.stress_.to_dict(orient="records"),
                "prescriptions": self.prescriptions_.to_dict(orient="records"),
            }
        )

    def save_report(self, directory: str | Path) -> dict[str, str]:
        output = Path(directory)
        output.mkdir(parents=True, exist_ok=True)
        paths = {
            "profile": output / "reversede_profile.csv",
            "candidates": output / "reversede_candidates.csv",
            "stress": output / "reversede_stress.csv",
            "prescriptions": output / "reversede_prescriptions.csv",
            "summary": output / "reversede_summary.json",
            "blueprint": output / "reversede_blueprint.py",
        }
        self.profile_.to_csv(paths["profile"], index=False)
        self.candidates_.to_csv(paths["candidates"], index=False)
        self.stress_.to_csv(paths["stress"], index=False)
        self.prescriptions_.to_csv(paths["prescriptions"], index=False)
        paths["summary"].write_text(
            json.dumps(self.summary(), indent=2, ensure_ascii=False), encoding="utf-8"
        )
        self.generate_blueprint(paths["blueprint"])
        return {key: str(value) for key, value in paths.items()}
