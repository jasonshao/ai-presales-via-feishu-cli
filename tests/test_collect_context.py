from pathlib import Path

import collect_context

EXAMPLES = Path(__file__).resolve().parent.parent / "examples" / "offline"


def _build():
    raw = collect_context.load_offline(EXAMPLES)
    return collect_context.build_context(raw)


def test_context_has_required_top_level_keys():
    ctx = _build()
    for key in ("report", "scenario_match", "completeness", "capabilities", "similar_cases"):
        assert key in ctx, f"context missing {key!r}"


def test_demo_matches_pay_api_miniprogram_with_high_confidence():
    ctx = _build()
    match = ctx["scenario_match"]
    assert match["scenario_id"] == "PAY_API_MINIPROGRAM"
    assert match["confidence"] == "high"
    assert match["score"] >= 3


def test_completeness_is_reasonable():
    ctx = _build()
    completeness = ctx["completeness"]
    assert 0.0 <= completeness["completeness_score"] <= 1.0
    assert completeness["checklist_total"] >= 5
    # Demo report intentionally leaves at least one checklist item open
    # so the agent has something to ask sales about.
    assert len(completeness["missing"]) >= 1


def test_capabilities_and_cases_filtered_to_matched_scenario():
    ctx = _build()
    sid = ctx["scenario_match"]["scenario_id"]
    for cap in ctx["capabilities"]:
        assert sid in cap.get("applicable_scenarios", [])
    for case in ctx["similar_cases"]:
        assert sid in case.get("scenario_tags", [])
        assert case.get("public_safe") is True
