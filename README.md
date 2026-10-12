# Reversede

Reversede is a private Python library candidate for auditable DataFrame
profiling, feature-screening hypotheses, stress diagnostics, model-conditioned
prescriptions, and generation of a scikit-learn preprocessing blueprint.

The distribution name is `reversede-ai`; the import is `reversede`. The current
version is `0.3.0.dev0`. Its GitHub repository is private: only the owner and
explicitly authorized collaborators can fetch the source or install from it.

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
```

## What it does

Reversede:

- validates and deep-copies a non-empty pandas DataFrame;
- accepts an explicit target or may propose one with confidence and abstention;
- infers practical column types with traceable evidence;
- retains eligibility and rejection reasons for every column;
- ranks eligible columns using task-conditioned univariate screening or a
  target-free structural priority;
- records missingness, outlier, scale, cardinality, date, and collinearity
  stress evidence;
- emits reviewable prescriptions and an unfitted sklearn-compatible blueprint.

It does not select a final estimator, prove causality, prove the absence of
leakage, or guarantee that a shortlist improves prediction. Fit generated
transformations only on training folds and evaluate on untouched data.

## Install from the private GitHub repository

After accepting access and authenticating Git with your own GitHub account:

```text
gh auth login
gh auth setup-git
python -m pip install "reversede-ai[sklearn] @ git+https://github.com/alemofer-hash/reversede-ai.git@v0.3.0-dev0"
```

The bare command `pip install reversede-ai` would search public package indexes;
this private release intentionally uses an authenticated Git URL instead. See
[private installation and access](docs/private_installation.md), including SSH
and Google Colab instructions.

## Technical reference PDF

The complete private reference manual covers the algorithm, pseudocode, public
API, parameters, generated blueprints, portability, reproducibility, and
scientific boundaries: [Reversede Technical Reference and Operating Guide](docs/pdf/reversede_reference.pdf).
The editable LaTeX source is kept at
[`docs/latex/reversede_reference.tex`](docs/latex/reversede_reference.tex).

## Local development installation

Create an isolated environment with a supported CPython version:

```text
python -m venv .venv
python -m pip install -e ".[dev,sklearn,notebook]"
python scripts/verify_install.py
```

Activation syntax is shell-specific, but installation and Python code are not
IDE-specific. See [the quickstart](docs/quickstart.md) and
[compatibility status](docs/compatibility.md).

Portable workspace assets include:

- `environment.yml` for Conda/Anaconda;
- standard virtual-environment and requirements recipes;
- VS Code settings/tasks and an optional development container;
- PyCharm, Jupyter, Colab, and editor-neutral instructions;
- private-install and synthetic quickstart notebooks under `notebooks/`.

Extras:

- core: NumPy and pandas only;
- `sklearn`: execute generated blueprints;
- `profiling`: optional ydata-profiling adapter;
- `analysis`: plotting/scientific utilities for separate studies;
- `notebook`: JupyterLab, ipykernel, and blueprint execution;
- `test`: pytest;
- `dev`: local build, lint, coverage, and metadata tools.

## Development checks

Using an existing compatible environment:

```text
python -m pytest --cov=reversede --cov=reverseda_ai
ruff check src tests examples scripts
ruff format --check src tests examples scripts
python scripts/validate_portable_assets.py
python -m build
python -m twine check dist/*
```

The L1 candidate was validated locally on Windows with Python 3.12. The private
repository workflow validates the declared Windows/Linux/macOS and Python
3.10–3.13 matrix; consult [compatibility status](docs/compatibility.md) for the
latest executed evidence instead of inferring support from configuration alone.

## Provenance boundary

This library tree was created from an allowlist. It intentionally excludes raw
datasets, supplied PDFs, study notebooks, scientific predictions, frozen holdouts,
virtual environments, caches, generated reports, and manuscript builds. The
source-study snapshot is recorded under `provenance/` without copying those
materials into this tree. The included notebooks use synthetic data only.

The current MIT file and authorship metadata are preserved from the source
candidate. They are not, by themselves, proof of exclusive authorship or a
completed rights review. See [licensing and provenance](docs/licensing_and_provenance.md)
and [the inclusion policy](provenance/INCLUSION_POLICY.md).

## Scientific boundary

The superconductivity study was executed with Reversede `0.2.0`. This library
candidate is `0.3.0.dev0`; historical results are not automatically attributed
to the newer code. The study remains in its preserved source directory and was
not rerun or modified during private-library hardening.

## Private status

The GitHub destination is private. Access, collaborator invitations, visibility
changes, package-index publication, and any public disclosure remain controlled
by the repository owner. This version is installable from authenticated Git but
is not published to PyPI, TestPyPI, conda-forge, Zenodo, or another public index.
