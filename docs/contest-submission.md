# Contest Submission

## Title

`ai-presales-via-feishu-cli` — turn a Feishu sales report into a customer solution draft in 30 minutes, end-to-end via `lark-cli`.

## Track

Feishu CLI Creator Competition — GitHub track.

## Award positioning

Primary target: **Best Practice Award** (skill + business workflow + measurable business efficiency).

Secondary target: **Honor Award** through a polished open-source skill.

The entry is intentionally not optimized for the Highest Stars Award — it targets the practical-business-value lane.

## Repo URL

https://github.com/jasonshao/ai-presales-via-feishu-cli _(currently private — flip to public before the contest deadline)_

## One-line summary

A Claude Code skill plus three thin Python scripts that turn a sales report stored in Feishu Bitable into a customer-facing solution draft, using `lark-cli` for every Feishu read and write. Includes a fully offline demo so any judge can run it without Feishu credentials.

## Why this fits the Best Practice Award

1. **Tied to a real business workflow.** AI presales is a measurable bottleneck for B2B sales orgs: the time from sales report to first customer solution draft. This skill targets that 30-minute window.
2. **Real Feishu CLI integration, not a wrapper.** Every Feishu read and write goes through `lark-cli`: auth, Bitable list, Docs create, record upsert. The skill explicitly tells the agent to use `lark-cli --help` and `lark-cli schema` instead of guessing flags.
3. **Reproducible by judges.** The offline demo runs without any Feishu credentials and ships a golden expected-output file. Live mode is a single env-file change away.
4. **Privacy-first.** A repo-wide privacy scan is part of the test suite. No real customer data, no internal cases, no Feishu tokens, no private URLs.
5. **Extensible.** Adding a new presales scenario means adding one record to a JSON file (or a Feishu Bitable row). No script changes required.

## What the agent does end-to-end

1. Reads sales report and supporting knowledge from Feishu Bitable via `lark-cli base +record-list`.
2. Picks the candidate scenario with deterministic keyword matching, then refines with real reasoning.
3. Diagnoses missing facts and emits a follow-up checklist for the sales owner.
4. Drafts a four-section customer solution in Markdown.
5. Writes the draft to Feishu Docs via `lark-cli docs +create` (demo folder by default).
6. Updates project status via `lark-cli base +record-upsert`.

## Demo

- 2-3 minute narration in [`demo-script.md`](demo-script.md).
- Offline workflow runs in three commands and produces a deterministic Markdown artifact identical to [`examples/offline/expected-output.md`](../examples/offline/expected-output.md).

## Tests in CI

- `python -m pytest -q` runs 13 tests, including:
  - Schema validation of bundled demo data.
  - Scenario matcher correctness for the demo report.
  - Renderer header completeness + golden-file comparison.
  - Repo-wide privacy scan for token leaks and private Feishu URLs.

## Screenshots / GIFs

_(to be added before submission — placeholders intentional)_

- Recognition card preview
- Follow-up checklist preview
- Solution draft preview (header section)
- `lark-cli auth status` output
- Generated Feishu Docs document (live mode, against demo folder)

## Submission checklist

- [ ] Repo is public on GitHub
- [ ] README opens with a `lark-cli` command in the first screen
- [ ] `python -m pytest -q` passes
- [ ] Privacy scan green
- [ ] Demo script recorded
- [ ] Submission filed at the contest page before the deadline (2026-05-05 23:59)
