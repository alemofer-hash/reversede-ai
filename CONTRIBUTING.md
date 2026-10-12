# Contributing to the private Reversede candidate

This directory is a local private-library candidate. It is not a Git
repository and has no configured remote.

1. Create an isolated Python 3.10+ environment.
2. Install `pip install -e ".[dev,sklearn]"`.
3. Run `ruff check src tests` and `ruff format --check src tests`.
4. Run `pytest --cov=reversede --cov=reverseda_ai`.
5. Build with `python -m build` and validate with `twine check dist/*`.
6. Install the resulting wheel in an isolated environment with `--no-index`
   and `--no-deps` when dependencies are already available locally.

Tests must distinguish descriptive evidence, screening hypotheses, and model
performance. Never open a frozen holdout while tuning. Do not include raw
external data, secrets, local absolute paths, virtual environments, generated
profiling reports, supplied documents, or scientific outputs. Public API
changes require migration notes and compatibility tests.

Use the allowlist in `provenance/INCLUSION_POLICY.md`. Do not initialize Git or
publish this project without separate authorization. Do not alter authorship,
copyright, or license metadata automatically.
