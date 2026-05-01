# AI Presales via Feishu CLI

> 🌏 Languages: [中文](README.md) · **English**
>
> Turn a Feishu sales report into a customer-facing solution draft in under 30 minutes — using `lark-cli` for every Feishu read and write, driven by a **portable agent skill document** (`SKILL.md`) that any modern agent can load.

This repository is an entry for the [Feishu CLI Creator Competition](https://www.feishu.cn/community/article/event?id=7629204812755635148) (GitHub track, "Best Practice Award" target). It packages a real internal AI-presales workflow as an open-source, runnable skill that **any agent that can read files and run shell commands** can pick up — Claude Code, Codex, OpenClaw, Cursor, your own Agent SDK, you name it.

---

## Table of Contents

- [Why this exists](#why-this-exists)
- [What the skill does](#what-the-skill-does)
- [Which agents can run this](#which-agents-can-run-this)
- [A complete demo walk-through](#a-complete-demo-walk-through)
- [30-second offline demo](#30-second-offline-demo)
- [Live Feishu demo](#live-feishu-demo)
- [Architecture and design principles](#architecture-and-design-principles)
- [Feishu CLI integration points](#feishu-cli-integration-points)
- [Extensibility: adding a new scenario](#extensibility-adding-a-new-scenario)
- [Tests and privacy scan](#tests-and-privacy-scan)
- [Repository layout](#repository-layout)
- [Reproduction guide for judges](#reproduction-guide-for-judges)
- [Design source of truth](#design-source-of-truth)
- [Contributing / License](#contributing)

---

## Why this exists

B2B presales has one high-frequency, time-eating bottleneck: **a sales report comes in → presales must produce a customer-facing solution draft within 30 minutes to 2 hours**.

Common pain points in practice:

1. **Scenario recognition is folklore.** Two presales engineers reading the same report often classify it into completely different scenarios.
2. **Reports are incomplete.** Sales typically misses key facts (subject consistency, peak TPS, reconciliation format, etc.) and presales has to ping-pong 3–5 times before drafting.
3. **Templates live everywhere.** Customer background, recommended solution, similar cases, open questions — scattered across a dozen Wikis and docs, manually stitched every time.
4. **Case library is dead weight.** Successful past projects are buried in chat screenshots and emails. New presales engineers can't actually find them.

The result: **presales becomes one of the most expensive bottlenecks on the line**. A junior presales person produces 3–5 drafts a day on a good day, and quality varies wildly.

What this skill is trying to do is concrete: **turn presales from "experience-driven manual work" into "skill-driven collaboration"**.

- The moment a sales report lands in a Feishu Bitable → an agent recognizes the scenario, surfaces the gaps, hands sales a follow-up checklist, and drafts the customer solution.
- Presales' role shifts from "writing the first draft" to "reviewing and setting the tone." Target time per draft: ≤ 30 minutes.
- Knowledge stays in Feishu Bitables — scenario packages, capabilities, cases. Adding a new scenario only requires a few rows of data, no code change.

## What the skill does

[`skills/ai-presales/SKILL.md`](skills/ai-presales/SKILL.md) is the heart of the repo. It directs the agent through the full presales loop:

```
Sales report lands in Feishu Bitable
        │
        ▼
[1] Read the report + scenario packages, capabilities, cases
        │     (lark-cli base +record-list)
        ▼
[2] Scenario recognition (keyword match → confidence + matched keywords)
        │
        ▼
[3] Gap diagnosis (5–8 follow-up checklist items for sales)
        │
        ▼
[4] Drafting (Markdown: background / recommendation / cases / open questions)
        │
        ▼
[5] Write back to Feishu Docs + update project status
              (lark-cli docs +create / base +record-upsert)
```

Two run modes:

- **Offline** — no Feishu credentials needed. Operates on the bundled fictional demo data under `examples/offline/`. Perfect for CI, demos, and judges.
- **Live** — point at a Feishu Bitable via env vars in `examples/live/env.example`.

## Which agents can run this

[`SKILL.md`](skills/ai-presales/SKILL.md) is a **static, portable agent instruction document**. The format (YAML frontmatter + Markdown body) is a Claude Code convention, **but the body itself is agent-neutral** — any agent platform that can "read files + run shell" can drive this workflow directly.

| Agent platform | How to wire it in | Notes |
|---|---|---|
| **Claude Code** | Symlink `skills/ai-presales/` into `~/.claude/skills/`, or use it directly inside the repo | Native format; auto-loads when the description matches |
| **Codex** (Anthropic) | Clone the repo and prompt Codex e.g. "follow `skills/ai-presales/SKILL.md` to handle customer X's report" | Codex reads SKILL.md and executes the steps |
| **OpenClaw** | Load SKILL.md as a system instruction, or treat it as a workflow doc / plugin | Same shape as Codex |
| **Cursor / Continue** | Drop SKILL.md content into `.cursorrules` or a prompt template | Reasoning happens in the IDE agent; shell commands run in your terminal |
| **Custom Agent SDK** | Use SKILL.md as the system prompt and give the agent a `bash` tool | Most general path — a few lines of code |
| **Any capable LLM agent** | Same | Recommended capability ≥ Claude Sonnet 4.5 / GPT-4 class |

The only hard dependencies are:

1. The agent can read this repo's files.
2. The agent can call `lark-cli` (or fall back to offline mode and read local JSON).

**Why we don't pin to a single agent platform**: presales is a real-world workflow, and different teams use different agent stacks. The value of this skill is in the "Feishu + presales business flow" packaging — not in coupling to a specific agent vendor. The committed `examples/offline/expected-output.md` is a deterministic golden file, so **whatever agent runs this should produce a final draft close to that baseline**, with differences only in language polishing.

## A complete demo walk-through

The repo bundles a fictional case — tea-chain brand "Beanlight Tea" wanting to launch a payment-enabled mini-program.

**Input**: [`examples/offline/sales-report.json`](examples/offline/sales-report.json) (excerpt)

```text
Customer: Beanlight Tea (Fictional Demo Co.)
Industry: Food & Beverage / Specialty tea chain
Report summary: ~120 mall-counter stores, want a branded WeChat
                mini-program with payment for pre-order pickup and
                loyalty. Existing POS but no online ordering.
                Target launch in 6-8 weeks.
Current system: self-built POS. No e-commerce. Finance reconciles
                daily via Excel exports.
Transaction scale: ~60,000 orders/day at peak, ~28 RMB ticket.
Expected solution: WeChat mini-program with payment under their own
                   merchant account, daily reconciliation files in
                   their finance team's format.
Deadline: Soft target 2026-07-15 launch.
```

**Output the skill produces** (full version in [`examples/offline/expected-output.md`](examples/offline/expected-output.md), excerpt below):

```markdown
# Project Recognition Card

- Customer: Beanlight Tea (Fictional Demo Co.)
- Candidate scenario: Mini-program payment via API integration (PAY_API_MINIPROGRAM)
- Confidence: high (score: 6)
- Matched keywords: mini-program, WeChat mini-program, in-app payment,
                    API integration, pre-order, branded mini-program
- Completeness: 86% of 7 checklist items
- Deadline: Soft target: 2026-07-15 launch.

---

# Follow-Up Checklist
_6 answered, 1 missing of 7 required items._

## Missing — ask sales before drafting
- Are refunds, partial refunds, and after-sales tickets in scope for v1?

---

# Beanlight Tea x [Your Company] Solution Draft

> Demo data — fictional customer. Reviewed by a human before sending.

## 1. Customer Background And Needs
   ...
## 2. Recommended Solution
   - Mini-program payment SDK + API: keep full UI control while we
     handle order creation, payment invocation, async callback, recon.
       - Constraint: Subject consistency mandatory.
   - Daily reconciliation and finance export: T+1 SFTP push.
       - Constraint: format must be agreed in discovery.
## 3. Similar Cases
   - CASE-DEMO-A1 (Tea chain, ~80 stores, recon SFTP, launched in 7 weeks)
   - CASE-DEMO-B2 (Coffee chain, ~200 stores, member identity reuse)
## 4. Assumptions And Open Questions
   - Are refunds, partial refunds, and after-sales tickets in scope for v1?
   - Subject-consistency reminder: signing entity = WeChat Pay merchant
```

Three things left for the human:

1. Write the sales report into the Bitable (which sales already does).
2. Skim the agent's follow-up checklist, ping sales for the missing items.
3. Skim the agent's draft, polish wording, send to the customer.

## 30-second offline demo

```bash
python skills/ai-presales/scripts/validate_sample_data.py examples/offline
python skills/ai-presales/scripts/collect_context.py --offline examples/offline --out /tmp/presales-context.json
python skills/ai-presales/scripts/render_solution.py --context /tmp/presales-context.json --out /tmp/customer-solution.md
```

The third command produces a file byte-for-byte identical to [`examples/offline/expected-output.md`](examples/offline/expected-output.md) — recognition card + follow-up checklist + customer solution draft.

> No Feishu account required. No `lark-cli` required. No tokens required. Open the repo and run.

## Live Feishu demo

```bash
# 1. Make sure lark-cli is authenticated
lark-cli auth status   # tokenStatus: valid

# 2. Configure the demo Bitable
cp examples/live/env.example ~/.presales.env
# Fill the 6 PRESALES_* values, then:
set -a; source ~/.presales.env; set +a

# 3. Run the same workflow against Feishu
python skills/ai-presales/scripts/collect_context.py --live --out /tmp/presales-context.json
python skills/ai-presales/scripts/render_solution.py --context /tmp/presales-context.json --out /tmp/customer-solution.md

# 4. Save the draft to a DEMO Feishu Drive folder
lark-cli docs +create \
  --folder-token "$PRESALES_OUTPUT_FOLDER_TOKEN" \
  --title "Customer Solution Draft (demo)" \
  --markdown @/tmp/customer-solution.md

# 5. Update project status
lark-cli base +record-upsert \
  --base-token "$PRESALES_BASE_TOKEN" \
  --table-id "$PRESALES_STATUS_TABLE" \
  --json '{"project_id":"demo-2026-001","status":"draft_generated","confidence":"high"}'
```

Full live runbook in [`examples/live/feishu-command-examples.md`](examples/live/feishu-command-examples.md).

## Architecture and design principles

```
┌──────────────────────────┐
│  Sales report in         │
│  Feishu Bitable          │
└────────────┬─────────────┘
             │  lark-cli base +record-list
             ▼
┌──────────────────────────┐      ┌──────────────────────────┐
│  collect_context.py      │ ◄─── │  examples/offline/*.json │
│  (offline | live)        │      │  (offline fallback)      │
└────────────┬─────────────┘      └──────────────────────────┘
             │  context.json (deterministic structured context)
             ▼
┌──────────────────────────┐
│  render_solution.py      │  ← Skill puts agent reasoning on top
│  → Markdown              │     - Project recognition card
│                          │     - Follow-up checklist
│                          │     - Customer solution draft
└────────────┬─────────────┘
             │  lark-cli docs +create
             │  lark-cli base +record-upsert
             ▼
┌──────────────────────────┐
│  Customer solution doc   │
│  + project status update │
│  in Feishu               │
└──────────────────────────┘
```

**Core design principle: scripts are deterministic, the skill owns reasoning.**

- **Scripts are deterministic.** Same input → same output, every time. Makes testing, CI, and diff-based validation possible.
- **The skill owns the reasoning.** Subtle scenario calls, case selection beyond keyword tags, customer-facing language — all of that requires the agent. Pushing it into scripts just hides it behind brittle templates.
- **Adding scenarios doesn't change code.** New scenario? Add a row to the JSON (or a Bitable). The renderer doesn't change.

**Why `lark-cli`, not raw SDK calls**

- Auth is shared with whatever the user already uses for Feishu — no separate OAuth flow.
- The CLI surface stays stable as the underlying APIs evolve.
- The agent can `lark-cli --help` / `lark-cli schema` to discover unknown command shapes at runtime, instead of guessing.
- It's the contest's primary track.

## Feishu CLI integration points

| Feishu CLI integration point | Where in this repo |
|---|---|
| Auth check (`lark-cli auth status`) | [`SKILL.md`](skills/ai-presales/SKILL.md), live workflow step 1 |
| Bitable read (`lark-cli base +record-list`) | [`collect_context.py`](skills/ai-presales/scripts/collect_context.py) (`load_live`) |
| Bitable list-tables (`lark-cli base +table-list`) | [`feishu-command-examples.md`](examples/live/feishu-command-examples.md) §2 |
| Bitable write (`lark-cli base +record-upsert`) | Live runbook step 5 |
| Docs creation (`lark-cli docs +create`) | Live runbook step 4 |
| Wiki/Docx fetch (`lark-cli docs +fetch`) | Optional decision-guide read in `SKILL.md` |
| Schema discovery (`lark-cli schema …`) | Troubleshooting in `SKILL.md` |

The skill explicitly tells the agent to prefer `lark-cli --help` / `lark-cli schema` over guessing flags, so the workflow stays robust as the CLI evolves.

## Extensibility: adding a new scenario

Suppose you want to add a "store POS upgrade assessment" scenario. Three steps:

1. Add a record to [`examples/offline/scenario-packages.json`](examples/offline/scenario-packages.json) (schema: [`scenario-package-schema.md`](skills/ai-presales/references/scenario-package-schema.md)):
   ```json
   {
     "scenario_id": "POS_UPGRADE_ASSESS",
     "scenario_name": "Store POS upgrade assessment",
     "trigger_keywords": ["POS upgrade", "替换收银", "store upgrade", "..."],
     "entry_conditions": ["..."],
     "confirmation_checklist": ["...", "..."],
     "decision_rules": ["if X then Y"],
     "supported_outputs": ["recognition card", "follow-up checklist"],
     "fallback_message": "..."
   }
   ```
2. In [`product-capabilities.json`](examples/offline/product-capabilities.json), add `"POS_UPGRADE_ASSESS"` to the `applicable_scenarios` list of any capability that fits.
3. Add a fictional case in [`case-library.json`](examples/offline/case-library.json) with `"POS_UPGRADE_ASSESS"` in `scenario_tags` and `public_safe: true`.

`pytest` covers your new scenario automatically. **No Python changes. No skill changes. No renderer changes.**

In live mode, just add a row to the Bitable.

## Tests and privacy scan

```bash
python -m pytest -q
```

13 tests cover:

- ✅ Sample data passes schema validation.
- ✅ The context collector returns the expected `PAY_API_MINIPROGRAM` high-confidence match for the demo report.
- ✅ The renderer emits all required §10.3 sections.
- ✅ Renderer output matches the bundled [`expected-output.md`](examples/offline/expected-output.md) **byte-for-byte** (golden-file diff).
- ✅ The privacy scan catches forbidden tokens, populated secrets, and private Feishu URLs anywhere in the repo (denylist in [`privacy-rules.md`](skills/ai-presales/references/privacy-rules.md)).

**The privacy scan matters most.** Once a real token or real customer name lands in a commit on an open-source project, you can't get it out of git history. So the scan is the gate-keeper in CI — strict on purpose.

## Repository layout

```text
ai-presales-via-feishu-cli/
  README.md                            # Chinese (primary)
  README.en.md                         # English (this file)
  LICENSE                              # MIT
  pyproject.toml                       # Python 3.10+, only dep: pytest
  skills/ai-presales/
    SKILL.md                           # ⭐ The skill — heart of the entry
    references/
      solution-template.md             # Customer solution Markdown template
      scenario-package-schema.md       # Scenario package field spec
      base-schema.md                   # Feishu Bitable field mappings
      privacy-rules.md                 # Public-safe data policy
    scripts/
      validate_sample_data.py          # Schema validator
      collect_context.py               # Context collection (offline + live)
      render_solution.py               # Deterministic Markdown renderer
  examples/
    offline/                           # Public-safe fictional demo data
      sales-report.json                #   Sales report (Beanlight Tea)
      scenario-packages.json           #   2 scenario packages
      product-capabilities.json        #   3 capabilities
      case-library.json                #   3 fictional cases
      expected-output.md               #   Golden file (renderer output)
    live/                              # Live-mode env + runbook
      env.example
      feishu-command-examples.md
  docs/
    architecture.md                    # Architecture summary
    demo-script.md                     # 2-3 minute demo narration
    contest-submission.md              # Contest summary
    superpowers/specs/                 # Full design doc (~600 lines)
  tests/                               # pytest, including privacy scan
```

## Reproduction guide for judges

If you're a contest judge, here's the shortest path to fully validate this project in 5 minutes:

```bash
# 1. clone
git clone https://github.com/jasonshao/ai-presales-via-feishu-cli
cd ai-presales-via-feishu-cli

# 2. install dep (just pytest)
python -m pip install --user pytest

# 3. run tests — 13 pass in ~0.5s
python -m pytest -q

# 4. run the offline demo
python skills/ai-presales/scripts/collect_context.py --offline examples/offline --out /tmp/c.json
python skills/ai-presales/scripts/render_solution.py --context /tmp/c.json --out /tmp/s.md

# 5. confirm output matches the golden file (should be identical)
diff /tmp/s.md examples/offline/expected-output.md && echo "GOLDEN MATCH"

# 6. (optional) sanity-check Feishu CLI integration density
grep -rE "lark-cli" skills/ examples/ README.md | wc -l   # 30+ hits
```

Suggested reading order:

1. [`skills/ai-presales/SKILL.md`](skills/ai-presales/SKILL.md) — the skill itself, ~10 minute read
2. [`docs/architecture.md`](docs/architecture.md) — architecture summary
3. [`examples/offline/expected-output.md`](examples/offline/expected-output.md) — what the skill actually produces
4. [`docs/superpowers/specs/2026-05-01-ai-presales-feishu-cli-skill-design.md`](docs/superpowers/specs/2026-05-01-ai-presales-feishu-cli-skill-design.md) — full design doc (deep read)

## Design source of truth

The full design document lives at [`docs/superpowers/specs/2026-05-01-ai-presales-feishu-cli-skill-design.md`](docs/superpowers/specs/2026-05-01-ai-presales-feishu-cli-skill-design.md). It explains the Skill / Auth / Knowledge / Workflow / Collaboration / Output / Measurement layers in depth and is the canonical reference if you want to extend or fork this skill.

## Contributing

Issues and PRs welcome — especially:

- New scenario packages (mind [`scenario-package-schema.md`](skills/ai-presales/references/scenario-package-schema.md))
- New `lark-cli` integration points the skill should know about
- Better deterministic scenario matching (the current matcher is intentionally simple)
- More end-to-end live-mode demo videos

By contributing you agree your contributions are MIT-licensed and contain no internal customer data.

## License

MIT. See [`LICENSE`](LICENSE).
