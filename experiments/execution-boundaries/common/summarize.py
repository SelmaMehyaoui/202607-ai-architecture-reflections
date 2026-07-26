"""Shared deterministic order-summary business logic."""

from __future__ import annotations

import csv
import json
from collections.abc import Iterable, Mapping
from decimal import Decimal, InvalidOperation
from pathlib import Path
from time import perf_counter_ns
from typing import Any

REQUIRED_FIELDS = {"order_id", "category", "quantity", "unit_price"}


def summarize_records(records: Iterable[Mapping[str, str]]) -> dict[str, Any]:
    order_count = 0
    total_revenue = Decimal(0)
    counts: dict[str, int] = {}
    revenues: dict[str, Decimal] = {}
    for row_number, row in enumerate(records, start=2):
        try:
            category = row["category"].strip()
            quantity = int(row["quantity"])
            unit_price = Decimal(row["unit_price"])
        except (KeyError, ValueError, InvalidOperation) as exc:
            raise ValueError(f"invalid order at CSV row {row_number}: {exc}") from exc
        if not category or quantity < 0 or unit_price < 0:
            raise ValueError(f"invalid order at CSV row {row_number}: values must be non-negative")
        order_count += 1
        revenue = quantity * unit_price
        total_revenue += revenue
        counts[category] = counts.get(category, 0) + 1
        revenues[category] = revenues.get(category, Decimal(0)) + revenue

    return {
        "total_orders": order_count,
        "total_revenue": f"{total_revenue:.2f}",
        "order_count_by_category": dict(sorted(counts.items())),
        "revenue_by_category": {key: f"{value:.2f}" for key, value in sorted(revenues.items())},
    }


def summarize_file(input_path: Path) -> tuple[dict[str, Any], int]:
    started = perf_counter_ns()
    try:
        with input_path.open(encoding="utf-8", newline="") as source:
            reader = csv.DictReader(source)
            if reader.fieldnames is None or not REQUIRED_FIELDS.issubset(reader.fieldnames):
                raise ValueError(f"CSV must contain columns: {sorted(REQUIRED_FIELDS)}")
            result = summarize_records(reader)
    except OSError as exc:
        raise ValueError(f"cannot read {input_path}: {exc}") from exc
    return result, perf_counter_ns() - started


def write_summary(output_path: Path, summary: Mapping[str, Any]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        output_path.write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    except OSError as exc:
        raise ValueError(f"cannot write {output_path}: {exc}") from exc


def summarize_to_file(input_path: Path, output_path: Path) -> dict[str, Any]:
    summary, business_logic_ns = summarize_file(input_path)
    write_summary(output_path, summary)
    return {"summary": summary, "business_logic_ns": business_logic_ns}
