#!/usr/bin/env python3
"""Render the customer solution draft (Markdown) from a context JSON.

Usage:
    python render_solution.py --context /tmp/context.json --out /tmp/solution.md

The output is a single Markdown file containing three artifacts:
1. Project recognition card.
2. Follow-up checklist.
3. Customer-facing solution draft (per design doc §10.3).

The draft is intentionally cautious: assumptions and missing facts are surfaced
explicitly so the human reviewer can correct them before sending to a customer.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable

DRAFT_TEMPLATE_HEADERS = (
    "## 1. Customer Background And Needs",
    "### Business Context",
    "### Core Pain Points",
    "### Target Outcome",
    "## 2. Recommended Solution",
    "### Solution Overview",
    "### Product Capability Match",
    "### Technical Flow",
    "## 3. Similar Cases",
    "## 4. Assumptions And Open Questions",
)


def _bullets(items: Iterable[str], placeholder: str = "_(no items)_") -> str:
    items = [i for i in items if i]
    if not items:
        return placeholder
    return "\n".join(f"- {item}" for item in items)


def _required(value, fallback: str = "_(missing — confirm with sales)_") -> str:
    if value is None:
        return fallback
    if isinstance(value, str) and not value.strip():
        return fallback
    return str(value)


def render_recognition_card(ctx: dict) -> str:
    report = ctx["report"]
    match = ctx["scenario_match"]
    completeness = ctx["completeness"]

    return "\n".join(
        [
            "# Project Recognition Card",
            "",
            f"- **Customer:** {_required(report.get('customer_name'))}",
            f"- **Industry:** {_required(report.get('industry'))}",
            f"- **Sales owner:** {_required(report.get('sales_owner'))}",
            f"- **Candidate scenario:** {_required(match.get('scenario_name'))} "
            f"(`{_required(match.get('scenario_id'))}`)",
            f"- **Confidence:** {_required(match.get('confidence'))} "
            f"(score: {match.get('score', 0)})",
            f"- **Matched keywords:** {', '.join(match.get('matched_keywords') or []) or '_(none)_'}",
            f"- **Completeness:** {completeness.get('completeness_score', 0):.0%} "
            f"of {completeness.get('checklist_total', 0)} checklist items",
            f"- **Deadline:** {_required(report.get('deadline'))}",
            "",
            "## Why this scenario",
            "",
            (
                "The sales report contains language strongly consistent with the "
                f"`{_required(match.get('scenario_id'))}` scenario. Confirm the entry "
                "conditions before drafting commercial terms."
            ),
            "",
            "## Next action",
            "",
            (
                "Run the follow-up checklist below with sales, then update the report "
                "before sending the solution draft to the customer."
            ),
        ]
    )


def render_checklist(ctx: dict) -> str:
    completeness = ctx["completeness"]
    answered = completeness.get("answered", [])
    missing = completeness.get("missing", [])

    lines = [
        "# Follow-Up Checklist",
        "",
        f"_{len(answered)} answered, {len(missing)} missing of "
        f"{completeness.get('checklist_total', 0)} required items._",
        "",
        "## Missing — ask sales before drafting",
        "",
        _bullets(missing, "_(none — proceed to drafting)_"),
        "",
        "## Already covered in the report",
        "",
        _bullets((a["question"] for a in answered), "_(none yet)_"),
    ]
    return "\n".join(lines)


def render_solution_draft(ctx: dict) -> str:
    report = ctx["report"]
    match = ctx["scenario_match"]
    capabilities = ctx.get("capabilities", []) or []
    cases = ctx.get("similar_cases", []) or []
    completeness = ctx["completeness"]
    customer = _required(report.get("customer_name"))

    capability_lines = []
    for cap in capabilities:
        name = cap.get("capability_name", "Capability")
        value = cap.get("value_proposition", "").strip()
        constraints = cap.get("constraints", []) or []
        capability_lines.append(f"- **{name}** — {value}")
        for constraint in constraints:
            capability_lines.append(f"  - Constraint: {constraint}")
    capability_block = "\n".join(capability_lines) or "_(no matching capabilities — escalate)_"

    case_lines = []
    for case in cases:
        case_lines.append(
            "- **{cid}** — {industry}: {summary} (Outcome: {outcome})".format(
                cid=case.get("case_id", ""),
                industry=case.get("industry", ""),
                summary=case.get("solution_summary", ""),
                outcome=case.get("outcome", ""),
            )
        )
    case_block = "\n".join(case_lines) or "_(no public-safe similar cases on file)_"

    flow_steps = []
    for cap in capabilities:
        for note in cap.get("implementation_notes", []) or []:
            flow_steps.append(note)
    flow_block = _bullets(flow_steps, "_(no implementation notes available)_")

    open_questions = completeness.get("missing", []) or []
    open_block = _bullets(
        open_questions, "_(no open questions — final review with sales recommended)_"
    )

    body = [
        f"# {customer} x [Your Company] Solution Draft",
        "",
        "> **Demo data — fictional customer.** This draft is generated by "
        "the Feishu CLI AI Presales Skill and must be reviewed by a human "
        "before sending to a customer.",
        "",
        DRAFT_TEMPLATE_HEADERS[0],
        "",
        DRAFT_TEMPLATE_HEADERS[1],
        "",
        _required(report.get("report_summary")),
        "",
        DRAFT_TEMPLATE_HEADERS[2],
        "",
        _bullets(report.get("known_requirements") or [], "_(no pain points captured)_"),
        "",
        DRAFT_TEMPLATE_HEADERS[3],
        "",
        _required(report.get("expected_solution")),
        "",
        DRAFT_TEMPLATE_HEADERS[4],
        "",
        DRAFT_TEMPLATE_HEADERS[5],
        "",
        (
            "Recommended scenario: **{name}** (`{sid}`, confidence {conf}). "
            "Current report covers {pct:.0%} of the required confirmation "
            "checklist; remaining items are listed in section 4."
        ).format(
            name=match.get("scenario_name", ""),
            sid=match.get("scenario_id", ""),
            conf=match.get("confidence", ""),
            pct=completeness.get("completeness_score", 0),
        ),
        "",
        DRAFT_TEMPLATE_HEADERS[6],
        "",
        capability_block,
        "",
        DRAFT_TEMPLATE_HEADERS[7],
        "",
        flow_block,
        "",
        DRAFT_TEMPLATE_HEADERS[8],
        "",
        case_block,
        "",
        DRAFT_TEMPLATE_HEADERS[9],
        "",
        "Open questions before commercial commitment:",
        "",
        open_block,
        "",
        "Subject-consistency reminder: the entity that signs with us must "
        "match the WeChat Pay merchant account holder. Do not commit before "
        "this is confirmed.",
    ]
    return "\n".join(body)


def render(ctx: dict) -> str:
    parts = [
        render_recognition_card(ctx),
        render_checklist(ctx),
        render_solution_draft(ctx),
    ]
    return "\n\n---\n\n".join(parts) + "\n"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--context", type=Path, required=True, help="path to context JSON")
    parser.add_argument("--out", type=Path, required=True, help="path to write Markdown output")
    args = parser.parse_args(argv)

    with args.context.open("r", encoding="utf-8") as f:
        ctx = json.load(f)

    md = render(ctx)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as f:
        f.write(md)
    print(f"OK: wrote solution Markdown to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
