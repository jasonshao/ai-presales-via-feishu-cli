#!/usr/bin/env python3
"""Validate offline sample data against the schemas in the design doc.

Usage:
    python skills/ai-presales/scripts/validate_sample_data.py examples/offline

Exit code 0 if all files are present and every record has the required fields.
Non-zero with a human-readable error otherwise.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable

REQUIRED_FIELDS = {
    "sales-report.json": [
        "project_id",
        "customer_name",
        "industry",
        "sales_owner",
        "report_summary",
        "known_requirements",
        "current_system",
        "transaction_scale",
        "expected_solution",
        "deadline",
        "raw_notes",
    ],
    "scenario-packages.json": [
        "scenario_id",
        "scenario_name",
        "trigger_keywords",
        "entry_conditions",
        "confirmation_checklist",
        "decision_rules",
        "supported_outputs",
        "fallback_message",
    ],
    "product-capabilities.json": [
        "product_line",
        "capability_name",
        "applicable_scenarios",
        "value_proposition",
        "constraints",
        "implementation_notes",
        "sales_talk_track",
    ],
    "case-library.json": [
        "case_id",
        "industry",
        "customer_profile",
        "scenario_tags",
        "pain_points",
        "solution_summary",
        "product_lines",
        "outcome",
        "public_safe",
    ],
}


def load_records(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    if not isinstance(payload, dict) or "records" not in payload:
        raise ValueError(f"{path}: top level must be an object with a 'records' array")
    records = payload["records"]
    if not isinstance(records, list) or not records:
        raise ValueError(f"{path}: 'records' must be a non-empty array")
    return records


def check_record(filename: str, idx: int, record: dict, fields: Iterable[str]) -> list[str]:
    errors = []
    for field in fields:
        if field not in record:
            errors.append(f"{filename}[{idx}] missing field: {field}")
            continue
        value = record[field]
        if value is None or (isinstance(value, str) and not value.strip()):
            errors.append(f"{filename}[{idx}] empty field: {field}")
    return errors


def validate(directory: Path) -> list[str]:
    errors: list[str] = []
    for filename, fields in REQUIRED_FIELDS.items():
        path = directory / filename
        if not path.exists():
            errors.append(f"missing file: {path}")
            continue
        try:
            records = load_records(path)
        except (json.JSONDecodeError, ValueError) as exc:
            errors.append(str(exc))
            continue
        for idx, record in enumerate(records):
            errors.extend(check_record(filename, idx, record, fields))

    case_path = directory / "case-library.json"
    if case_path.exists():
        try:
            cases = load_records(case_path)
        except (json.JSONDecodeError, ValueError):
            cases = []
        for idx, case in enumerate(cases):
            if case.get("public_safe") is not True:
                errors.append(
                    f"case-library.json[{idx}] public_safe must be true for offline demo data"
                )
    return errors


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, help="path to offline examples directory")
    args = parser.parse_args(argv)

    if not args.directory.is_dir():
        print(f"not a directory: {args.directory}", file=sys.stderr)
        return 2

    errors = validate(args.directory)
    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        return 1

    print(f"OK: validated sample data in {args.directory}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
