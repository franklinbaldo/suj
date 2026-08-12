# Copyright (c) 2026 Franklin Baldo
"""Safety fixtures applied to the default test suite."""

import socket

import pytest


@pytest.fixture(autouse=True)
def _forbid_external_network(monkeypatch: pytest.MonkeyPatch) -> None:
    """Forbid DNS and outbound connections without breaking async loop internals."""

    def blocked(*_args: object, **_kwargs: object) -> None:
        msg = "External network access is forbidden in the default test suite."
        raise AssertionError(msg)

    monkeypatch.setattr(socket, "create_connection", blocked)
    monkeypatch.setattr(socket, "getaddrinfo", blocked)
