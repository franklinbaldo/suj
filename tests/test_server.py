# Copyright (c) 2026 Franklin Baldo
"""Tests for the initial MCP surface."""

from suj.server import DISCLAIMER, suj_status


def test_status_is_explicitly_experimental() -> None:
    """The public status must make the project's risk explicit."""
    result = suj_status()

    assert result == {"status": "experimental", "disclaimer": DISCLAIMER}
    assert "Não use em processos reais" in result["disclaimer"]
