#!/usr/bin/env python3
"""Repeatable architecture benchmark; no LLM is involved."""

from __future__ import annotations

import argparse
import asyncio
import csv
import json
import os
import subprocess
import sys
import tempfile
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter_ns
from typing import Any

from environment import environment

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "common/input/orders.csv"
SKILL = ROOT / "skill/scripts/summarize_orders.py"
LOCAL_SERVER = ROOT / "mcp-local/server.py"
FIELDS = [
    "architecture",
    "run_index",
    "classification",
    "total_elapsed_ns",
    "business_logic_ns",
    "server_duration_ns",
    "success",
    "timestamp",
    "environment_id",
]


def record(
    architecture: str,
    index: int,
    classification: str,
    elapsed: int,
    metadata: dict[str, Any],
    success: bool,
) -> dict[str, Any]:
    return {
        "architecture": architecture,
        "run_index": index,
        "classification": classification,
        "total_elapsed_ns": elapsed,
        "business_logic_ns": metadata.get("business_logic_ns", ""),
        "server_duration_ns": metadata.get("server_duration_ns", ""),
        "success": success,
        "timestamp": datetime.now(UTC).isoformat(),
        "environment_id": environment()["environment_id"],
    }


def benchmark_skill(cold: int, warm: int, output_dir: Path) -> list[dict[str, Any]]:
    rows = []
    for index in range(cold + warm):
        destination = output_dir / f"skill-{index}.json"
        started = perf_counter_ns()
        process = subprocess.run(
            [sys.executable, str(SKILL), "--input", str(INPUT), "--output", str(destination)],
            capture_output=True,
            text=True,
            check=False,
        )
        elapsed = perf_counter_ns() - started
        metadata = json.loads(process.stdout) if process.returncode == 0 else {}
        rows.append(
            record(
                "skill",
                index,
                "cold" if index < cold else "warm",
                elapsed,
                metadata,
                process.returncode == 0,
            )
        )
    return rows


def tool_payload(result: Any) -> dict[str, Any]:
    if result.isError:
        raise RuntimeError("MCP tool returned an error")
    if result.structuredContent:
        return dict(result.structuredContent)
    for content in result.content:
        if getattr(content, "text", None):
            return dict(json.loads(content.text))
    raise RuntimeError("MCP result had no JSON payload")


async def benchmark_mcp(
    architecture: str, cold: int, warm: int, output_dir: Path
) -> list[dict[str, Any]]:
    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
    except ImportError as exc:
        raise SystemExit("Install project dependencies first: python -m pip install -e .") from exc

    arguments: Callable[[int], dict[str, str]]
    if architecture == "mcp-local":
        params = StdioServerParameters(command=sys.executable, args=[str(LOCAL_SERVER)])
        arguments = lambda index: {
            "input_path": str(INPUT),
            "output_path": str(output_dir / f"local-{index}.json"),
        }
    else:
        if subprocess.run(
            ["docker", "image", "inspect", "orders-mcp-isolated"], capture_output=True, check=False
        ).returncode:
            raise SystemExit(
                "Build image first: docker build -f mcp-isolated/Dockerfile "
                "-t orders-mcp-isolated ."
            )
        params = StdioServerParameters(
            command="docker",
            args=[
                "run",
                "--rm",
                "-i",
                "--network",
                "none",
                "--read-only",
                "--cpus",
                "0.5",
                "--memory",
                "128m",
                "--tmpfs",
                "/tmp",
                "--mount",
                f"type=bind,src={INPUT.parent},dst=/input,readonly",
                "--mount",
                f"type=bind,src={output_dir},dst=/output",
                "orders-mcp-isolated",
            ],
        )
        arguments = lambda index: {}

    rows: list[dict[str, Any]] = []
    # Cold calls each create a server process; warm calls share one server session.
    for index in range(cold):
        async with stdio_client(params) as streams, ClientSession(*streams) as session:
            started = perf_counter_ns()
            await session.initialize()
            result = await session.call_tool("summarize_orders", arguments(index))
            rows.append(
                record(
                    architecture,
                    index,
                    "cold",
                    perf_counter_ns() - started,
                    tool_payload(result),
                    not result.isError,
                )
            )
    async with stdio_client(params) as streams, ClientSession(*streams) as session:
        await session.initialize()
        for offset in range(warm):
            index = cold + offset
            started = perf_counter_ns()
            result = await session.call_tool("summarize_orders", arguments(index))
            rows.append(
                record(
                    architecture,
                    index,
                    "warm",
                    perf_counter_ns() - started,
                    tool_payload(result),
                    not result.isError,
                )
            )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("architecture", choices=["skill", "mcp-local", "mcp-isolated"])
    parser.add_argument("--cold", type=int, default=1)
    parser.add_argument("--warm", type=int, default=30)
    parser.add_argument("--output", type=Path, default=ROOT / "results/latency.csv")
    args = parser.parse_args()
    if args.cold < 0 or args.warm < 1:
        parser.error("--cold must be non-negative and --warm must be positive")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    # Colima shares the repository's /Users path, but not macOS /var/folders.
    temporary_parent = ROOT / "results" if args.architecture == "mcp-isolated" else None
    with tempfile.TemporaryDirectory(
        prefix="execution-boundary-", dir=temporary_parent
    ) as temporary:
        output_dir = Path(temporary)
        if args.architecture == "mcp-isolated":
            # The designated disposable output mount must be writable by UID 10001.
            os.chmod(output_dir, 0o777)
        rows = (
            benchmark_skill(args.cold, args.warm, output_dir)
            if args.architecture == "skill"
            else asyncio.run(benchmark_mcp(args.architecture, args.cold, args.warm, output_dir))
        )
    with args.output.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return 0 if all(row["success"] for row in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
