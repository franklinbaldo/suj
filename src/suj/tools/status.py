# Copyright (c) 2026 Franklin Baldo
"""Offline status capability."""

from collections.abc import Callable

from suj.domain.status import SujStatus
from suj.settings import Settings

DISCLAIMER = (
    "Integração não oficial, experimental e potencialmente insegura. Não use em processos reais."
)


def build_status_tool(settings: Settings) -> Callable[[], SujStatus]:
    """Bind immutable process settings without global registration."""

    def suj_status() -> SujStatus:
        """Return project status without accessing any external service."""
        return SujStatus(
            disclaimer=DISCLAIMER,
            network_enabled=settings.network_enabled,
            writes_enabled=settings.writes_enabled,
        )

    return suj_status
