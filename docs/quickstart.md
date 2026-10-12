# Quickstart

The distribution name is `reversede-ai`; the Python import is `reversede`.

## 1. Select an interpreter

Use CPython 3.10–3.13. Local L1 validation was performed only with Python
3.12.10 on Windows; see `compatibility.md` before making broader claims.

Create an isolated environment:

```text
python -m venv .venv
python -m pip install --upgrade pip
python -m pip install -e ".[sklearn]"
```

The activation command differs by shell. VS Code and PyCharm can select the
`.venv` interpreter directly; Jupyter must use a kernel created from the same
environment. The library code does not change by IDE.

Use only `.` for the lightweight core, `[profiling]` for the optional report
adapter, or `[dev,sklearn]` for local development. Optional dependencies are
imported only when their features are called.

## 2. Run a minimal analysis

```python
import pandas as pd

from reversede import Reversede, ReversedeConfig

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
analysis.save_report("reversede-report")
analysis.generate_blueprint("reversede_blueprint.py")
```

The same example is available at `examples/quickstart.py` and requires no
network or external dataset.

## 3. Review the result

`Reversede` copies the input and does not train a final estimator. Its shortlist
is a reviewable screening hypothesis. Review:

- target and task source/confidence;
- every eligibility and rejection reason;
- ranking basis and original association metrics;
- stress diagnostics and model-conditioned prescriptions;
- generated source before execution.

Fit a generated sklearn blueprint only on training folds and evaluate it on
untouched data.

## Target omission

If `target` is omitted, Reversede may infer a column-name hypothesis with a
confidence and warning, or abstain. Inference never replaces the scientific or
business contract. With no adopted target, priority is structural and is not
predictive importance.

## Portuguese essentials

O nome da distribuição é `reversede-ai`, mas o import é `reversede`. Prefira
informar `target` e `task`. A seleção não demonstra causalidade. Ajuste qualquer
transformação apenas nos dados de treino e avalie em dados intocados.

## Environments not yet certified

Conda, Google Colab, and the full Windows/Linux/macOS matrix are later gates.
Do not treat this quickstart as evidence that those environments have already
been executed.
