#!/usr/bin/env python3
"""Collect presales context for the renderer.

Offline mode reads JSON files from a directory:
    python collect_context.py --offline examples/offline --out /tmp/context.json

Live mode shells out to ``lark-cli`` (Feishu CLI) to read a Bitable. It expects
the table-id environment variables documented in examples/live/env.example::

    PRESALES_BASE_TOKEN
    PRESALES_REPORT_TABLE
    PRESALES_SCENARIO_TABLE
    PRESALES_CAPABILITY_TABLE
    PRESALES_CASE_TABLE

The script is deterministic: scenario matching uses keyword overlap, not an LLM.
The agent is expected to do higher-quality reasoning on top of this output.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

OFFLINE_FILES = {
    "sales_reports": "sales-report.json",
    "scenarios": "scenario-packages.json",
    "capabilities": "product-capabilities.json",
    "cases": "case-library.json",
}

LIVE_TABLE_ENV = {
    "sales_reports": "PRESALES_REPORT_TABLE",
    "scenarios": "PRESALES_SCENARIO_TABLE",
    "capabilities": "PRESALES_CAPABILITY_TABLE",
    "cases": "PRESALES_CASE_TABLE",
}


def load_offline(directory: Path) -> dict[str, list[dict]]:
    data: dict[str, list[dict]] = {}
    for key, filename in OFFLINE_FILES.items():
        path = directory / filename
        if not path.exists():
            raise FileNotFoundError(f"missing {path}")
        with path.open("r", encoding="utf-8") as f:
            payload = json.load(f)
        records = payload.get("records", []) if isinstance(payload, dict) else []
        data[key] = records
    return data


def _run_lark_cli(args: list[str]) -> dict:
    if shutil.which("lark-cli") is None:
        raise RuntimeError("lark-cli not found on PATH; install Feishu CLI first")
    proc = subprocess.run(
        ["lark-cli", *args, "--format", "json"],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"lark-cli failed: {' '.join(args)}\n{proc.stderr}")
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"lark-cli returned non-JSON output for {' '.join(args)}: {exc}")


def load_live() -> dict[str, list[dict]]:
    base_token = os.environ.get("PRESALES_BASE_TOKEN")
    if not base_token:
        raise RuntimeError("PRESALES_BASE_TOKEN is not set; see examples/live/env.example")

    data: dict[str, list[dict]] = {}
    for key, env_var in LIVE_TABLE_ENV.items():
        table_id = os.environ.get(env_var)
        if not table_id:
            raise RuntimeError(f"{env_var} is not set; see examples/live/env.example")
        payload = _run_lark_cli(
            [
                "base",
                "+record-list",
                "--base-token",
                base_token,
                "--table-id",
                table_id,
                "--limit",
                "200",
            ]
        )
        records = _extract_records(payload)
        data[key] = records
    return data


def _extract_records(payload: Any) -> list[dict]:
    """Best-effort extraction of records from various lark-cli JSON shapes."""
    if isinstance(payload, list):
        return [r for r in payload if isinstance(r, dict)]
    if isinstance(payload, dict):
        if isinstance(payload.get("records"), list):
            inner = []
            for item in payload["records"]:
                if isinstance(item, dict) and isinstance(item.get("fields"), dict):
                    inner.append(item["fields"])
                elif isinstance(item, dict):
                    inner.append(item)
            return inner
        if isinstance(payload.get("data"), dict):
            return _extract_records(payload["data"])
        if isinstance(payload.get("items"), list):
            return _extract_records(payload["items"])
    return []


def _tokenize(text: str) -> set[str]:
    if not text:
        return set()
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9_-]+|[一-鿿]+", text.lower())
    return {t for t in tokens if len(t) >= 3 or re.match(r"[一-鿿]", t)}


def _report_text(report: dict) -> str:
    parts = [
        report.get("report_summary", ""),
        " ".join(report.get("known_requirements", []) or []),
        report.get("current_system", ""),
        report.get("expected_solution", ""),
        report.get("raw_notes", ""),
    ]
    return " ".join(p for p in parts if p)


def match_scenario(report: dict, scenarios: list[dict]) -> dict:
    text = _report_text(report).lower()
    text_tokens = _tokenize(text)
    scored: list[dict] = []
    for scenario in scenarios:
        keywords = scenario.get("trigger_keywords", []) or []
        hits = []
        for kw in keywords:
            kw_lower = (kw or "").lower()
            if not kw_lower:
                continue
            if kw_lower in text or _tokenize(kw_lower).issubset(text_tokens):
                hits.append(kw)
        score = len(hits)
        confidence = "high" if score >= 3 else "medium" if score == 2 else "low"
        scored.append(
            {
                "scenario_id": scenario.get("scenario_id"),
                "scenario_name": scenario.get("scenario_name"),
                "score": score,
                "confidence": confidence,
                "matched_keywords": hits,
                "scenario": scenario,
            }
        )
    scored.sort(key=lambda x: (-x["score"], x["scenario_id"] or ""))
    return scored[0] if scored else {}


def select_cases(scenario_id: str, cases: list[dict], limit: int = 2) -> list[dict]:
    matched = [c for c in cases if scenario_id and scenario_id in (c.get("scenario_tags") or [])]
    return matched[:limit]


def select_capabilities(scenario_id: str, capabilities: list[dict]) -> list[dict]:
    return [
        c for c in capabilities if scenario_id and scenario_id in (c.get("applicable_scenarios") or [])
    ]


def assess_completeness(report: dict, scenario: dict) -> dict:
    checklist = scenario.get("confirmation_checklist", []) or []
    raw = _report_text(report).lower()
    answered, missing = [], []
    for question in checklist:
        q_tokens = _tokenize(question)
        meaningful = {t for t in q_tokens if len(t) >= 4}
        overlap = meaningful & _tokenize(raw)
        if meaningful and len(overlap) >= max(1, len(meaningful) // 5):
            answered.append({"question": question, "evidence": sorted(overlap)})
        else:
            missing.append(question)
    total = len(checklist) or 1
    completeness = round(len(answered) / total, 2)
    return {
        "checklist_total": len(checklist),
        "answered": answered,
        "missing": missing,
        "completeness_score": completeness,
    }


def build_context(raw: dict[str, list[dict]]) -> dict:
    reports = raw.get("sales_reports", []) or []
    if not reports:
        raise RuntimeError("no sales reports found; cannot build context")
    report = reports[0]
    scenarios = raw.get("scenarios", []) or []
    capabilities = raw.get("capabilities", []) or []
    cases = raw.get("cases", []) or []

    match = match_scenario(report, scenarios)
    scenario_id = match.get("scenario_id") or ""
    completeness = assess_completeness(report, match.get("scenario", {}))
    matched_capabilities = select_capabilities(scenario_id, capabilities)
    similar_cases = select_cases(scenario_id, [c for c in cases if c.get("public_safe") is True])

    return {
        "version": 1,
        "source_mode": raw.get("_source_mode", "offline"),
        "report": report,
        "scenario_match": {
            "scenario_id": match.get("scenario_id"),
            "scenario_name": match.get("scenario_name"),
            "confidence": match.get("confidence"),
            "score": match.get("score"),
            "matched_keywords": match.get("matched_keywords", []),
            "fallback_message": match.get("scenario", {}).get("fallback_message"),
        },
        "completeness": completeness,
        "capabilities": matched_capabilities,
        "similar_cases": similar_cases,
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--offline", type=Path, help="path to offline examples directory")
    group.add_argument("--live", action="store_true", help="read from Feishu via lark-cli")
    parser.add_argument("--out", type=Path, required=True, help="path to write context JSON")
    args = parser.parse_args(argv)

    if args.offline:
        raw = load_offline(args.offline)
        raw["_source_mode"] = "offline"  # type: ignore[assignment]
    else:
        raw = load_live()
        raw["_source_mode"] = "live"  # type: ignore[assignment]

    context = build_context(raw)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as f:
        json.dump(context, f, indent=2, ensure_ascii=False)
    print(f"OK: wrote context to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
