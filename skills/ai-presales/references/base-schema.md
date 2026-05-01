# Feishu Bitable Schema (Live Mode)

This is the field mapping the live mode expects when reading from Feishu Bitable via `lark-cli base +record-list`. The offline JSON files use the same field names so the renderer is mode-agnostic.

## Sales report table (`PRESALES_REPORT_TABLE`)

| Bitable column | JSON key | Type | Required |
|---|---|---|---|
| Project ID | `project_id` | text | yes |
| Customer Name | `customer_name` | text | yes |
| Industry | `industry` | text | yes |
| Sales Owner | `sales_owner` | text or person | yes |
| Report Summary | `report_summary` | text | yes |
| Known Requirements | `known_requirements` | multi-text or array | yes |
| Current System | `current_system` | text | yes |
| Transaction Scale | `transaction_scale` | text | yes |
| Expected Solution | `expected_solution` | text | yes |
| Deadline | `deadline` | text or date | yes |
| Raw Notes | `raw_notes` | text | yes |

For person-type or array-type fields, the agent should normalize to plain strings and lists respectively before passing to `render_solution.py`.

## Scenario package table (`PRESALES_SCENARIO_TABLE`)

See `scenario-package-schema.md`. Each Bitable row maps 1:1 to a scenario record.

## Product capability table (`PRESALES_CAPABILITY_TABLE`)

| Bitable column | JSON key | Type | Required |
|---|---|---|---|
| Product Line | `product_line` | text | yes |
| Capability Name | `capability_name` | text | yes |
| Applicable Scenarios | `applicable_scenarios` | multi-text | yes |
| Value Proposition | `value_proposition` | text | yes |
| Constraints | `constraints` | multi-text | yes |
| Implementation Notes | `implementation_notes` | multi-text | yes |
| Sales Talk Track | `sales_talk_track` | text | yes |

## Case library table (`PRESALES_CASE_TABLE`)

| Bitable column | JSON key | Type | Required |
|---|---|---|---|
| Case ID | `case_id` | text | yes |
| Industry | `industry` | text | yes |
| Customer Profile | `customer_profile` | text | yes |
| Scenario Tags | `scenario_tags` | multi-text | yes |
| Pain Points | `pain_points` | multi-text | yes |
| Solution Summary | `solution_summary` | text | yes |
| Product Lines | `product_lines` | multi-text | yes |
| Outcome | `outcome` | text | yes |
| Public Safe | `public_safe` | checkbox | yes |

Only rows with `public_safe = true` are eligible for inclusion in offline examples.

## Project status table (`PRESALES_STATUS_TABLE`)

| Bitable column | JSON key | Type | Required |
|---|---|---|---|
| Project ID | `project_id` | text | yes |
| Customer Name | `customer_name` | text | no |
| Scenario ID | `scenario_id` | text | no |
| Confidence | `confidence` | single-select | no |
| Missing Info Count | `missing_info_count` | number | no |
| Solution Doc URL | `solution_doc_url` | url | no |
| Status | `status` | single-select | yes |
| Last Generated At | `last_generated_at` | datetime | no |

Used for `lark-cli base +record-upsert` writes after the agent renders a draft.

## Output folder (`PRESALES_OUTPUT_FOLDER_TOKEN`)

A Feishu Drive folder token where generated solution drafts are saved via `lark-cli docs +create`. Always use a demo folder; never write into a real customer-facing folder without explicit user approval.
