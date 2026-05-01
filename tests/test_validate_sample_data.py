from pathlib import Path

import validate_sample_data

EXAMPLES = Path(__file__).resolve().parent.parent / "examples" / "offline"


def test_offline_examples_pass_validation():
    errors = validate_sample_data.validate(EXAMPLES)
    assert errors == [], f"validation errors: {errors}"


def test_missing_field_is_detected(tmp_path):
    # Build a minimal sales-report.json missing a required field
    bad_dir = tmp_path / "bad"
    bad_dir.mkdir()
    (bad_dir / "sales-report.json").write_text(
        '{"records": [{"project_id": "x"}]}', encoding="utf-8"
    )
    # Provide stubs for the other files so we exercise the detector path
    for filename in [
        "scenario-packages.json",
        "product-capabilities.json",
        "case-library.json",
    ]:
        (bad_dir / filename).write_text('{"records": [{}]}', encoding="utf-8")

    errors = validate_sample_data.validate(bad_dir)
    assert any("missing field" in e for e in errors)


def test_public_safe_required_for_cases(tmp_path):
    bad_dir = tmp_path / "cases"
    bad_dir.mkdir()
    src = EXAMPLES
    for filename in [
        "sales-report.json",
        "scenario-packages.json",
        "product-capabilities.json",
    ]:
        (bad_dir / filename).write_text((src / filename).read_text(encoding="utf-8"), encoding="utf-8")
    (bad_dir / "case-library.json").write_text(
        '{"records": [{"case_id":"X","industry":"i","customer_profile":"p","scenario_tags":["S"],'
        '"pain_points":["p"],"solution_summary":"s","product_lines":["l"],"outcome":"o",'
        '"public_safe": false}]}',
        encoding="utf-8",
    )

    errors = validate_sample_data.validate(bad_dir)
    assert any("public_safe" in e for e in errors)
