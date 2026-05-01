# Architecture

The full design is in [`docs/superpowers/specs/2026-05-01-ai-presales-feishu-cli-skill-design.md`](superpowers/specs/2026-05-01-ai-presales-feishu-cli-skill-design.md). This file is a fast orientation for new contributors.

## One-line summary

A portable agent skill (`SKILL.md`) plus three thin Python scripts that turn a Feishu Bitable sales report into a customer-facing solution draft, using `lark-cli` for every Feishu read and write. The skill format is the Claude Code convention but the body is agent-neutral — Codex, OpenClaw, Cursor, custom Agent SDKs, etc. can all load and drive it.

## Component diagram

```
┌──────────────────────────┐
│  Sales report in         │
│  Feishu Bitable          │
└────────────┬─────────────┘
             │  lark-cli base +record-list
             ▼
┌──────────────────────────┐      ┌──────────────────────────┐
│  collect_context.py      │ ◄─── │  examples/offline/*.json │
│  (offline | live)        │      │  (demo fallback)         │
└────────────┬─────────────┘      └──────────────────────────┘
             │  context.json
             ▼
┌──────────────────────────┐
│  render_solution.py      │
│  → Markdown              │
│  - recognition card      │
│  - follow-up checklist   │
│  - solution draft        │
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

Any agent that loads `SKILL.md` (Claude Code, Codex, OpenClaw, Cursor, a custom Agent SDK, …) is the conductor:

1. Decides which mode to run (offline vs. live).
2. Runs the three scripts.
3. Reads the rendered Markdown.
4. Applies real reasoning on top of the deterministic baseline (the matcher only scores keyword overlap; a real agent should refine the verdict, fill in details, and rewrite generic phrasing).
5. Writes the polished draft to Feishu Docs and updates project status — only against demo folders unless the user explicitly approves a customer-facing target.

## Why split scripts from skill

- **Scripts are deterministic.** They produce the same output for the same input, every time. This makes tests and CI possible.
- **The skill owns the reasoning.** Scenario nuance, case selection beyond keyword tags, customer-facing language — all of that requires the agent. Pushing it into scripts would just hide it behind brittle templates.
- **Easy to extend.** New scenario? Add a row to the JSON (or Bitable). New capability? Same. The renderer does not need to change.

## Why `lark-cli` and not raw HTTP

- Auth is shared with whatever the user already uses for Feishu — no separate OAuth flow.
- The CLI surface stays stable as the underlying Feishu APIs evolve.
- `lark-cli --help` and `lark-cli schema` give the agent a way to discover correct flags at runtime.
- It is the contest's primary track.

## Data flow boundaries

- `collect_context.py` is the only place that talks to Feishu (live mode). Everything downstream operates on the merged context JSON.
- `render_solution.py` is pure: context JSON in, Markdown out. No I/O to Feishu, no network calls.
- `validate_sample_data.py` is offline-only. It is the gatekeeper for new contributors adding sample data.

## Tests

- `test_validate_sample_data.py` — schema enforcement.
- `test_collect_context.py` — scenario matcher correctness on the bundled demo.
- `test_render_solution.py` — required headers + golden-file comparison against `examples/offline/expected-output.md`.
- `test_privacy_scan.py` — repo-wide regex scan for token leaks, real-customer markers, private Feishu URLs.

## Out of scope (intentionally)

- No FastAPI service / webhook listener.
- No bot card UI.
- No vector DB / RAG.
- No auto-deploy.
- No real customer cases.

These belong in the production internal MVP, not in the open-source contest entry.
