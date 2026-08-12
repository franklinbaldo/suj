# Copyright (c) 2026 Franklin Baldo
"""Console entrypoint for suj."""

from suj.mcp import build_mcp


def main() -> None:
    """Build and run the suj MCP server over stdio."""
    build_mcp().run()


if __name__ == "__main__":
    main()
