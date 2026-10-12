# Migration from 0.1.x and 0.2.0

## New public API

```python
from reversede import Reversede, ReversedeConfig

analysis = Reversede(
    frame,
    target="critical_temp",
    task="regression",
    config=ReversedeConfig(max_features=30, exclude_columns=("material",)),
)
code = analysis.generate_blueprint(print_code=False)
```

The historical call remains temporarily available:

```python
from reverseda_ai import ReversedaAutonoma

legacy = ReversedaAutonoma(frame, target="critical_temp", max_features=30)
code = legacy.gerar_blueprint_extrator(imprimir=False)
```

It emits `DeprecationWarning`. Attribute translations are covered by tests;
new concepts and report schemas use English names. The adapter is for migration,
not a second brand or a promise that every undocumented 0.1.x behavior remains.

From 0.2.0 to 0.3.0.dev0, the core contract is retained. Extras were separated,
the optional profiling adapter and logging were added, and local packaging
gates were formalized. The `.dev0` version denotes an unpublished candidate.
