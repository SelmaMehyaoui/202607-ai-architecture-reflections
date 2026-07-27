from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

EXPERIMENT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "complete_ai_system_benchmark", EXPERIMENT / "run_benchmark.py"
)
assert SPEC is not None and SPEC.loader is not None
benchmark = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = benchmark
SPEC.loader.exec_module(benchmark)


class HelpersTest(unittest.TestCase):
    def test_codex_run_template_preserves_unavailable_token_state(self) -> None:
        template = json.loads((EXPERIMENT / "templates/codex-run.json").read_text(encoding="utf-8"))
        observations = template["observations"]
        self.assertIsNone(observations["token_count"])
        self.assertEqual(observations["token_measurement_source"], "unavailable")
        self.assertIsNone(template["success"])

    def test_usage_is_provider_reported_or_missing(self) -> None:
        self.assertEqual(
            benchmark.usage(
                {
                    "usage": {
                        "prompt_tokens": 10,
                        "completion_tokens": 4,
                        "total_tokens": 14,
                    }
                }
            ),
            (10, 4, 14),
        )
        self.assertEqual(benchmark.usage({}), (None, None, None))

    def test_expected_call_arguments_are_strict(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "summary.json"
            arguments = {
                "input_path": str(benchmark.INPUT),
                "output_path": str(output),
            }
            self.assertTrue(benchmark.arguments_are_valid(arguments, output))
            self.assertFalse(
                benchmark.arguments_are_valid({**arguments, "unexpected": True}, output)
            )

    def test_answer_requires_both_expected_values(self) -> None:
        self.assertTrue(
            benchmark.final_answer_is_correct(
                {"content": "The 8 orders produced total revenue of 411.49."}
            )
        )
        self.assertFalse(benchmark.final_answer_is_correct({"content": "Total revenue: 411.49."}))

    def test_skill_executor_runs_the_real_script(self) -> None:
        expected = json.loads(benchmark.EXPECTED.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "skill.json"
            payload, elapsed_ms = benchmark.run_skill(
                {
                    "input_path": str(benchmark.INPUT),
                    "output_path": str(output),
                }
            )
            self.assertEqual(benchmark.normalize_tool_payload(payload), expected)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8")), expected)
            self.assertGreaterEqual(elapsed_ms, 0)


class McpExecutorTest(unittest.IsolatedAsyncioTestCase):
    async def test_mcp_schema_and_real_call_match_the_controlled_operation(self) -> None:
        expected = json.loads(benchmark.EXPECTED.read_text(encoding="utf-8"))
        parameters = StdioServerParameters(command=sys.executable, args=[str(benchmark.MCP_SERVER)])
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "mcp.json"
            async with (
                stdio_client(parameters) as streams,
                ClientSession(*streams) as session,
            ):
                await session.initialize()
                listed = await session.list_tools()
                tools = [tool for tool in listed.tools if tool.name == "summarize_orders"]
                self.assertEqual(len(tools), 1)
                schema: dict[str, Any] = benchmark.mcp_tool_schema(tools[0])
                properties = schema["function"]["parameters"]["properties"]
                self.assertEqual(set(properties), {"input_path", "output_path"})
                result = await session.call_tool(
                    "summarize_orders",
                    {
                        "input_path": str(benchmark.INPUT),
                        "output_path": str(output),
                    },
                )
                payload = benchmark.mcp_payload(result)
            self.assertEqual(benchmark.normalize_tool_payload(payload), expected)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8")), expected)


if __name__ == "__main__":
    unittest.main()
