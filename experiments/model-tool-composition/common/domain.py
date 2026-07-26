"""Deterministic controlled-domain operations used by both study conditions."""

from __future__ import annotations

import csv
import json
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

INPUT_DIR = Path(__file__).resolve().parent / "input"
VALID_CATEGORIES = {"amber", "cobalt", "verdant"}


def parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"invalid ISO date: {value}") from exc


def summarize_orders(
    category: str | None = None, placed_on_or_after: str | None = None
) -> dict[str, Any]:
    """Return deterministic filtered order counts and revenue."""
    normalized_category = category.lower() if category else None
    if normalized_category and normalized_category not in VALID_CATEGORIES:
        raise ValueError(f"unknown category: {category}")
    start_date = parse_date(placed_on_or_after) if placed_on_or_after else None
    order_count = 0
    revenue = Decimal(0)
    by_category: dict[str, Decimal] = {}
    try:
        with (INPUT_DIR / "orders.csv").open(encoding="utf-8", newline="") as source:
            for row in csv.DictReader(source):
                row_date = parse_date(row["placed_on"])
                row_category = row["category"]
                if normalized_category and row_category != normalized_category:
                    continue
                if start_date and row_date < start_date:
                    continue
                try:
                    row_revenue = int(row["quantity"]) * Decimal(row["unit_price"])
                except (ValueError, InvalidOperation) as exc:
                    raise ValueError(f"invalid controlled order {row['order_id']}") from exc
                order_count += 1
                revenue += row_revenue
                by_category[row_category] = by_category.get(row_category, Decimal(0)) + row_revenue
    except OSError as exc:
        raise ValueError(f"cannot read controlled orders: {exc}") from exc
    return {
        "filters": {
            "category": normalized_category,
            "placed_on_or_after": placed_on_or_after,
        },
        "order_count": order_count,
        "revenue": f"{revenue:.2f}",
        "revenue_by_category": {key: f"{value:.2f}" for key, value in sorted(by_category.items())},
    }


def get_return_policy(category: str) -> dict[str, Any]:
    """Return the fictional policy for one known category."""
    normalized = category.lower()
    if normalized not in VALID_CATEGORIES:
        raise ValueError(f"unknown category: {category}")
    try:
        policies = json.loads((INPUT_DIR / "policies.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read controlled policies: {exc}") from exc
    return {"category": normalized, **policies[normalized]}
