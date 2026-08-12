# Copyright (c) 2026 Franklin Baldo
"""Tests for the MCP error boundary."""

from fastmcp import Client, FastMCP

from suj.domain.errors import SafeSujError
from suj.mcp.errors import public_error


async def test_unexpected_error_is_masked_on_the_wire() -> None:
    """Internal exception details never become tool output."""

    def fail_unexpectedly() -> str:
        msg = "internal-secret-detail"
        raise RuntimeError(msg)

    server = FastMCP(tools=[fail_unexpectedly], mask_error_details=True)
    async with Client(server) as client:
        result = await client.call_tool("fail_unexpectedly", {}, raise_on_error=False)

    assert result.is_error is True
    assert "internal-secret-detail" not in str(result.content)


async def test_deliberately_safe_error_remains_actionable() -> None:
    """Only explicitly classified messages are exposed to the caller."""

    def fail_safely() -> str:
        error = SafeSujError("A entrada sintética não é suportada.")
        raise public_error(error) from error

    server = FastMCP(tools=[fail_safely], mask_error_details=True)
    async with Client(server) as client:
        result = await client.call_tool("fail_safely", {}, raise_on_error=False)

    assert result.is_error is True
    assert "A entrada sintética não é suportada." in str(result.content)
