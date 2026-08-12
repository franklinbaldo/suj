# Copyright (c) 2026 Franklin Baldo
"""Tests for fail-closed process settings."""

import pytest
from pydantic import ValidationError

from suj.settings import Settings


def test_defaults_disable_all_external_effects(monkeypatch: pytest.MonkeyPatch) -> None:
    """A clean installation cannot access the network or write remotely."""
    monkeypatch.delenv("SUJ_NETWORK_ENABLED", raising=False)
    monkeypatch.delenv("SUJ_WRITES_ENABLED", raising=False)

    settings = Settings()

    assert settings.network_enabled is False
    assert settings.writes_enabled is False


def test_environment_uses_only_the_suj_prefix(monkeypatch: pytest.MonkeyPatch) -> None:
    """Non-secret configuration has one namespaced entry point."""
    monkeypatch.setenv("NETWORK_ENABLED", "true")
    monkeypatch.setenv("SUJ_NETWORK_ENABLED", "true")

    assert Settings().network_enabled is True


def test_invalid_boolean_fails_during_settings_construction(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Invalid configuration fails before a server is published."""
    monkeypatch.setenv("SUJ_NETWORK_ENABLED", "perhaps")

    with pytest.raises(ValidationError):
        Settings()
