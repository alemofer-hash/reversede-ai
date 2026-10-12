# API reference

## `Reversede(data, target=None, task="auto", config=None)`

Analyzes a non-empty pandas `DataFrame` without mutating it. `target` must name
an existing non-degenerate column when supplied. `task` accepts `auto`,
`regression` or `classification`.

Stable review surfaces after construction:

- `target_`, `target_source_`, `target_confidence_`, `target_candidates_`;
- `task_`, `task_source_`, `alerts_`;
- `profile_`, `candidates_`, `stress_`, `prescriptions_`;
- `selected_features_`.

Methods:

- `summary()` returns JSON-ready Python values;
- `save_report(directory)` writes CSV, JSON and blueprint artifacts;
- `generate_blueprint(path=None, print_code=False)` compiles the generated
  source before returning it and optionally persists it.

Construction performs profiling and prescription generation, not estimator
training. Debug logs contain dimensions and state counts only, never cell
values.

## `ReversedeConfig`

Frozen typed configuration with thresholds for shortlist size, categorical
cardinality, near constants, likely identifiers, target confidence/margin,
rare categories, outliers, and explicit include/exclude lists. Invalid ranges
raise `ValueError`. Blueprint generation uses the configured outlier threshold,
high-cardinality boundary, maximum categorical levels, and rare-category
frequency. Configuration is therefore part of the generated source contract.

## Optional profiling adapter

```python
from reversede.integrations.profiling import profile_with_ydata

report = profile_with_ydata(frame, "profile.html", minimal=True)
```

This import is lightweight. Calling the function without the `profiling` extra
raises an actionable `ImportError`.

## Historical compatibility

`reverseda_ai.ReversedaAutonoma` remains as a narrow adapter for 0.1.x callers
and emits `DeprecationWarning`. New code must use `reversede.Reversede`; see
`migration.md`.
