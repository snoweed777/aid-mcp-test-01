"""Validate employees.json shape and demo count."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EMPLOYEES = ROOT / "employees.json"

REQUIRED_KEYS = (
    "name",
    "email",
    "phone",
    "address",
    "department",
    "salary",
    "evaluation",
    "my_number",
    "gender",
)

_ALLOWED_GENDER = frozenset({"男性", "女性"})


def test_employees_file_exists() -> None:
    assert EMPLOYEES.is_file(), f"missing {EMPLOYEES}"


def test_employees_is_non_empty_array() -> None:
    with EMPLOYEES.open(encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, list)
    assert len(data) >= 1


def test_employees_demo_count() -> None:
    with EMPLOYEES.open(encoding="utf-8") as f:
        data = json.load(f)
    assert len(data) == 20, "demo spec expects 20 employees"


def test_each_employee_has_required_fields() -> None:
    with EMPLOYEES.open(encoding="utf-8") as f:
        data = json.load(f)
    for i, row in enumerate(data):
        assert isinstance(row, dict), f"row {i} not an object"
        for key in REQUIRED_KEYS:
            assert key in row, f"row {i} missing {key}"
        assert isinstance(row["salary"], int)
        assert row["salary"] > 0
        assert row["gender"] in _ALLOWED_GENDER


def test_employee_names_unique() -> None:
    with EMPLOYEES.open(encoding="utf-8") as f:
        data = json.load(f)
    names = [r["name"] for r in data]
    assert len(names) == len(set(names)), "duplicate employee name"
