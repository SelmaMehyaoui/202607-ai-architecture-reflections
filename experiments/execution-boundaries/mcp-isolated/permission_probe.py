#!/usr/bin/env python3
"""Fixed, harmless capability probes executed inside the isolated container."""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any


def attempt(action: Callable[[], object]) -> tuple[str, str]:
    try:
        action()
        return "allowed", ""
    except (OSError, subprocess.SubprocessError) as exc:
        return "denied", f"{type(exc).__name__}: {exc}"


def environment_probe() -> tuple[str, str]:
    if "EXPERIMENT_DUMMY_TOKEN" in os.environ:
        return "allowed", "dummy variable was passed into the container"
    return "denied", "dummy variable was not passed into the container"


def network_probe() -> tuple[str, str]:
    try:
        with socket.create_connection(("192.0.2.1", 9), timeout=0.2):
            return "connected", "unexpected connection to TEST-NET-1"
    except OSError as exc:
        return "connection_failed", f"{type(exc).__name__}: {exc}"


def main() -> int:
    probes: list[tuple[str, str, Callable[[], tuple[str, str]]]] = [
        (
            "read designated input",
            "allowed",
            lambda: attempt(lambda: Path("/input/orders.csv").read_text(encoding="utf-8")),
        ),
        (
            "read restricted fixture",
            "denied",
            lambda: attempt(
                lambda: Path("/security-fixtures/restricted/secret.txt").read_text(encoding="utf-8")
            ),
        ),
        (
            "write designated output",
            "allowed",
            lambda: attempt(
                lambda: Path("/output/permission-probe.txt").write_text(
                    "disposable", encoding="utf-8"
                )
            ),
        ),
        (
            "write elsewhere",
            "denied",
            lambda: attempt(
                lambda: Path("/app/permission-probe.txt").write_text("disposable", encoding="utf-8")
            ),
        ),
        (
            "enumerate parent directory",
            "allowed",
            lambda: attempt(lambda: list(Path("/").iterdir())),
        ),
        (
            "read dummy environment variable",
            "denied",
            environment_probe,
        ),
        (
            "spawn subprocess",
            "allowed",
            lambda: attempt(lambda: subprocess.run([sys.executable, "-c", "pass"], check=True)),
        ),
        (
            "outbound network",
            "connection_failed",
            network_probe,
        ),
        (
            "read host repository file",
            "denied",
            lambda: attempt(lambda: Path("/repository/README.md").read_text(encoding="utf-8")),
        ),
        (
            "read container system file",
            "allowed",
            lambda: attempt(lambda: Path("/etc/os-release").read_text(encoding="utf-8")),
        ),
    ]
    rows: list[dict[str, Any]] = []
    for capability, expected, probe in probes:
        actual, detail = probe()
        rows.append(
            {
                "architecture": "mcp-isolated",
                "capability": capability,
                "expected": expected,
                "actual": actual,
                "executing_boundary": "container permission-probe process (UID 10001)",
                "notes": detail,
            }
        )
    print(json.dumps(rows, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
