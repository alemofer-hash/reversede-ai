# Private repository publication report

Date: 2026-10-12

## Repository state

- repository: `https://github.com/alemofer-hash/reversede-ai`;
- visibility: `PRIVATE`;
- default branch: `main`;
- owner permission: `ADMIN`;
- public package-index publication: none;
- GitHub Release publication: none;
- vulnerability alerts: enabled;
- automated security fixes: enabled;
- head branches are deleted automatically after merge.

The repository can be read, cloned, or installed only by the owner and GitHub
accounts to which the owner explicitly grants access. Removing access blocks
future remote fetches but cannot retract copies already downloaded.

## Installation contract

Authorized users install the tagged candidate with an authenticated VCS direct
URL:

```text
gh auth login
gh auth setup-git
python -m pip install "reversede-ai[sklearn] @ git+https://github.com/alemofer-hash/reversede-ai.git@v0.3.0-dev0"
```

The distribution name remains `reversede-ai` and the import remains
`reversede`. Plain `pip install reversede-ai` is intentionally unavailable
because it would require a configured private package index or public PyPI
publication. The repository is the private package source.

## Portable assets

- standard `pyproject.toml` packaging for CPython 3.10–3.13;
- `environment.yml` for Conda/Anaconda;
- pip requirement profiles for core, notebook, and development use;
- VS Code settings and tasks plus an optional Linux development container;
- PyCharm, Jupyter, Colab, and editor-neutral instructions;
- a secure Colab private-install notebook with no embedded credential;
- a synthetic quickstart notebook with no private data or stored output;
- portable verification and asset-validation scripts.

## Validation evidence

- local suite: 23 tests passed;
- local Ruff lint and format checks: passed;
- local synthetic Jupyter execution: four code cells, zero error outputs;
- local wheel and sdist: built, metadata-checked, installed, and smoke-tested;
- archive audit: no private data, PDF, personal path, cache, environment, or
  common secret-shaped value;
- first private GitHub Actions publication run: successful across Windows,
  Ubuntu, macOS and Python 3.10–3.13, including core-only, notebook, quality,
  build, metadata, test, and coverage jobs.

The workflow contains no package upload, public release, visibility change, or
deployment step.

## Local artifact hashes

- wheel SHA-256:
  `d9a5847c7c127232577f6df1e033b421853557e676d2138b3a09231af317088c`;
- sdist SHA-256:
  `985a27e390811629852e035239b4551f817f09eb5319e97ec15d5e7e3d5b213d`.

These local files are validation artifacts, not uploaded package releases.

## Remaining boundaries

- Google Colab and Conda recipes are prepared but were not executed against
  those hosted runtimes in this publication task;
- the development container definition was not built locally;
- bit-for-bit builds across operating systems are not claimed;
- no public index, mirror, release, article, dataset, or scientific result was
  published;
- authorship, copyright, and third-party provenance remain subject to the
  documented human review before any public disclosure.
