# Copyright (c) 2026 Franklin Baldo
"""Errors whose public/private boundary is explicit."""


class SujError(Exception):
    """Base class for expected domain failures."""


class SafeSujError(SujError):
    """An expected failure whose message is deliberately safe for clients."""
