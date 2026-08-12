# Copyright (c) 2026 Franklin Baldo
"""Prevent the initial Ruff exemption set from growing or changing identity."""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path

PYPROJECT = Path(__file__).parents[1] / "pyproject.toml"
ALLOWED_EXEMPTIONS = {
    ("global", "COM812"),
    ("global", "D203"),
    ("global", "D213"),
    ("tests/**/*.py", "S101"),
}


def configured_exemptions(source: str) -> set[tuple[str, str]]:
    """Read semantic global and per-file Ruff exemptions from TOML."""
    data = tomllib.loads(source)
    lint = data["tool"]["ruff"]["lint"]
    exemptions = {("global", selector) for selector in lint.get("ignore", [])}
    for scope, selectors in lint.get("per-file-ignores", {}).items():
        exemptions.update((scope, selector) for selector in selectors)
    return exemptions


def main() -> int:
    """Reject exemptions outside the reviewed bootstrap allowlist."""
    configured = configured_exemptions(PYPROJECT.read_text(encoding="utf-8"))
    unexpected = sorted(configured - ALLOWED_EXEMPTIONS)
    if unexpected:
        sys.stderr.write("Novas isenções Ruff são proibidas:\n")
        for scope, selector in unexpected:
            sys.stderr.write(f"  - {scope}: {selector}\n")
        return 1
    sys.stdout.write(f"Catraca Ruff: {len(configured)} isenções conhecidas; nenhuma nova.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
