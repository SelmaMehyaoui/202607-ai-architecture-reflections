#!/usr/bin/env python3
"""Local stdio MCP server exposing one explicit operation."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from time import perf_counter_ns
from typing import Any

COMMON = Path(__file__).resolve().parents[1] / "common"
sys.path.insert(0, str(COMMON))

from mcp.server.fastmcp import FastMCP
from summarize import summarize_to_file

logging.basicConfig(level=logging.INFO, stream=sys.stderr)
LOGGER = logging.getLogger("orders-mcp-local")
mcp = FastMCP("Order summary (local)")


@mcp.tool()
def summarize_orders(input_path: str, output_path: str) -> dict[str, Any]:
    """Summarize an explicitly supplied order CSV into an explicit JSON path."""
    started = perf_counter_ns()
    LOGGER.info("summarize_orders started")
    try:
        result = summarize_to_file(Path(input_path), Path(output_path))
    except ValueError:
        LOGGER.exception("summarize_orders failed")
        raise
    result["server_duration_ns"] = perf_counter_ns() - started
    LOGGER.info("summarize_orders completed duration_ns=%d", result["server_duration_ns"])
    return result


if __name__ == "__main__":
    mcp.run(transport="stdio")
