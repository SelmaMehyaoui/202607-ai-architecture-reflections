from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "composition_evaluator", ROOT / "evaluation/evaluate.py"
)
assert SPEC and SPEC.loader
evaluator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(evaluator)


def record(model_class: str, condition: str, answer_correct: bool = True) -> dict[str, object]:
    return {
        "run_id": f"{model_class}-{condition}",
        "task_id": "direct-001",
        "model_class": model_class,
        "model_id": f"{model_class}-model",
        "condition": condition,
        "tool_selection_correct": True,
        "arguments_valid": True,
        "answer_correct": answer_correct,
        "clarification_correct": False,
        "abstention_correct": False,
        "unsupported_claim_count": 0,
        "model_turns": 1,
        "tool_calls": 1 if condition == "mcp" else 0,
        "end_to_end_ms": 10.0,
    }


class EvaluationTests(unittest.TestCase):
    def test_primary_contrast_is_derived(self) -> None:
        tasks = evaluator.load_tasks()
        result = evaluator.summarize([record("local", "mcp"), record("remote", "mcp")], tasks)
        self.assertEqual(result["local_minus_remote_mcp_success_rate"], 0.0)

    def test_incorrect_answer_fails_end_to_end(self) -> None:
        tasks = evaluator.load_tasks()
        self.assertFalse(evaluator.task_success(tasks["direct-001"], record("local", "mcp", False)))

    def test_unsupported_claim_fails_end_to_end(self) -> None:
        tasks = evaluator.load_tasks()
        reviewed = record("local", "mcp")
        reviewed["unsupported_claim_count"] = 1
        self.assertFalse(evaluator.task_success(tasks["direct-001"], reviewed))


if __name__ == "__main__":
    unittest.main()
