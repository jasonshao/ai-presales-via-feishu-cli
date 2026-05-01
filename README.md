# AI Presales via Feishu CLI

> Turn a Feishu sales report into a customer-facing solution draft in under 30 minutes — using `lark-cli` for every Feishu read and write, and a Claude Code skill (`SKILL.md`) for the reasoning.

This repository is an entry for the [Feishu CLI Creator Competition](https://www.feishu.cn/community/article/event?id=7629204812755635148) (GitHub track, "Best Practice Award" target). It packages a real internal AI-presales workflow as an open-source, runnable skill that any agent with `lark-cli` can pick up.

---

## What you get

A single skill, [`skills/ai-presales/SKILL.md`](skills/ai-presales/SKILL.md), that knows how to:

1. **Read** a sales report (and the supporting scenario / capability / case knowledge) from a Feishu Bitable, via `lark-cli base +record-list`.
2. **Recognize** which presales scenario the opportunity belongs to, with a confidence score and a list of matched keywords.
3. **Diagnose** what's missing: a 5–8 question follow-up checklist for the sales owner.
4. **Draft** a customer-facing solution in Markdown — background, recommended solution, similar cases, open questions.
5. **Write** the draft back to Feishu Docs via `lark-cli docs +create`, and update project status with `lark-cli base +record-upsert`.

Two run modes:

- **Offline** — no Feishu credentials needed. Works on the bundled demo data under `examples/offline/`. Perfect for CI, demos, and judges.
- **Live** — point at a Feishu Bitable via env vars in `examples/live/env.example`.

## Quick start

### 30-second offline demo

```bash
python skills/ai-presales/scripts/validate_sample_data.py examples/offline
python skills/ai-presales/scripts/collect_context.py --offline examples/offline --out /tmp/presales-context.json
python skills/ai-presales/scripts/render_solution.py --context /tmp/presales-context.json --out /tmp/customer-solution.md
```

The third command writes [the same recognition card + checklist + solution draft you can preview here](examples/offline/expected-output.md).

### Live Feishu demo

```bash
# 1. Make sure lark-cli is authenticated
lark-cli auth status   # tokenStatus: valid

# 2. Configure the demo Bitable
cp examples/live/env.example ~/.presales.env
# fill in the 6 PRESALES_* values, then:
set -a; source ~/.presales.env; set +a

# 3. Run the same workflow against Feishu
python skills/ai-presales/scripts/collect_context.py --live --out /tmp/presales-context.json
python skills/ai-presales/scripts/render_solution.py --context /tmp/presales-context.json --out /tmp/customer-solution.md

# 4. Save the draft to a DEMO Feishu Drive folder
lark-cli docs +create \
  --folder-token "$PRESALES_OUTPUT_FOLDER_TOKEN" \
  --title "Customer Solution Draft (demo)" \
  --markdown @/tmp/customer-solution.md
```

See [`examples/live/feishu-command-examples.md`](examples/live/feishu-command-examples.md) for the full live runbook.

## Why this is a Feishu CLI skill, not a generic prompt

| Feishu CLI integration point | Where in this repo |
|---|---|
| Auth check (`lark-cli auth status`) | [`SKILL.md`](skills/ai-presales/SKILL.md), live workflow step 1 |
| Bitable reads (`lark-cli base +record-list`) | [`collect_context.py`](skills/ai-presales/scripts/collect_context.py) (`load_live`) |
| Bitable writes (`lark-cli base +record-upsert`) | Live runbook step 6 |
| Docs creation (`lark-cli docs +create`) | Live runbook step 5 |
| Wiki/Docx fetch (`lark-cli docs +fetch`) | Optional decision-guide read in `SKILL.md` |
| Schema discovery (`lark-cli schema …`) | Troubleshooting in `SKILL.md` |

The skill explicitly tells the agent to prefer `lark-cli --help` and `lark-cli schema` over guessing flags, so the workflow stays robust as the CLI evolves.

## Repository layout

```text
ai-presales-via-feishu-cli/
  README.md
  LICENSE
  pyproject.toml
  skills/ai-presales/
    SKILL.md                          # the skill — heart of the entry
    references/
      solution-template.md
      scenario-package-schema.md
      base-schema.md
      privacy-rules.md
    scripts/
      validate_sample_data.py
      collect_context.py
      render_solution.py
  examples/
    offline/                          # public-safe demo data
    live/                             # env template + lark-cli runbook
  docs/
    architecture.md
    demo-script.md
    contest-submission.md
    superpowers/specs/                # full design doc
  tests/                              # pytest, including a privacy scan
```

## Demo data is fictional

All `examples/` data is fictional. The demo customer "Beanlight Tea" does not exist. No real customer names, no internal cases, no Feishu tokens, no private URLs are committed — see [`skills/ai-presales/references/privacy-rules.md`](skills/ai-presales/references/privacy-rules.md). A privacy scan in [`tests/test_privacy_scan.py`](tests/test_privacy_scan.py) enforces this on every test run.

## Running the tests

```bash
python -m pytest -q
```

Tests cover:

- Sample data passes schema validation.
- Context collection produces the expected scenario match for the bundled demo.
- The renderer emits all required §10.3 sections.
- The privacy scan catches forbidden tokens, populated secrets, and private Feishu URLs anywhere in the repo (denylist in [`skills/ai-presales/references/privacy-rules.md`](skills/ai-presales/references/privacy-rules.md)).

## Design source of truth

The full design document lives at [`docs/superpowers/specs/2026-05-01-ai-presales-feishu-cli-skill-design.md`](docs/superpowers/specs/2026-05-01-ai-presales-feishu-cli-skill-design.md). It explains the Skill / Auth / Knowledge / Workflow / Collaboration / Output / Measurement layers in depth and is the canonical reference if you want to extend or fork this skill.

## Contributing

Issues and PRs welcome — especially:

- Additional scenario packages (mind `references/scenario-package-schema.md`).
- New `lark-cli` integration points the skill should know about.
- Better deterministic scenario matching (the current matcher is intentionally simple).

By contributing you agree your contributions are MIT-licensed and contain no internal customer data.

## License

MIT. See [`LICENSE`](LICENSE).
