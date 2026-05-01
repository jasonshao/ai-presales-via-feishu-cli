# Scenario Package Schema

A scenario package describes a presales situation the agent should recognize and how to handle it. Both the offline JSON files in `examples/offline/scenario-packages.json` and the live Feishu Bitable rows must conform to this schema.

## Required fields

| Field | Type | Notes |
|---|---|---|
| `scenario_id` | string | Stable, uppercase snake-case id. Example: `PAY_API_MINIPROGRAM`. Used as a key by capabilities and cases. |
| `scenario_name` | string | Human-readable name. Shown in the recognition card. |
| `trigger_keywords` | string[] | Used by the deterministic matcher in `collect_context.py`. Mix English and Chinese as needed. Each keyword should be a phrase that strongly suggests the scenario, not a generic word. |
| `entry_conditions` | string[] | Plain-English bullets the agent confirms before drafting. |
| `confirmation_checklist` | string[] | 5–8 questions sales must answer. Drives the "missing facts" output. |
| `decision_rules` | string[] | Rules of the form "if X then Y" the agent applies during drafting. |
| `supported_outputs` | string[] | What the scenario can produce (e.g. recognition card, follow-up checklist, customer solution draft). |
| `fallback_message` | string | What to say when entry conditions are not met. |

## Optional fields

| Field | Type | Notes |
|---|---|---|
| `linked_capabilities` | string[] | Capability `capability_name` values to prefer for this scenario. Useful when one capability serves many scenarios. |
| `notes_for_agent` | string | Free-text agent guidance, e.g. "always escalate if signing entity differs from merchant of record". |

## Authoring tips

- Keep `trigger_keywords` specific. `"payment"` alone matches every scenario; `"in-app payment"` does not.
- Phrase `confirmation_checklist` items as questions the sales owner can paste verbatim into the customer chat.
- `decision_rules` should be deterministic — they are referenced by the agent as guardrails, not as suggestions.

## Adding a new scenario

1. Add the JSON record to `examples/offline/scenario-packages.json`.
2. Run `python skills/ai-presales/scripts/validate_sample_data.py examples/offline`.
3. Add a fictional case to `examples/offline/case-library.json` with the new `scenario_id` in `scenario_tags`.
4. Run `python -m pytest`.
