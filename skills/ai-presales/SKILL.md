---
name: ai-presales
description: Use this skill when a user asks to analyze a Feishu sales report, generate a presales recognition card, produce a missing-information checklist for sales, or draft a customer-facing solution. Triggers on phrases like "sales report", "presales", "customer solution draft", "recognition card", "follow-up checklist", "lark-cli base", or when the user shares a Feishu Bitable record about a sales opportunity. Skip for unrelated coding, generic chat, or non-presales Feishu tasks.
---

# AI Presales via Feishu CLI

> **Portability note.** This file uses the Claude Code skill format (frontmatter + body), but the body is agent-neutral. Any agent that can read files and run shell commands — Claude Code, Codex, OpenClaw, Cursor, a custom Agent SDK, etc. — can load this document as instructions and drive the workflow. The repo also ships a deterministic offline demo so the workflow can be validated with no agent at all.

Turn a sales report stored in Feishu into:

1. A **project recognition card** (which scenario this opportunity is, and how confident).
2. A **follow-up checklist** of missing facts the sales owner needs to fill in.
3. A **customer-facing solution draft** in Markdown.

The skill always uses [`lark-cli`](https://github.com/larksuite/lark-cli) for Feishu I/O — never raw HTTP or other SDKs. It runs in two modes:

- **Offline mode** (no Feishu credentials needed) — operates on JSON files under `examples/offline/`. Use this for demos, tests, and CI.
- **Live mode** — reads the sales report and reference data from a Feishu Bitable via `lark-cli base +record-list`, and writes the solution back to Feishu Docs via `lark-cli docs +create`.

## When to invoke

Invoke this skill when the user:

- Pastes or references a sales report and asks for analysis.
- Asks to "identify the scenario" or "draft a solution" for a customer.
- Wants a follow-up checklist or recognition card from a report.
- Asks how to read presales data from a Feishu Bitable via `lark-cli`.

Do **not** invoke for unrelated Feishu work (calendar, chat, file storage) or for generic prompt tasks that have no presales structure.

## Required CLI checks

Before live mode, verify Feishu CLI auth:

```bash
lark-cli auth status
```

If `tokenStatus` is not `valid`, stop and ask the user to run `lark-cli auth login` (or fall back to offline mode).

When unsure of a `lark-cli` command shape, prefer:

```bash
lark-cli base +record-list --help
lark-cli docs +create --help
lark-cli schema <service.resource.method> --format pretty
```

over guessing at flags.

## Offline workflow

```bash
# 1. Validate the bundled demo data
python skills/ai-presales/scripts/validate_sample_data.py examples/offline

# 2. Build a single context JSON (deterministic scenario match + completeness)
python skills/ai-presales/scripts/collect_context.py \
  --offline examples/offline \
  --out /tmp/presales-context.json

# 3. Render the recognition card, follow-up checklist, and solution draft
python skills/ai-presales/scripts/render_solution.py \
  --context /tmp/presales-context.json \
  --out /tmp/customer-solution.md
```

The agent (you) should:

1. Run the three commands above.
2. Read `/tmp/customer-solution.md`.
3. Apply real reasoning: the deterministic matcher uses keyword overlap. You must double-check the scenario verdict, fill in any gaps you can fill from the report, and rewrite phrasing where the renderer's defaults are too generic.
4. Surface the final draft to the user, clearly labeled as a draft for human review.

## Live workflow

Required environment variables (see `examples/live/env.example`):

```text
PRESALES_BASE_TOKEN
PRESALES_REPORT_TABLE
PRESALES_SCENARIO_TABLE
PRESALES_CAPABILITY_TABLE
PRESALES_CASE_TABLE
PRESALES_STATUS_TABLE
PRESALES_OUTPUT_FOLDER_TOKEN
```

Steps:

```bash
# 1. Auth check
lark-cli auth status

# 2. Read tables (record list returns JSON; the script does the call)
python skills/ai-presales/scripts/collect_context.py \
  --live \
  --out /tmp/presales-context.json

# 3. Render the draft
python skills/ai-presales/scripts/render_solution.py \
  --context /tmp/presales-context.json \
  --out /tmp/customer-solution.md

# 4. Write the draft into Feishu Docs (only against a demo folder)
lark-cli docs +create \
  --folder-token "$PRESALES_OUTPUT_FOLDER_TOKEN" \
  --title "Customer Solution Draft" \
  --markdown @/tmp/customer-solution.md

# 5. Update project status
lark-cli base +record-upsert \
  --base-token "$PRESALES_BASE_TOKEN" \
  --table-id "$PRESALES_STATUS_TABLE" \
  --json '{"project_id":"demo","status":"draft_generated"}'
```

Do not run step 4 or 5 against a real Feishu workspace without the user's explicit go-ahead. Default to a demo folder.

## Output format requirements

The Markdown output must contain three sections, separated by `---`:

1. `# Project Recognition Card` — customer, scenario, confidence, matched keywords, completeness, next action.
2. `# Follow-Up Checklist` — answered vs. missing checklist items.
3. `# <Customer> x [Your Company] Solution Draft` with sub-headers:
   - `## 1. Customer Background And Needs` (Business Context, Core Pain Points, Target Outcome)
   - `## 2. Recommended Solution` (Solution Overview, Product Capability Match, Technical Flow)
   - `## 3. Similar Cases`
   - `## 4. Assumptions And Open Questions`

Always include a "demo data — fictional" callout when running in offline mode against the bundled examples.

## Privacy rules

See `skills/ai-presales/references/privacy-rules.md`.

Never:

- Commit real customer names, internal cases, or private Feishu URLs.
- Print customer-identifying tokens, app secrets, or session cookies into chat or logs.
- Write live mode output back to a non-demo Feishu folder without explicit user approval.

If the user asks you to write a real customer's name into the bundled `examples/`, refuse and offer to fictionalize it.

## Troubleshooting

| Symptom | Likely cause | Action |
|---|---|---|
| `lark-cli: command not found` | Feishu CLI not installed | Install per upstream docs; fall back to offline mode meanwhile. |
| `tokenStatus: expired` | Auth expired | Run `lark-cli auth login`; re-check with `lark-cli auth status`. |
| Scenario confidence is `low` | Keyword overlap is weak | Ask sales for the missing checklist items before drafting. |
| Renderer crashes on live data | Unexpected Bitable field types | Inspect the raw JSON; align field names with the offline schema in `references/base-schema.md`. |
| `tests/test_privacy_scan.py` fails | A forbidden token leaked into examples or docs | Read the failing line, fictionalize the value, re-run the test. |

## References

- `references/solution-template.md` — Markdown template for the customer solution draft.
- `references/scenario-package-schema.md` — required fields for scenario packages.
- `references/base-schema.md` — Feishu Bitable field mappings used in live mode.
- `references/privacy-rules.md` — public-safe data policy.
