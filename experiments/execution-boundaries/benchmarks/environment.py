#!/usr/bin/env python3
"""Persist reproducibility metadata without collecting personal data."""

from __future__ import annotations

import argparse
import json
import platform
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
IMAGE = "orders-mcp-isolated"


def environment_id() -> str:
    return f"{platform.system()}-{platform.machine()}-py{platform.python_version()}"


def command_output(arguments: list[str], timeout: int = 10) -> dict[str, Any]:
    try:
        process = subprocess.run(
            arguments, capture_output=True, text=True, check=False, timeout=timeout
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return {"available": False, "error": f"{type(exc).__name__}: {exc}"}
    output = process.stdout.strip() or process.stderr.strip()
    return {
        "available": process.returncode == 0,
        "returncode": process.returncode,
        "output": output,
    }


def package_version(package: str) -> str | None:
    try:
        return version(package)
    except PackageNotFoundError:
        return None


def environment() -> dict[str, Any]:
    data: dict[str, Any] = {
        "captured_at": datetime.now(UTC).isoformat(),
        "environment_id": environment_id(),
        "host": {
            "os": platform.platform(),
            "machine": platform.machine(),
            "python": sys.version.split()[0],
        },
        "packages": {"mcp": package_version("mcp")},
        "docker": {"cli_installed": shutil.which("docker") is not None},
        "colima": {"cli_installed": shutil.which("colima") is not None},
    }
    if data["docker"]["cli_installed"]:
        data["docker"].update(
            {
                "cli_version": command_output(["docker", "--version"]),
                "active_context": command_output(["docker", "context", "show"]),
                "server": command_output(
                    [
                        "docker",
                        "info",
                        "--format",
                        (
                            "version={{.ServerVersion}};"
                            "os={{.OperatingSystem}};"
                            "arch={{.Architecture}};"
                            "cpus={{.NCPU}};"
                            "memory={{.MemTotal}}"
                        ),
                    ]
                ),
                "isolated_image": command_output(
                    [
                        "docker",
                        "image",
                        "inspect",
                        "--format",
                        "id={{.Id}};user={{.Config.User}};digests={{json .RepoDigests}}",
                        IMAGE,
                    ]
                ),
            }
        )
    if data["colima"]["cli_installed"]:
        data["colima"].update(
            {
                "version": command_output(["colima", "version"]),
                "status": command_output(["colima", "status", "--json"]),
            }
        )
    return data


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "results/environment.json",
        help="JSON destination (default: results/environment.json)",
    )
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(environment(), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
