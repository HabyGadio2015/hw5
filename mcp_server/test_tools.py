"""Protocol-level smoke test for the Campus Customs MCP server.

Spawns mcp_server/server.py exactly like an MCP client (e.g. the vibe coder,
per the root .mcp.json entry) would over stdio, and calls each of the 3
tools through the real MCP tool-call protocol — not by importing the
Python functions directly.
"""

import asyncio
from pathlib import Path

from fastmcp import Client

SERVER_PATH = Path(__file__).resolve().parent / "server.py"


async def main() -> None:
    async with Client(SERVER_PATH) as client:
        tools = await client.list_tools()
        print("Tools registered:", [t.name for t in tools])

        print("\nget_ticket(101):")
        print((await client.call_tool("get_ticket", {"ticket_id": 101})).data)

        print("\nget_ticket(999) [not found]:")
        print((await client.call_tool("get_ticket", {"ticket_id": 999})).data)

        print("\ncheck_inventory('CC-TEE-WHITE', 'S') [ticket 101, out of stock]:")
        print(
            (
                await client.call_tool(
                    "check_inventory", {"sku": "CC-TEE-WHITE", "size": "S"}
                )
            ).data
        )

        print("\ncheck_inventory('cc-hood-navy', 'm') [ticket 103, case-insensitive]:")
        print(
            (
                await client.call_tool(
                    "check_inventory", {"sku": "cc-hood-navy", "size": "m"}
                )
            ).data
        )

        print("\ncheck_inventory('CC-FAKE', 'S') [not found]:")
        print(
            (
                await client.call_tool("check_inventory", {"sku": "CC-FAKE", "size": "S"})
            ).data
        )

        print("\nget_shop_today() [ticket 102]:")
        print((await client.call_tool("get_shop_today", {})).data)


if __name__ == "__main__":
    asyncio.run(main())
