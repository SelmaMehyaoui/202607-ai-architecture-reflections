#!/usr/bin/env python3
"""Run safe host-authority approximations and real isolated-container probes."""

from __future__ import annotations

import argparse
import csv
import json
import os
import socket
import subprocess
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "common/security-fixtures"
INPUT = ROOT / "common/input"
RESULTS = ROOT / "results"
IMAGE = "orders-mcp-isolated"
FIELDS = ["architecture", "capability", "expected", "actual", "executing_boundary", "notes"]
Probe = Callable[[], tuple[str, str]]


def attempt(action: Callable[[], object]) -> tuple[str, str]:
    try:
        action()
        return "allowed", ""
    except (OSError, subprocess.SubprocessError) as exc:
        return "denied", f"{type(exc).__name__}: {exc}"


def host_network_probe() -> tuple[str, str]:
    try:
        with socket.create_connection(("example.invalid", 9), timeout=0.2):
            return "connected", "unexpected connection to reserved invalid domain"
    except OSError as exc:
        return "connection_failed", (
            f"{type(exc).__name__}: {exc}; failure does not establish an administrative denial"
        )


def host_probes(boundary: str) -> list[dict[str, str]]:
    os.environ["EXPERIMENT_DUMMY_TOKEN"] = "dummy-value-only"
    RESULTS.mkdir(parents=True, exist_ok=True)
    with (
        tempfile.TemporaryDirectory(prefix="permission-probe-", dir=RESULTS) as temporary,
        tempfile.TemporaryDirectory(
            prefix="unrelated-write-", dir=FIXTURES / "allowed"
        ) as unrelated_temporary,
    ):
        designated_output = Path(temporary) / "output.txt"
        unrelated_output = Path(unrelated_temporary) / "probe.txt"
        probes: list[tuple[str, str, Probe, str]] = [
            (
                "read designated input",
                "allowed",
                lambda: attempt(
                    lambda: (ROOT / "common/input/orders.csv").read_text(encoding="utf-8")
                ),
                "explicit fixture",
            ),
            (
                "read unrelated repository file",
                "observe",
                lambda: attempt(
                    lambda: (ROOT.parents[1] / "README.md").read_text(encoding="utf-8")
                ),
                "repository README only",
            ),
            (
                "read restricted fixture",
                "observe",
                lambda: attempt(
                    lambda: (FIXTURES / "restricted/secret.txt").read_text(encoding="utf-8")
                ),
                "dummy secret only",
            ),
            (
                "write designated output",
                "allowed",
                lambda: attempt(
                    lambda: designated_output.write_text("disposable", encoding="utf-8")
                ),
                "disposable results directory",
            ),
            (
                "write elsewhere in repository",
                "observe",
                lambda: attempt(
                    lambda: unrelated_output.write_text("disposable", encoding="utf-8")
                ),
                "disposable security-fixture path removed after the probe",
            ),
            (
                "enumerate parent directory",
                "observe",
                lambda: attempt(lambda: list(ROOT.parent.iterdir())),
                "names are not persisted",
            ),
            (
                "read dummy environment variable",
                "observe",
                lambda: attempt(lambda: os.environ["EXPERIMENT_DUMMY_TOKEN"]),
                "fake value only",
            ),
            (
                "spawn subprocess",
                "observe",
                lambda: attempt(lambda: subprocess.run([sys.executable, "-c", "pass"], check=True)),
                "fixed harmless Python command; no shell",
            ),
            (
                "outbound network",
                "observe",
                host_network_probe,
                "reserved invalid domain; no service contacted",
            ),
            (
                "read outside intended working area",
                "observe",
                lambda: attempt(lambda: Path("/etc/hosts").read_text(encoding="utf-8")),
                "non-sensitive host system file",
            ),
        ]
        rows = []
        for name, expected, probe, note in probes:
            actual, detail = probe()
            rows.append(
                {
                    "architecture": boundary,
                    "capability": name,
                    "expected": expected,
                    "actual": actual,
                    "executing_boundary": "permission-test process (same host OS user)",
                    "notes": (
                        f"{note}; OS-authority approximation, not exposed as an MCP tool"
                        + (f"; {detail}" if detail else "")
                    ),
                }
            )
        return rows


def isolated_probes() -> list[dict[str, str]]:
    image = subprocess.run(
        ["docker", "image", "inspect", IMAGE], capture_output=True, text=True, check=False
    )
    if image.returncode:
        raise RuntimeError(
            "isolated image is unavailable; build it first with "
            "`docker build -f mcp-isolated/Dockerfile -t orders-mcp-isolated .`"
        )
    with tempfile.TemporaryDirectory(prefix="permission-container-", dir=RESULTS) as temporary:
        output_dir = Path(temporary)
        os.chmod(output_dir, 0o777)
        process = subprocess.run(
            [
                "docker",
                "run",
                "--rm",
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
                f"type=bind,src={INPUT},dst=/input,readonly",
                "--mount",
                f"type=bind,src={output_dir},dst=/output",
                "--entrypoint",
                "python",
                IMAGE,
                "/app/permission_probe.py",
            ],
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
        if process.returncode:
            raise RuntimeError(
                f"isolated permission probe failed: {process.stderr.strip() or process.stdout.strip()}"
            )
        rows = json.loads(process.stdout)
        if not isinstance(rows, list) or not all(isinstance(item, dict) for item in rows):
            raise TypeError("isolated permission probe returned an invalid payload")
        return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=RESULTS / "permissions.csv")
    args = parser.parse_args()
    try:
        rows = host_probes("skill") + host_probes("mcp-local") + isolated_probes()
    except (
        OSError,
        RuntimeError,
        TypeError,
        subprocess.SubprocessError,
        json.JSONDecodeError,
    ) as exc:
        parser.exit(1, f"error: {exc}\n")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
