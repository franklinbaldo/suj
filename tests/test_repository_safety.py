# Copyright (c) 2026 Franklin Baldo
"""Repository-wide privacy invariants for versioned fixtures."""

import re
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).parents[1]
SCANNED_SUFFIXES = {".json", ".md", ".py", ".toml", ".yaml", ".yml"}
JWT_PATTERN = re.compile(r"eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]+")


def test_versioned_corpus_contains_no_jwt() -> None:
    """A pasted Bearer token must fail the default test suite."""
    matches: list[str] = []
    for path in WORKSPACE_ROOT.rglob("*"):
        if path.is_file() and path.suffix in SCANNED_SUFFIXES and ".venv" not in path.parts:
            content = path.read_text(encoding="utf-8")
            if JWT_PATTERN.search(content):
                matches.append(str(path.relative_to(WORKSPACE_ROOT)))

    assert matches == []
