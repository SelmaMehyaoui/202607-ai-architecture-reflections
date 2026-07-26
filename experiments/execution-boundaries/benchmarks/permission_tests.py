#!/usr/bin/env python3
"""Safe, explicit host-boundary capability probes.

This initial runner records direct process observations for the skill and local
server configurations. Container probes are intentionally left unobserved until
Docker is available; no outcome is inferred from the Dockerfile.
"""

from __future__ import annotations

import argparse
import csv
import os
import socket
import subprocess
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "common/security-fixtures"
FIELDS = ["architecture", "capability", "expected", "actual", "executing_boundary", "notes"]


def attempt(action: Callable[[], object]) -> str:
    try:
        action()
        return "allowed"
    except (OSError, subprocess.SubprocessError):
        return "denied"


def host_probes(boundary: str) -> list[dict[str, str]]:
    os.environ["EXPERIMENT_DUMMY_TOKEN"] = "dummy-value-only"
    with tempfile.TemporaryDirectory(prefix="permission-probe-") as temporary:
        output = Path(temporary) / "output.txt"
        probes: list[tuple[str, str, Callable[[], object], str]] = [
            (
                "read designated input",
                "allowed",
                lambda: (ROOT / "common/input/orders.csv").read_text(),
                "explicit fixture",
            ),
            (
                "read restricted fixture",
                "observe",
                lambda: (FIXTURES / "restricted/secret.txt").read_text(),
                "dummy secret only",
            ),
            (
                "write designated output",
                "allowed",
                lambda: output.write_text("disposable"),
                "temporary directory",
            ),
            (
                "enumerate parent directory",
                "observe",
                lambda: list(ROOT.parent.iterdir()),
                "names are not persisted",
            ),
            (
                "read dummy environment variable",
                "observe",
                lambda: os.environ["EXPERIMENT_DUMMY_TOKEN"],
                "fake value only",
            ),
            (
                "spawn subprocess",
                "observe",
                lambda: subprocess.run([sys.executable, "-c", "pass"], check=True),
                "no shell",
            ),
            (
                "outbound network",
                "observe",
                lambda: socket.create_connection(("example.invalid", 9), timeout=0.1),
                "reserved invalid domain; no service contacted",
            ),
        ]
        return [
            {
                "architecture": boundary,
                "capability": name,
                "expected": expected,
                "actual": attempt(action),
                "executing_boundary": "permission-test process (same host user)",
                "notes": f"{notes}; OS-authority probe, not exposed as an MCP tool",
            }
            for name, expected, action, notes in probes
        ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "results/permissions.csv")
    args = parser.parse_args()
    rows = host_probes("skill") + host_probes("mcp-local")
    rows += [
        {
            "architecture": "mcp-isolated",
            "capability": "all probes",
            "expected": "configuration-specific",
            "actual": "not run",
            "executing_boundary": "container MCP server",
            "notes": "Run and record only when Docker is available.",
        }
    ]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
