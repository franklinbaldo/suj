# Copyright (c) 2026 Franklin Baldo
"""Translation of deliberately public domain errors to MCP errors."""

from fastmcp.exceptions import ToolError

from suj.domain.errors import SafeSujError


def public_error(error: SafeSujError) -> ToolError:
    """Expose only an error explicitly classified as safe by the domain."""
    return ToolError(str(error))
