from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "common/summarize.py"
SPEC = importlib.util.spec_from_file_location("summarize", MODULE_PATH)
assert SPEC and SPEC.loader
summarize = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(summarize)


class SummarizeTests(unittest.TestCase):
    def test_fixture_matches_expected(self) -> None:
        actual, _ = summarize.summarize_file(ROOT / "common/input/orders.csv")
        expected = json.loads((ROOT / "common/expected/summary.json").read_text())
        self.assertEqual(expected, actual)

    def test_serialization_is_deterministic(self) -> None:
        summary, _ = summarize.summarize_file(ROOT / "common/input/orders.csv")
        with tempfile.TemporaryDirectory() as temporary:
            first = Path(temporary) / "first.json"
            second = Path(temporary) / "second.json"
            summarize.write_summary(first, summary)
            summarize.write_summary(second, summary)
            self.assertEqual(first.read_bytes(), second.read_bytes())

    def test_invalid_columns_fail_clearly(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            invalid = Path(temporary) / "invalid.csv"
            invalid.write_text("order_id,category\n1,books\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "CSV must contain columns"):
                summarize.summarize_file(invalid)


if __name__ == "__main__":
    unittest.main()
