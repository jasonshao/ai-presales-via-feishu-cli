# AI Presales Feishu CLI Skill Design

## 1. Purpose

Build an open-source contest entry for the Feishu CLI Creator Competition:

> Feishu CLI AI Presales Skill: turn a sales report in Feishu into a customer-facing solution draft in about 30 minutes.

The project should demonstrate how an AI agent uses `lark-cli` to enter a real presales workflow: read Feishu business context, identify the customer scenario, generate the missing-information checklist, draft a solution, and write the output back into Feishu.

This is a contest-sized packaging of the existing AI presales MVP concept. It is not a production backend and should not attempt to rebuild the full webhook/FastAPI/state-machine system.

## 2. Success Criteria

The finished repository should satisfy these outcomes:

1. A reviewer can understand the business scenario from the README in under 3 minutes.
2. A reviewer can run a local demo without private Feishu data.
3. A reviewer with Feishu CLI auth can run a live demo against a demo Base or document.
4. The repo includes a proper AI agent Skill (`SKILL.md`) that instructs Claude Code or another agent to use `lark-cli` for the workflow.
5. The demo shows a complete loop:
   - Read a sales report.
   - Read scenario/product/case knowledge.
   - Generate a project recognition card.
   - Generate a sales follow-up checklist.
   - Generate a customer solution draft.
   - Write or prepare the output for Feishu.
6. No real customer data, internal product secrets, private sales records, or confidential case studies are committed.

## 3. Non-Goals

Do not build these for the contest MVP:

1. Full FastAPI service.
2. Webhook listener.
3. Feishu bot card interactions.
4. Multi-tenant admin UI.
5. Production-grade permission management.
6. Real customer case ingestion.
7. Complex vector database or RAG service.
8. Automated deployment.

The contest entry should be a clear, runnable AI-agent workflow, not a production platform.

## 4. Target User

Primary user:

- A junior presales or business expert who receives a sales report and needs a first customer solution draft quickly.

Secondary user:

- An AI agent operator using Claude Code or another coding agent with Feishu CLI access.

Reviewer user:

- Feishu CLI competition judge evaluating whether the project is practical, original, technically feasible, and business-relevant.

## 5. Competition Positioning

Primary award target:

- GitHub Best Practice Award: skill + business workflow + measurable business efficiency.

Secondary award target:

- Honor award through a polished open-source Skill.

Do not optimize primarily for GitHub Stars or social-media virality. The strongest story is practical business value.

## 6. Feishu CLI Integration Layers

### 6.1 Skill Layer

Create a skill folder with a `SKILL.md` that teaches the agent how to perform AI presales work through Feishu CLI.

The Skill should:

- Trigger when the user asks to analyze a sales report, generate a presales checklist, or draft a customer solution.
- Prefer `lark-cli` for all Feishu operations.
- Explain the workflow step by step.
- Include privacy rules.
- Include command examples.
- Point to sample schemas and templates in `references/` or `examples/`.

This is the heart of the contest entry.

### 6.2 Auth Layer

Use Feishu CLI authentication instead of custom OAuth.

Expected command:

```bash
lark-cli auth status
```

The Skill should instruct the agent to verify auth before live mode. If auth is invalid, the agent should fall back to offline demo mode or ask the user to authenticate.

### 6.3 Knowledge Access Layer

Use `lark-cli` to read business knowledge from Feishu:

- `lark-cli docs +fetch` for Wiki/Docx decision guides and templates.
- `lark-cli base +record-list` for sales reports, cases, product capabilities, and scenario packages.
- `lark-cli base +record-search` when selecting records by customer/project/status.
- `lark-cli docs +create` or `lark-cli docs +update` for generated solution output.
- `lark-cli base +record-upsert` for project status and feedback logs.

The public demo should include sample data files so reviewers can run without access to private Feishu resources.

### 6.4 Workflow Layer

The agent should orchestrate the presales flow:

1. Load sales report.
2. Normalize the report into a structured project profile.
3. Match candidate scenario packages.
4. Produce a recognition card.
5. Produce missing-information questions.
6. Match similar cases.
7. Draft the customer-facing solution.
8. Write the result back to Feishu or save local output in offline mode.

### 6.5 Collaboration Layer

The workflow should preserve human review:

- The agent generates a draft, not a final customer commitment.
- The output should clearly mark assumptions and missing facts.
- Sales or presales users can edit the generated Feishu document.
- Feedback can be logged back to a Base table.

### 6.6 Output Asset Layer

Primary output:

- A Markdown customer solution draft that can be written into Feishu Docx.

Secondary outputs:

- Project recognition card.
- Follow-up checklist.
- Similar case references.
- Project status update.
- Feedback log entry.

### 6.7 Measurement Layer

For the contest story, record lightweight metrics:

- Report completeness score.
- Number of missing fields.
- Scenario confidence.
- Draft generation time.
- Output document URL.
- Human review status.

These can be stored in a demo `Project Status` table or a local JSON artifact.

## 7. Recommended Repository Structure

```text
feishu-cli-ai-presales-skill/
  README.md
  LICENSE
  .gitignore
  skills/
    ai-presales/
      SKILL.md
      references/
        solution-template.md
        scenario-package-schema.md
        base-schema.md
        privacy-rules.md
      scripts/
        collect_context.py
        render_solution.py
        validate_sample_data.py
  examples/
    offline/
      sales-report.json
      scenario-packages.json
      product-capabilities.json
      case-library.json
      expected-output.md
    live/
      env.example
      feishu-command-examples.md
  docs/
    architecture.md
    demo-script.md
    contest-submission.md
  tests/
    test_collect_context.py
    test_render_solution.py
```

Keep the repo small. The skill, README, examples, and demo quality matter more than a large codebase.

## 8. Data Model

### 8.1 Sales Report

Minimum fields:

- `project_id`
- `customer_name`
- `industry`
- `sales_owner`
- `report_summary`
- `known_requirements`
- `current_system`
- `transaction_scale`
- `expected_solution`
- `deadline`
- `raw_notes`

### 8.2 Scenario Package

Minimum fields:

- `scenario_id`
- `scenario_name`
- `trigger_keywords`
- `entry_conditions`
- `confirmation_checklist`
- `decision_rules`
- `supported_outputs`
- `fallback_message`

Initial public demo scenarios:

- `PAY_API_MINIPROGRAM`: mini-program payment API integration.
- `SHOP_WECHAT_BASIC`: WeChat shop feasibility and development-scope assessment.

Do not include confidential product strategy. Use public or fictionalized capability descriptions.

### 8.3 Product Capability

Minimum fields:

- `product_line`
- `capability_name`
- `applicable_scenarios`
- `value_proposition`
- `constraints`
- `implementation_notes`
- `sales_talk_track`

### 8.4 Case Library

Minimum fields:

- `case_id`
- `industry`
- `customer_profile`
- `scenario_tags`
- `pain_points`
- `solution_summary`
- `product_lines`
- `outcome`
- `public_safe`

Only records with `public_safe = true` may appear in public examples.

### 8.5 Project Status

Minimum fields:

- `project_id`
- `customer_name`
- `scenario_id`
- `confidence`
- `missing_info_count`
- `solution_doc_url`
- `status`
- `last_generated_at`

## 9. Agent Workflow

### 9.1 Offline Demo Mode

Offline mode uses `examples/offline/*.json`.

Flow:

1. Load sample sales report.
2. Load sample scenario packages.
3. Load sample product capabilities.
4. Load sample cases.
5. Generate:
   - Recognition card.
   - Follow-up checklist.
   - Customer solution draft.
6. Save generated output to a local Markdown file.

Expected local command examples:

```bash
python skills/ai-presales/scripts/validate_sample_data.py examples/offline
python skills/ai-presales/scripts/collect_context.py --offline examples/offline --out /tmp/presales-context.json
python skills/ai-presales/scripts/render_solution.py --context /tmp/presales-context.json --out /tmp/customer-solution.md
```

The exact CLI interface can be adjusted during implementation, but the repo must keep one copy-pastable offline demo path.

### 9.2 Live Feishu Mode

Live mode uses `lark-cli`.

Required environment variables:

```bash
PRESALES_BASE_TOKEN=
PRESALES_REPORT_TABLE=
PRESALES_SCENARIO_TABLE=
PRESALES_CAPABILITY_TABLE=
PRESALES_CASE_TABLE=
PRESALES_STATUS_TABLE=
PRESALES_OUTPUT_FOLDER_TOKEN=
```

Useful commands:

```bash
lark-cli auth status
lark-cli base +record-list --base-token "$PRESALES_BASE_TOKEN" --table-id "$PRESALES_REPORT_TABLE" --limit 20
lark-cli docs +fetch --doc "$PRESALES_DECISION_GUIDE_DOC"
lark-cli docs +create --folder-token "$PRESALES_OUTPUT_FOLDER_TOKEN" --title "Customer Solution Draft" --markdown @/tmp/customer-solution.md
lark-cli base +record-upsert --base-token "$PRESALES_BASE_TOKEN" --table-id "$PRESALES_STATUS_TABLE" --json '{"project_id":"demo","status":"draft_generated"}'
```

The Skill should tell the agent to inspect available CLI schemas with:

```bash
lark-cli schema <service.resource.method> --format pretty
```

or use command help:

```bash
lark-cli base +record-list --help
lark-cli docs +create --help
```

## 10. Output Templates

### 10.1 Project Recognition Card

The recognition card should include:

- Customer name.
- Candidate scenario.
- Confidence.
- Why this scenario was selected.
- Known facts.
- Missing facts.
- Similar cases.
- Next action.

### 10.2 Follow-Up Checklist

The checklist should include 5-8 questions.

Each item should include:

- Question.
- Why it matters.
- Suggested wording to ask sales.
- Current status: known or missing.
- Which scenario rule depends on it.

### 10.3 Customer Solution Draft

The customer-facing draft should use this structure:

```markdown
# <Customer> x <Company> Solution Draft

## 1. Customer Background And Needs

### Business Context

### Core Pain Points

### Target Outcome

## 2. Recommended Solution

### Solution Overview

### Product Capability Match

### Technical Flow

## 3. Similar Cases

## 4. Assumptions And Open Questions
```

Use neutral wording. Avoid unsupported promises.

## 11. Privacy And Open-Source Rules

The implementation must include a public-safe data policy:

1. Never commit real customer names.
2. Never commit internal customer cases.
3. Never commit private Feishu document URLs unless they are public demo docs.
4. Never commit tokens, cookies, app secrets, or exported auth files.
5. Demo cases must be fictionalized.
6. Product capability descriptions must be generic enough for public release.
7. Generated output must label demo data as fictional.

Add these rules to `skills/ai-presales/references/privacy-rules.md`.

## 12. Implementation Tasks For Claude Code

### Task 1: Scaffold Repository

Create the folder structure in section 7.

Add:

- `README.md`
- `LICENSE`
- `.gitignore`
- `skills/ai-presales/SKILL.md`
- `examples/offline/*.json`
- helper scripts
- tests

### Task 2: Write The Skill

`SKILL.md` must include:

- Frontmatter name and description.
- Trigger conditions.
- Required CLI checks.
- Offline mode workflow.
- Live Feishu mode workflow.
- Privacy rules.
- Output format requirements.
- Troubleshooting guidance.

The Skill should be concise enough for an agent to follow, but specific enough to produce consistent output.

### Task 3: Create Public Demo Data

Create fictional sample data for:

- One sales report.
- Two scenario packages.
- Three product capabilities.
- Three similar cases.

Use a fictional customer such as `Beanlight Tea` or `Demo Coffee Chain`.

### Task 4: Build Helper Scripts

Scripts should stay thin and deterministic.

Suggested responsibilities:

- `validate_sample_data.py`: validate required fields.
- `collect_context.py`: merge sales report, scenarios, capabilities, and cases into one context JSON.
- `render_solution.py`: render a deterministic Markdown draft from context.

Do not embed the full AI reasoning in scripts. The Skill and agent should own the reasoning. Scripts exist to make the demo repeatable.

### Task 5: Write README

README should include:

- One-sentence value proposition.
- Problem statement.
- Demo GIF or screenshot placeholder.
- Quick start.
- Offline demo.
- Live Feishu demo.
- Feishu CLI integration points.
- Data privacy note.
- Contest submission summary.

### Task 6: Add Tests

Minimum tests:

- Sample data validates.
- Context collection produces expected keys.
- Solution renderer includes required sections.
- Privacy scan catches suspicious placeholders such as `真实客户`, `token=`, `secret`, or private Feishu URLs in examples.

### Task 7: Prepare Contest Assets

Create:

- `docs/demo-script.md`: 2-3 minute demo narration.
- `docs/contest-submission.md`: title, repo URL placeholder, summary, key screenshots, and award positioning.

## 13. Acceptance Criteria

The project is done when:

1. `lark-cli auth status` is documented and works in live mode if the user is authenticated.
2. Offline demo runs without Feishu credentials.
3. Live demo command examples are documented and use `lark-cli`.
4. The generated solution draft contains all required sections.
5. README explains why this is a Feishu CLI Skill, not just a generic prompt.
6. Tests pass.
7. No private data appears in examples or docs.
8. The repo can be submitted to the competition as a GitHub project.

## 14. Testing Plan

Run local tests:

```bash
python -m pytest
```

Run sample validation:

```bash
python skills/ai-presales/scripts/validate_sample_data.py examples/offline
```

Run offline demo:

```bash
python skills/ai-presales/scripts/collect_context.py --offline examples/offline --out /tmp/presales-context.json
python skills/ai-presales/scripts/render_solution.py --context /tmp/presales-context.json --out /tmp/customer-solution.md
```

Run live smoke checks:

```bash
lark-cli auth status
lark-cli base +record-list --base-token "$PRESALES_BASE_TOKEN" --table-id "$PRESALES_REPORT_TABLE" --limit 1
```

Only run live write commands against a demo folder or demo Base.

## 15. Risks

### Risk: Overbuilding

Mitigation:

- Keep this as a Skill + demo repo.
- Avoid backend services.
- Avoid webhook implementation.

### Risk: Private Data Leakage

Mitigation:

- Use fictional demo data.
- Add privacy scan tests.
- Document strict public-safe rules.

### Risk: Weak Feishu CLI Story

Mitigation:

- Make `lark-cli` visible in README, Skill workflow, and demo script.
- Show both read and write operations.
- Explain auth, Base, Docs, and Wiki integration.

### Risk: Demo Is Too Manual

Mitigation:

- Provide a deterministic offline demo.
- Provide live command examples.
- Include expected output.

## 16. Suggested Claude Code Handoff Prompt

Use this prompt to start implementation in Claude Code:

```text
You are implementing the Feishu CLI AI Presales Skill contest repository.

Read docs/superpowers/specs/2026-05-01-ai-presales-feishu-cli-skill-design.md first.

Build a small open-source repo, not a production backend. Prioritize:
1. A clear AI agent Skill at skills/ai-presales/SKILL.md.
2. Public-safe offline demo data.
3. Thin helper scripts for validation, context collection, and Markdown rendering.
4. README with offline and live Feishu CLI demo instructions.
5. Tests that prove the demo works and catches private-data leaks.

Use lark-cli command examples for live mode. Do not commit real customer data, Feishu tokens, private URLs, or internal case studies. Keep all sample data fictional.

After implementation, run tests and the offline demo, then summarize the result and any remaining live-mode setup steps.
```

## 17. Build Sequence Recommendation

Recommended order:

1. Scaffold folders and placeholder docs.
2. Create sample data.
3. Implement validation script.
4. Implement context collection script.
5. Implement renderer.
6. Write Skill.
7. Write README and contest docs.
8. Add tests.
9. Run offline demo.
10. Review for private data.

The repo should be ready for a first public GitHub submission after this sequence.
