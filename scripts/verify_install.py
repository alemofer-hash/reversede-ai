"""Portable installed-package smoke test with synthetic data only."""

from __future__ import annotations

import json

import pandas as pd

import reversede
from reversede import Reversede


def main() -> None:
    frame = pd.DataFrame(
        {
            "temperature": [8.0, 12.0, 17.0, 21.0, 26.0, 31.0],
            "pressure": [1.0, 1.1, 1.2, 1.4, 1.5, 1.7],
            "family": ["a", "a", "b", "b", "c", "c"],
            "target": [0.0, 0.8, 1.7, 2.2, 3.4, 4.1],
        }
    )
    analysis = Reversede(frame, target="target", task="regression")
    payload = {
        "version": reversede.__version__,
        "target": analysis.target_,
        "selected_features": analysis.selected_features_,
        "status": "ok",
    }
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
