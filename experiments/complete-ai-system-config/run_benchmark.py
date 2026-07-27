#!/usr/bin/env python3
"""Optional API-driven Skill versus MCP system-configuration benchmark."""

from __future__ import annotations

import argparse
import asyncio
import csv
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter_ns
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

EXPERIMENT = Path(__file__).resolve().parent
REPOSITORY = EXPERIMENT.parents[1]
BOUNDARIES = EXPERIMENT.parent / "execution-boundaries"
INPUT = BOUNDARIES / "common/input/orders.csv"
EXPECTED = BOUNDARIES / "common/expected/summary.json"
SKILL_MD = BOUNDARIES / "skill/SKILL.md"
SKILL_SCRIPT = BOUNDARIES / "skill/scripts/summarize_orders.py"
MCP_SERVER = BOUNDARIES / "mcp-local/server.py"
DEFAULT_BASE_URL = "http://localhost:12434/engines/v1"
USER_REQUEST = (
    "Summarize the experiment order CSV. Report the total number of orders "
    "and total revenue after using the available capability."
)
COMMON_SYSTEM = (
    "You are the action-selection layer in a controlled architecture experiment. "
    "Use exactly one available function to perform the calculation. Do not calculate "
    "the CSV yourself. After receiving the function result, answer the user concisely "
    "and include both total orders and total revenue."
)
FIELDS = [
    "run_id",
    "timestamp",
    "model",
    "interface",
    "run_index",
    "classification",
    "success",
    "tool_selected",
    "arguments_valid",
    "answer_correct",
    "prompt_tokens",
    "completion_tokens",
    "total_tokens",
    "usage_reported",
    "first_inference_ms",
    "tool_execution_ms",
    "second_inference_ms",
    "end_to_end_ms",
    "request_bytes",
    "response_bytes",
    "model_turns",
    "tool_calls",
    "error",
]


@dataclass
class ModelResponse:
    payload: dict[str, Any]
    elapsed_ms: float
    request_bytes: int
    response_bytes: int


class ChatClient:
    def __init__(
        self,
        base_url: str,
        model: str,
        api_key: str | None,
        timeout: float,
        temperature: float,
        max_tokens: int,
    ) -> None:
        self.url = f"{base_url.rstrip('/')}/chat/completions"
        self.model = model
        self.api_key = api_key
        self.timeout = timeout
        self.temperature = temperature
        self.max_tokens = max_tokens

    def complete(
        self, messages: list[dict[str, Any]], tools: list[dict[str, Any]]
    ) -> ModelResponse:
        body = {
            "model": self.model,
            "messages": messages,
            "tools": tools,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": False,
        }
        encoded = json.dumps(body, separators=(",", ":")).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        request = urllib.request.Request(self.url, data=encoded, headers=headers, method="POST")
        started = perf_counter_ns()
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                raw = response.read()
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"model endpoint HTTP {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"cannot reach model endpoint {self.url}: {exc.reason}") from exc
        elapsed_ms = (perf_counter_ns() - started) / 1_000_000
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RuntimeError("model endpoint returned invalid JSON") from exc
        return ModelResponse(payload, elapsed_ms, len(encoded), len(raw))


def slug(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return normalized or "model"


def usage(payload: dict[str, Any]) -> tuple[int | None, int | None, int | None]:
    reported = payload.get("usage")
    if not isinstance(reported, dict):
        return None, None, None
    return (
        integer_or_none(reported.get("prompt_tokens")),
        integer_or_none(reported.get("completion_tokens")),
        integer_or_none(reported.get("total_tokens")),
    )


def integer_or_none(value: object) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def add_optional(left: int | None, right: int | None) -> int | None:
    if left is None or right is None:
        return None
    return left + right


def choice_message(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        message = payload["choices"][0]["message"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError("model response contains no assistant message") from exc
    if not isinstance(message, dict):
        raise TypeError("assistant message has an invalid type")
    return message


def tool_call(message: dict[str, Any]) -> tuple[str, str, dict[str, Any]]:
    calls = message.get("tool_calls")
    if not isinstance(calls, list) or len(calls) != 1:
        raise RuntimeError("model must request exactly one tool call")
    call = calls[0]
    try:
        call_id = call["id"]
        function = call["function"]
        name = function["name"]
        arguments = json.loads(function["arguments"])
    except (KeyError, TypeError, json.JSONDecodeError) as exc:
        raise RuntimeError("model returned an invalid function call") from exc
    if not isinstance(call_id, str) or not isinstance(name, str) or not isinstance(arguments, dict):
        raise TypeError("model returned invalid function-call fields")
    return call_id, name, arguments


def assistant_history_message(message: dict[str, Any]) -> dict[str, Any]:
    return {
        "role": "assistant",
        "content": message.get("content"),
        "tool_calls": message.get("tool_calls"),
    }


def arguments_are_valid(arguments: dict[str, Any], output: Path) -> bool:
    return (
        arguments.get("input_path") == str(INPUT)
        and arguments.get("output_path") == str(output)
        and set(arguments) == {"input_path", "output_path"}
    )


def skill_tool() -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": "run_skill_order_summary",
            "description": (
                "Run the bundled Python script described by SKILL.md to summarize "
                "an explicit order CSV into an explicit JSON output path."
            ),
            "parameters": path_parameters(),
        },
    }


def path_parameters() -> dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "input_path": {
                "type": "string",
                "description": "Exact path of the controlled input CSV.",
            },
            "output_path": {
                "type": "string",
                "description": "Exact disposable JSON destination.",
            },
        },
        "required": ["input_path", "output_path"],
        "additionalProperties": False,
    }


def mcp_tool_schema(tool: Any) -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description or "",
            "parameters": tool.inputSchema,
        },
    }


def condition_system(interface: str, output: Path) -> str:
    controlled = (
        f"\nControlled input_path: {INPUT}\n"
        f"Controlled output_path: {output}\n"
        "Use these exact values as function arguments."
    )
    if interface == "skill":
        return f"{COMMON_SYSTEM}\n\n<skill>\n{SKILL_MD.read_text(encoding='utf-8')}\n</skill>{controlled}"
    return f"{COMMON_SYSTEM}{controlled}"


def normalize_tool_payload(payload: dict[str, Any]) -> dict[str, Any]:
    summary = payload.get("summary")
    if not isinstance(summary, dict):
        raise TypeError("executor returned no structured summary")
    return summary


def run_skill(arguments: dict[str, Any]) -> tuple[dict[str, Any], float]:
    started = perf_counter_ns()
    process = subprocess.run(
        [
            sys.executable,
            str(SKILL_SCRIPT),
            "--input",
            arguments["input_path"],
            "--output",
            arguments["output_path"],
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    elapsed_ms = (perf_counter_ns() - started) / 1_000_000
    if process.returncode:
        raise RuntimeError(process.stderr.strip() or "skill script failed")
    return json.loads(process.stdout), elapsed_ms


def mcp_payload(result: Any) -> dict[str, Any]:
    if result.isError:
        raise RuntimeError("MCP tool returned an error")
    if result.structuredContent:
        return dict(result.structuredContent)
    for content in result.content:
        text = getattr(content, "text", None)
        if text:
            return dict(json.loads(text))
    raise RuntimeError("MCP tool returned no JSON payload")


def final_answer_is_correct(message: dict[str, Any]) -> bool:
    content = message.get("content")
    return (
        isinstance(content, str)
        and "411.49" in content
        and re.search(r"\b8\b", content) is not None
    )


async def run_condition(
    client: ChatClient,
    session: ClientSession,
    interface: str,
    run_index: int,
    output: Path,
    mcp_tool: Any,
) -> tuple[dict[str, Any], dict[str, Any]]:
    run_id = f"{run_index:03d}-{interface}"
    started = perf_counter_ns()
    first: ModelResponse | None = None
    second: ModelResponse | None = None
    selected = ""
    valid_arguments = False
    answer_correct = False
    tool_ms = 0.0
    error = ""
    tool_result: dict[str, Any] | None = None
    expected_tool = "run_skill_order_summary" if interface == "skill" else mcp_tool.name
    tools = [skill_tool() if interface == "skill" else mcp_tool_schema(mcp_tool)]
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": condition_system(interface, output)},
        {"role": "user", "content": USER_REQUEST},
    ]
    trace: dict[str, Any] = {
        "run_id": run_id,
        "model": client.model,
        "interface": interface,
        "messages_before_first_call": json.loads(json.dumps(messages)),
        "tools": tools,
    }
    try:
        first = await asyncio.to_thread(client.complete, messages, tools)
        first_message = choice_message(first.payload)
        call_id, selected, arguments = tool_call(first_message)
        valid_arguments = selected == expected_tool and arguments_are_valid(arguments, output)
        if not valid_arguments:
            raise RuntimeError("model selected the wrong tool or supplied uncontrolled arguments")
        if interface == "skill":
            payload, tool_ms = await asyncio.to_thread(run_skill, arguments)
        else:
            tool_started = perf_counter_ns()
            result = await session.call_tool(selected, arguments)
            tool_ms = (perf_counter_ns() - tool_started) / 1_000_000
            payload = mcp_payload(result)
        tool_result = normalize_tool_payload(payload)
        messages.extend(
            [
                assistant_history_message(first_message),
                {
                    "role": "tool",
                    "tool_call_id": call_id,
                    "content": json.dumps(tool_result, sort_keys=True),
                },
            ]
        )
        second = await asyncio.to_thread(client.complete, messages, tools)
        final_message = choice_message(second.payload)
        if final_message.get("tool_calls"):
            raise RuntimeError("model requested an additional tool on the final turn")
        answer_correct = final_answer_is_correct(final_message)
        if not answer_correct:
            raise RuntimeError("final answer did not contain the expected order count and revenue")
        trace["final_message"] = final_message
    except (KeyError, TypeError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        error = f"{type(exc).__name__}: {exc}"

    first_usage = usage(first.payload) if first else (None, None, None)
    second_usage = usage(second.payload) if second else (None, None, None)
    prompt_tokens = add_optional(first_usage[0], second_usage[0])
    completion_tokens = add_optional(first_usage[1], second_usage[1])
    total_tokens = add_optional(first_usage[2], second_usage[2])
    row = {
        "run_id": run_id,
        "timestamp": datetime.now(UTC).isoformat(),
        "model": client.model,
        "interface": interface,
        "run_index": run_index,
        "classification": "first_observation" if run_index == 0 else "repeat",
        "success": not error,
        "tool_selected": selected,
        "arguments_valid": valid_arguments,
        "answer_correct": answer_correct,
        "prompt_tokens": prompt_tokens if prompt_tokens is not None else "",
        "completion_tokens": completion_tokens if completion_tokens is not None else "",
        "total_tokens": total_tokens if total_tokens is not None else "",
        "usage_reported": total_tokens is not None,
        "first_inference_ms": round(first.elapsed_ms, 3) if first else "",
        "tool_execution_ms": round(tool_ms, 3),
        "second_inference_ms": round(second.elapsed_ms, 3) if second else "",
        "end_to_end_ms": round((perf_counter_ns() - started) / 1_000_000, 3),
        "request_bytes": (first.request_bytes if first else 0)
        + (second.request_bytes if second else 0),
        "response_bytes": (first.response_bytes if first else 0)
        + (second.response_bytes if second else 0),
        "model_turns": int(first is not None) + int(second is not None),
        "tool_calls": int(tool_result is not None),
        "error": error,
    }
    trace.update(
        {
            "first_response": first.payload if first else None,
            "normalized_tool_result": tool_result,
            "second_response": second.payload if second else None,
            "summary": row,
        }
    )
    return row, trace


async def benchmark(args: argparse.Namespace) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    api_key = os.environ.get(args.api_key_env) if args.api_key_env else None
    if args.api_key_env and not api_key:
        raise SystemExit(f"environment variable {args.api_key_env} is not set")
    client = ChatClient(
        args.base_url,
        args.model,
        api_key,
        args.timeout,
        args.temperature,
        args.max_tokens,
    )
    parameters = StdioServerParameters(command=sys.executable, args=[str(MCP_SERVER)])
    rows: list[dict[str, Any]] = []
    traces: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="complete-system-") as temporary:
        output = Path(temporary) / "summary.json"
        async with stdio_client(parameters) as streams, ClientSession(*streams) as session:
            await session.initialize()
            listed = await session.list_tools()
            matching = [tool for tool in listed.tools if tool.name == "summarize_orders"]
            if len(matching) != 1:
                raise RuntimeError(
                    "local MCP server did not expose exactly one summarize_orders tool"
                )
            mcp_tool = matching[0]
            for run_index in range(args.runs):
                order = ["skill", "mcp"] if run_index % 2 == 0 else ["mcp", "skill"]
                for interface in order:
                    row, trace = await run_condition(
                        client, session, interface, run_index, output, mcp_tool
                    )
                    rows.append(row)
                    traces.append(trace)
    return rows, traces


def write_outputs(
    rows: list[dict[str, Any]],
    traces: list[dict[str, Any]],
    output: Path,
    args: argparse.Namespace,
) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    trace_path = output.with_name(output.stem.replace("_comparison", "_traces") + ".jsonl")
    with trace_path.open("w", encoding="utf-8") as target:
        for trace in traces:
            target.write(json.dumps(trace, sort_keys=True) + "\n")
    metadata = {
        "captured_at": datetime.now(UTC).isoformat(),
        "base_url": args.base_url,
        "model": args.model,
        "runs_per_interface": args.runs,
        "temperature": args.temperature,
        "max_tokens": args.max_tokens,
        "request_timeout_seconds": args.timeout,
        "user_request": USER_REQUEST,
        "input": str(INPUT),
        "expected": json.loads(EXPECTED.read_text(encoding="utf-8")),
        "skill_md": SKILL_MD.read_text(encoding="utf-8"),
        "api_key_environment_variable": args.api_key_env,
        "note": "API key values are never persisted.",
    }
    metadata_path = output.with_name(output.stem.replace("_comparison", "_metadata") + ".json")
    metadata_path.write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--api-key-env")
    parser.add_argument("--runs", type=int, default=10)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=256)
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.runs < 1:
        parser.error("--runs must be positive")
    if args.max_tokens < 1:
        parser.error("--max-tokens must be positive")
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    if args.output is None:
        date = datetime.now(UTC).strftime("%Y%m%d")
        args.output = EXPERIMENT / f"results/{date}_{slug(args.model)}_comparison.csv"
    return args


def main() -> int:
    args = parse_args()
    try:
        rows, traces = asyncio.run(benchmark(args))
    except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
        raise SystemExit(f"error: {exc}") from exc
    write_outputs(rows, traces, args.output, args)
    print(args.output)
    return 0 if all(row["success"] for row in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
