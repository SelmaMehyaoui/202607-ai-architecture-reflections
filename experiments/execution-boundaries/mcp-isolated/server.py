#!/usr/bin/env python3
"""Container MCP server with paths fixed to its narrow mounts."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from time import perf_counter_ns
from typing import Any

sys.path.insert(0, "/app/common")
from mcp.server.fastmcp import FastMCP
from summarize import summarize_to_file

logging.basicConfig(level=logging.INFO, stream=sys.stderr)
LOGGER = logging.getLogger("orders-mcp-isolated")
mcp = FastMCP("Order summary (isolated)")


@mcp.tool()
def summarize_orders() -> dict[str, Any]:
    """Summarize /input/orders.csv and write /output/summary.json."""
    started = perf_counter_ns()
    result = summarize_to_file(Path("/input/orders.csv"), Path("/output/summary.json"))
    result["server_duration_ns"] = perf_counter_ns() - started
    LOGGER.info("summarize_orders completed duration_ns=%d", result["server_duration_ns"])
    return result


if __name__ == "__main__":
    mcp.run(transport="stdio")
