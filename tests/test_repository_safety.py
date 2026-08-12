# Copyright (c) 2026 Franklin Baldo
"""Repository-wide privacy invariants for versioned fixtures."""

import re
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).parents[1]
SCANNED_SUFFIXES = {".json", ".md", ".py", ".toml", ".yaml", ".yml"}
JWT_PATTERN = re.compile(r"eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]+")
SECRET_PATTERNS = {
    "jwt": JWT_PATTERN,
    "private-key": re.compile("-----BEGIN " + r"(?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "github-token": re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
    "generic-api-key": re.compile(r"(?i)(?:api[_-]?key|secret[_-]?key)\s*[=:]\s*['\"][^'\"]{12,}"),
}


def test_versioned_corpus_contains_no_secret_patterns() -> None:
    """Pasted credentials and private keys must fail the default suite."""
    matches: list[str] = []
    for path in WORKSPACE_ROOT.rglob("*"):
        if path.is_file() and path.suffix in SCANNED_SUFFIXES and ".venv" not in path.parts:
            content = path.read_text(encoding="utf-8")
            for label, pattern in SECRET_PATTERNS.items():
                if pattern.search(content):
                    matches.append(f"{path.relative_to(WORKSPACE_ROOT)}: {label}")

    assert matches == []
