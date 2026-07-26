from __future__ import annotations

import sys
import unittest
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "mcp/domain_server.py"


class McpProtocolTests(unittest.IsolatedAsyncioTestCase):
    async def test_controlled_domain_tool_over_stdio(self) -> None:
        parameters = StdioServerParameters(command=sys.executable, args=[str(SERVER)])
        async with stdio_client(parameters) as streams, ClientSession(*streams) as session:
            await session.initialize()
            result = await session.call_tool(
                "summarize_orders",
                {"category": "cobalt", "placed_on_or_after": "2026-03-01"},
            )
        self.assertFalse(result.isError)
        assert result.structuredContent
        self.assertEqual(result.structuredContent["order_count"], 1)
        self.assertEqual(result.structuredContent["revenue"], "48.00")


if __name__ == "__main__":
    unittest.main()
