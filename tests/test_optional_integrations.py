from __future__ import annotations

import builtins

import pandas as pd
import pytest

from reversede.integrations.profiling import profile_with_ydata


def test_profiling_adapter_has_clear_missing_extra_error(monkeypatch: pytest.MonkeyPatch) -> None:
    original_import = builtins.__import__

    def guarded_import(name: str, *args: object, **kwargs: object) -> object:
        if name == "ydata_profiling":
            raise ImportError("simulated optional dependency absence")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    with pytest.raises(ImportError, match="profiling.*extra"):
        profile_with_ydata(pd.DataFrame({"x": [1, 2]}), minimal=True)
