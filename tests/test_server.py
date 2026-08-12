# Copyright (c) 2026 Franklin Baldo
"""Tests for the initial MCP surface."""

from fastmcp import Client

from suj.domain.status import SujStatus
from suj.mcp import build_mcp
from suj.settings import Settings
from suj.tools.status import DISCLAIMER


async def test_status_crosses_the_real_in_process_contract() -> None:
    """Schema, validation and structured content come from FastMCP."""
    server = build_mcp()

    async with Client(server) as client:
        tools = await client.list_tools()
        result = await client.call_tool("suj_status", {})

    assert [tool.name for tool in tools] == ["suj_status"]
    output_schema = tools[0].outputSchema
    assert output_schema is not None
    assert output_schema["type"] == "object"
    assert set(output_schema["required"]) == {
        "disclaimer",
        "network_enabled",
        "writes_enabled",
    }
    assert result.structured_content is not None
    status = SujStatus.model_validate(result.structured_content)
    assert status.disclaimer == DISCLAIMER
    assert status.network_enabled is False
    assert status.writes_enabled is False


async def test_two_builds_are_independent_and_structurally_identical() -> None:
    """There is no mutable server singleton or import-time registration."""
    first = build_mcp()
    second = build_mcp()

    assert first is not second
    async with Client(first) as first_client, Client(second) as second_client:
        first_tools = await first_client.list_tools()
        second_tools = await second_client.list_tools()

    assert [tool.model_dump() for tool in first_tools] == [
        tool.model_dump() for tool in second_tools
    ]


async def test_every_public_tool_has_a_typed_object_contract() -> None:
    """The catalog cannot grow a legacy dict, list or absent output schema."""
    async with Client(build_mcp()) as client:
        tools = await client.list_tools()

    assert tools
    for tool in tools:
        assert tool.outputSchema is not None, tool.name
        assert tool.outputSchema.get("type") == "object", tool.name
        assert tool.outputSchema.get("additionalProperties") is False, tool.name


async def test_explicit_settings_are_visible_without_enabling_effects() -> None:
    """Status reports flags; it does not interpret them as authorization."""
    server = build_mcp(Settings(network_enabled=True, writes_enabled=False))

    async with Client(server) as client:
        result = await client.call_tool("suj_status", {})

    status = SujStatus.model_validate(result.structured_content)
    assert status.network_enabled is True
    assert status.writes_enabled is False
