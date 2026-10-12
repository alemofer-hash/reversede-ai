"""Validate repository portability assets without extra parser dependencies."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    ".editorconfig",
    ".gitattributes",
    ".devcontainer/devcontainer.json",
    ".vscode/extensions.json",
    ".vscode/settings.json",
    ".vscode/tasks.json",
    "environment.yml",
    "requirements/core.txt",
    "requirements/notebook.txt",
    "requirements/dev.txt",
    "notebooks/00_colab_private_install.ipynb",
    "notebooks/01_quickstart.ipynb",
)
SECRET_PATTERNS = (
    re.compile(r"\bghp_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY"),
)


def main() -> None:
    missing = [relative for relative in REQUIRED if not (ROOT / relative).is_file()]
    if missing:
        raise SystemExit(f"missing portable assets: {missing}")

    for relative in REQUIRED:
        path = ROOT / relative
        text = path.read_text(encoding="utf-8")
        if any(pattern.search(text) for pattern in SECRET_PATTERNS):
            raise SystemExit(f"secret-shaped value found in {relative}")
        if path.suffix == ".json":
            json.loads(text)

    for notebook_path in sorted((ROOT / "notebooks").glob("*.ipynb")):
        notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
        if notebook.get("nbformat") != 4:
            raise SystemExit(f"unsupported notebook format: {notebook_path.name}")
        for cell in notebook.get("cells", []):
            if cell.get("cell_type") == "code":
                if cell.get("execution_count") is not None or cell.get("outputs"):
                    raise SystemExit(f"stored execution output in {notebook_path.name}")
                source = "".join(cell.get("source", []))
                compile(source, notebook_path.name, "exec")

    print(f"portable-assets: ok ({len(REQUIRED)} required files)")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"portable-assets: failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
