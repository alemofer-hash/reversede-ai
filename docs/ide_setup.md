# IDE and notebook setup

Reversede uses standard Python packaging. The IDE is only a client of the chosen
Python environment; there is no IDE-specific runtime implementation.

## Universal local workflow

From the repository root:

```text
python -m venv .venv
python -m pip install -e ".[dev,sklearn,notebook]"
python scripts/verify_install.py
python -m pytest -ra
```

Select `.venv` as the project interpreter or Jupyter kernel.

## VS Code

Open the repository folder. The committed `.vscode/` files recommend Python,
Pylance, Ruff, and Jupyter extensions and expose verification/test tasks. On
Windows the interpreter hint points to `.venv/Scripts/python.exe`; on Linux or
macOS choose `.venv/bin/python` with **Python: Select Interpreter**.

The `.devcontainer/` definition offers a reproducible Python 3.12 Linux
development container when Docker and the Dev Containers extension are present.

## PyCharm

Open the repository, choose **Add Interpreter > Existing**, and select:

- Windows: `.venv/Scripts/python.exe`
- Linux/macOS: `.venv/bin/python`

PyCharm reads `pyproject.toml` for the package and pytest configuration. Do not
commit `.idea/`; it contains machine- and user-specific state.

## JupyterLab and classic Jupyter

```text
python -m ipykernel install --user --name reversede --display-name "Python (Reversede)"
python -m jupyter lab
```

Open `notebooks/01_quickstart.ipynb` and select **Python (Reversede)**.

## Anaconda or Miniconda

```text
conda env create --file environment.yml
conda activate reversede
python scripts/verify_install.py
```

The Conda file fixes Python 3.12 for a stable shared baseline while the package
itself declares CPython 3.10–3.13. Solver output can differ over time; export an
explicit platform lock separately when bit-for-bit environment reproduction is
required.

## Other editors and CI systems

Any editor or CI runner that can select a CPython 3.10–3.13 interpreter and run
PEP 517/pip projects can use the same commands. `.editorconfig` and
`.gitattributes` provide editor-neutral whitespace and line-ending rules.
