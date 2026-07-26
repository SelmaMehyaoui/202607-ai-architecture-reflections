#!/usr/bin/env python3
"""Record benchmark environment without collecting personal data."""

from __future__ import annotations

import json
import platform
import shutil
import subprocess
import sys
from typing import Any


def environment() -> dict[str, Any]:
    data: dict[str, Any] = {
        "environment_id": f"{platform.system()}-{platform.machine()}-py{platform.python_version()}",
        "os": platform.platform(),
        "machine": platform.machine(),
        "python": sys.version.split()[0],
        "docker_available": shutil.which("docker") is not None,
    }
    if data["docker_available"]:
        process = subprocess.run(
            ["docker", "--version"], capture_output=True, text=True, check=False, timeout=10
        )
        data["docker_version"] = process.stdout.strip() or process.stderr.strip()
    return data


if __name__ == "__main__":
    print(json.dumps(environment(), indent=2, sort_keys=True))
