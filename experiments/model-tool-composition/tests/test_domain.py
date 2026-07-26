from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("composition_domain", ROOT / "common/domain.py")
assert SPEC and SPEC.loader
domain = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(domain)


class DomainTests(unittest.TestCase):
    def test_full_summary(self) -> None:
        self.assertEqual(
            domain.summarize_orders(),
            {
                "filters": {"category": None, "placed_on_or_after": None},
                "order_count": 9,
                "revenue": "498.00",
                "revenue_by_category": {
                    "amber": "106.00",
                    "cobalt": "238.00",
                    "verdant": "154.00",
                },
            },
        )

    def test_filtered_summary(self) -> None:
        actual = domain.summarize_orders("cobalt", "2026-03-01")
        self.assertEqual(actual["order_count"], 1)
        self.assertEqual(actual["revenue"], "48.00")

    def test_policy_is_fictional_and_deterministic(self) -> None:
        self.assertEqual(
            domain.get_return_policy("verdant"),
            {
                "category": "verdant",
                "return_window_days": 30,
                "restocking_fee_percent": 0,
                "condition": "Unused items with the fictional Norvale tag attached",
            },
        )

    def test_unknown_category_fails(self) -> None:
        with self.assertRaisesRegex(ValueError, "unknown category"):
            domain.get_return_policy("ultraviolet")

    def test_task_manifest_is_unique_and_complete(self) -> None:
        tasks = [
            json.loads(line)
            for line in (ROOT / "tasks/tasks.jsonl").read_text(encoding="utf-8").splitlines()
        ]
        identifiers = [task["task_id"] for task in tasks]
        self.assertEqual(len(identifiers), len(set(identifiers)))
        self.assertEqual(len(tasks), 10)


if __name__ == "__main__":
    unittest.main()
