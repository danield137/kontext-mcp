"""
Tool registration for Kontext MCP server.
"""

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from kontext_mcp import tools


def register_tools(mcp: FastMCP) -> None:
    """Register Kontext tools with the MCP server."""

    mcp.add_tool(
        tools.remember,
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True),
    )

    mcp.add_tool(
        tools.recall,
        annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False),
    )
