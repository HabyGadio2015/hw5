"""Shared helper for calling campus-customs MCP tools directly from a route
handler (not through an agent run). Uses fastmcp's in-memory transport —
the same FastMCP server object, no subprocess — so this is still a real MCP
tool call, not a second shop-tools layer that bypasses MCP.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from fastmcp import Client

from mcp_server.server import mcp as campus_mcp


@asynccontextmanager
async def mcp_client() -> AsyncIterator[Client]:
    async with Client(campus_mcp) as client:
        yield client


async def call_tool(name: str, args: dict[str, Any]) -> Any:
    async with mcp_client() as client:
        result = await client.call_tool(name, args)
        return result.data
