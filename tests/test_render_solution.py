from pathlib import Path

import collect_context
import render_solution

EXAMPLES = Path(__file__).resolve().parent.parent / "examples" / "offline"

REQUIRED_HEADERS = (
    "# Project Recognition Card",
    "# Follow-Up Checklist",
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


def _render():
    raw = collect_context.load_offline(EXAMPLES)
    ctx = collect_context.build_context(raw)
    return render_solution.render(ctx)


def test_render_contains_all_required_headers():
    md = _render()
    missing = [h for h in REQUIRED_HEADERS if h not in md]
    assert not missing, f"missing headers: {missing}"


def test_render_includes_demo_data_callout():
    md = _render()
    assert "Demo data" in md and "fictional" in md.lower()


def test_render_includes_subject_consistency_reminder():
    md = _render()
    assert "subject-consistency" in md.lower() or "subject consistency" in md.lower()


def test_render_matches_committed_golden_file():
    md = _render()
    golden = (EXAMPLES / "expected-output.md").read_text(encoding="utf-8")
    assert md == golden, (
        "Renderer output drifted from examples/offline/expected-output.md. "
        "If the change is intentional, regenerate the golden file via:\n"
        "  python skills/ai-presales/scripts/collect_context.py "
        "--offline examples/offline --out /tmp/c.json && "
        "python skills/ai-presales/scripts/render_solution.py "
        "--context /tmp/c.json --out examples/offline/expected-output.md"
    )
