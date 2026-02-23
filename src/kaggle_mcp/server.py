"""Kaggle MCP Server - main entry point."""

from mcp.server.fastmcp import FastMCP

from . import competitions, datasets, discussions, kernels, models

mcp = FastMCP("kaggle")

# Register all tool modules
competitions.register(mcp)
datasets.register(mcp)
kernels.register(mcp)
models.register(mcp)
discussions.register(mcp)


def main() -> None:
    """Run the MCP server."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
