"""Minimal synthetic Reversede example; no external data or network required."""

from __future__ import annotations

import pandas as pd

from reversede import Reversede, ReversedeConfig


def main() -> None:
    frame = pd.DataFrame(
        {
            "temperature": [12.1, 18.4, 22.0, 28.7, 31.2, 37.6],
            "pressure": [1.0, 1.2, 1.1, 1.5, 1.7, 1.9],
            "family": ["a", "a", "b", "b", "c", "c"],
            "critical_temp": [4.0, 6.1, 7.8, 10.2, 12.0, 14.5],
        }
    )
    analysis = Reversede(
        frame,
        target="critical_temp",
        task="regression",
        config=ReversedeConfig(max_features=3),
    )
    print(analysis.selected_features_)
    print(analysis.summary()["alerts"])


if __name__ == "__main__":
    main()
