#!/usr/bin/env python3
"""Derive descriptive task-success summaries from reviewed JSONL records."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from statistics import median
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FIELDS = {
    "run_id",
    "task_id",
    "model_class",
    "model_id",
    "condition",
    "tool_selection_correct",
    "arguments_valid",
    "answer_correct",
    "clarification_correct",
    "abstention_correct",
    "unsupported_claim_count",
    "model_turns",
    "tool_calls",
    "end_to_end_ms",
}


def load_tasks() -> dict[str, dict[str, Any]]:
    tasks: dict[str, dict[str, Any]] = {}
    path = ROOT / "tasks/tasks.jsonl"
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        task = json.loads(line)
        task_id = task["task_id"]
        if task_id in tasks:
            raise ValueError(f"duplicate task_id at {path}:{line_number}: {task_id}")
        tasks[task_id] = task
    return tasks


def load_records(path: Path) -> list[dict[str, Any]]:
    records = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        record = json.loads(line)
        missing = REQUIRED_FIELDS - record.keys()
        if missing:
            raise ValueError(f"{path}:{line_number} missing fields: {sorted(missing)}")
        records.append(record)
    if not records:
        raise ValueError(f"{path} contains no response records")
    return records


def task_success(task: dict[str, Any], record: dict[str, Any]) -> bool:
    if record["unsupported_claim_count"] != 0:
        return False
    behavior = task["expected_behavior"]
    if behavior in {"tool", "recover"}:
        return bool(
            record["tool_selection_correct"]
            and record["arguments_valid"]
            and record["answer_correct"]
        )
    if behavior == "clarify":
        return bool(record["clarification_correct"] and record["tool_calls"] == 0)
    if behavior == "abstain":
        return bool(record["abstention_correct"] and record["tool_calls"] == 0)
    raise ValueError(f"unsupported expected behavior: {behavior}")


def summarize(records: list[dict[str, Any]], tasks: dict[str, dict[str, Any]]) -> dict[str, Any]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        task_id = record["task_id"]
        if task_id not in tasks:
            raise ValueError(f"unknown task_id: {task_id}")
        enriched = {**record, "success": task_success(tasks[task_id], record)}
        groups[(record["model_class"], record["condition"])].append(enriched)

    summaries: dict[str, Any] = {}
    rates: dict[tuple[str, str], float] = {}
    for (model_class, condition), group in sorted(groups.items()):
        successes = sum(item["success"] for item in group)
        rate = successes / len(group)
        rates[(model_class, condition)] = rate
        summaries[f"{model_class}:{condition}"] = {
            "runs": len(group),
            "successes": successes,
            "success_rate": round(rate, 4),
            "unsupported_claims": sum(item["unsupported_claim_count"] for item in group),
            "median_end_to_end_ms": round(median(item["end_to_end_ms"] for item in group), 3),
            "mean_tool_calls": round(sum(item["tool_calls"] for item in group) / len(group), 3),
        }

    contrast = None
    if ("local", "mcp") in rates and ("remote", "mcp") in rates:
        contrast = round(rates[("local", "mcp")] - rates[("remote", "mcp")], 4)
    return {
        "groups": summaries,
        "local_minus_remote_mcp_success_rate": contrast,
        "note": "Descriptive result only; apply the pre-registered margin and uncertainty analysis.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("responses", type=Path, help="reviewed JSONL response records")
    args = parser.parse_args()
    try:
        result = summarize(load_records(args.responses), load_tasks())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.exit(1, f"error: {exc}\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
