# Copyright (c) 2026 Franklin Baldo
"""MCP entrypoint for suj."""

from typing import Final

from fastmcp import FastMCP

DISCLAIMER: Final = (
    "Integração não oficial, experimental e potencialmente insegura. Não use em processos reais."
)

mcp = FastMCP(
    name="suj",
    instructions=DISCLAIMER,
)


@mcp.tool()
def suj_status() -> dict[str, str]:
    """Return project status without accessing any external service."""
    return {"status": "experimental", "disclaimer": DISCLAIMER}


def main() -> None:
    """Run the suj MCP server over stdio."""
    mcp.run()


if __name__ == "__main__":
    main()
