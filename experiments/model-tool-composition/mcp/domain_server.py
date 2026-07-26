#!/usr/bin/env python3
"""MCP server for the controlled Norvale Commerce domain."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

COMMON = Path(__file__).resolve().parents[1] / "common"
sys.path.insert(0, str(COMMON))

from domain import get_return_policy as domain_get_return_policy
from domain import summarize_orders as domain_summarize_orders
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Norvale Commerce controlled domain")


@mcp.tool()
def summarize_orders(
    category: str | None = None, placed_on_or_after: str | None = None
) -> dict[str, Any]:
    """Summarize orders, optionally filtering category and inclusive ISO start date."""
    return domain_summarize_orders(category, placed_on_or_after)


@mcp.tool()
def get_return_policy(category: str) -> dict[str, Any]:
    """Retrieve the fictional return policy for one category."""
    return domain_get_return_policy(category)


if __name__ == "__main__":
    mcp.run(transport="stdio")
