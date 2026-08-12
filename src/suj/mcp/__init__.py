# Copyright (c) 2026 Franklin Baldo
"""Explicit FastMCP composition root."""

from fastmcp import FastMCP

from suj.settings import Settings
from suj.tools.status import DISCLAIMER, build_status_tool


def build_mcp(settings: Settings | None = None) -> FastMCP:
    """Build a fresh, independent server with an explicit catalog."""
    resolved_settings = settings or Settings()
    return FastMCP(
        name="suj",
        instructions=DISCLAIMER,
        tools=[build_status_tool(resolved_settings)],
        on_duplicate="error",
        mask_error_details=True,
    )


__all__ = ["build_mcp"]
