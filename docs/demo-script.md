# 2-3 Minute Demo Script

Use this as the narration for a screen capture or a live walk-through. Total target: ~2 minutes 30 seconds.

## 0:00 — Set the stage (15 s)

> "This is `ai-presales-via-feishu-cli` — a Feishu CLI Skill that turns a sales report into a customer-facing solution draft. The whole thing runs through `lark-cli`. I'll show you the offline demo first, then the live Feishu mode."

Show the [`README.md`](../README.md) header on screen.

## 0:15 — Show the skill (20 s)

Open [`skills/ai-presales/SKILL.md`](../skills/ai-presales/SKILL.md). Scroll to the "When to invoke" and "Live workflow" sections.

> "The skill tells the agent when to wake up — sales report, recognition card, customer solution draft — and exactly which `lark-cli` commands to use. Auth check, Bitable read, Docs write, status upsert."

## 0:35 — Run the offline demo (40 s)

Run in a terminal:

```bash
python skills/ai-presales/scripts/validate_sample_data.py examples/offline
python skills/ai-presales/scripts/collect_context.py --offline examples/offline --out /tmp/c.json
python skills/ai-presales/scripts/render_solution.py --context /tmp/c.json --out /tmp/sol.md
cat /tmp/sol.md | head -40
```

> "Validation passes. The collector picks `PAY_API_MINIPROGRAM` with high confidence — six matched keywords. The renderer emits three artifacts: project recognition card, follow-up checklist with the missing items, and a four-section customer-facing draft."

Highlight the `Demo data — fictional customer` callout.

> "Note the demo callout — required by the privacy rules. Demo data is fictional. No real customer ever appears in this repo."

## 1:15 — Show the live mode contract (30 s)

Open [`examples/live/feishu-command-examples.md`](../examples/live/feishu-command-examples.md).

> "Live mode uses the same scripts. The only thing that changes is `--live` instead of `--offline`. Behind the scenes that runs `lark-cli base +record-list` against the demo Bitable. The output goes back into Feishu Docs via `lark-cli docs +create`, and project status updates with `lark-cli base +record-upsert`."

Show `lark-cli auth status` output.

## 1:45 — Tests + privacy scan (25 s)

```bash
python -m pytest -q
```

> "Thirteen tests, all green. The last one is a privacy scan — it greps the entire repo for Feishu token shapes, real-customer markers, and private Feishu URLs. If any contributor leaks a real token in a PR, this turns red in CI."

## 2:10 — Wrap (20 s)

> "That's the entry. One skill, three thin scripts, fictional demo data, live Feishu mode through `lark-cli`, privacy scan in CI. The repo is MIT-licensed. Source of truth for the design lives in `docs/superpowers/specs/`."

Show the GitHub repo URL on screen.

## Recording tips

- Use a 1280×720 capture window.
- Pre-warm the venv so commands return instantly.
- Pre-cd to the repo root.
- Pre-export the live-mode env vars but do not actually run any live writes during the demo (or use a throwaway demo folder).
