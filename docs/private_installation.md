# Private installation and access

Repository: `https://github.com/alemofer-hash/reversede-ai`
Visibility: **Private**

Only the owner and GitHub accounts explicitly granted access can clone or
install this project. Accept the repository invitation before using the
commands below.

## Recommended authenticated HTTPS installation

Install Git and GitHub CLI, authenticate your own GitHub account, and connect
Git's credential helper:

```text
gh auth login
gh auth setup-git
python -m pip install "reversede-ai[sklearn] @ git+https://github.com/alemofer-hash/reversede-ai.git@v0.3.0-dev0"
python -c "from reversede import Reversede; print(Reversede)"
```

Pip supports the `ProjectName @ git+https://...@ref` direct-URL form. Pinning a
tag or full commit hash is reproducible; installing from a moving branch is not.

## SSH installation

After adding an SSH key to the authorized GitHub account:

```text
python -m pip install "reversede-ai[sklearn] @ git+ssh://git@github.com/alemofer-hash/reversede-ai.git@v0.3.0-dev0"
```

## Why plain `pip install reversede-ai` is not used

The bare command searches the configured Python package indexes, normally
public PyPI. This project is not published there. A private GitHub repository
therefore requires the authenticated direct URL above, or a separately operated
private Python package index. No private package index is part of this release.

## Clone the complete workspace

Cloning provides the notebooks, editor configuration, tests, documentation, and
environment recipes that are not installed as importable package modules:

```text
gh repo clone alemofer-hash/reversede-ai
cd reversede-ai
python -m venv .venv
python -m pip install -e ".[dev,sklearn,notebook]"
python scripts/verify_install.py
```

Use the shell-specific activation command for `.venv`, or point the IDE directly
at the environment interpreter.

## Google Colab

1. The GitHub account must already have repository access.
2. Create a fine-grained GitHub token restricted to this repository with
   read-only `Contents` permission.
3. Store it in Colab Secrets as `REVERSEDE_GITHUB_TOKEN`; never paste it into a
   code cell or save it in notebook output.
4. Upload and run `notebooks/00_colab_private_install.ipynb`.

The notebook passes authentication to Git only for the installation subprocess,
removes the temporary environment variables afterward, and never prints the
secret. Revoke the token when it is no longer needed.

## Access management

The repository owner grants and revokes collaborators in GitHub repository
settings. Revoking access prevents future remote fetches but cannot erase local
clones or files that a former collaborator already downloaded.
