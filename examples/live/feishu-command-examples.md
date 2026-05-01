# Live Feishu CLI Command Examples

These commands assume you have authenticated `lark-cli` and exported the variables in `env.example`.

## 1. Sanity check auth

```bash
lark-cli auth status
```

Expected output: `tokenStatus: valid` and a non-empty `userOpenId`.

## 2. List tables in the presales Bitable

```bash
lark-cli base +table-list \
  --base-token "$PRESALES_BASE_TOKEN" \
  --format json
```

Use the returned `table_id` values to populate `PRESALES_REPORT_TABLE`, etc., in your env file.

## 3. Read sales reports

```bash
lark-cli base +record-list \
  --base-token "$PRESALES_BASE_TOKEN" \
  --table-id "$PRESALES_REPORT_TABLE" \
  --limit 20 \
  --format json
```

## 4. Read a Wiki/Docx decision guide

```bash
lark-cli docs +fetch \
  --doc "$PRESALES_DECISION_GUIDE_DOC"
```

## 5. Run the live workflow end-to-end

```bash
python skills/ai-presales/scripts/collect_context.py --live --out /tmp/presales-context.json
python skills/ai-presales/scripts/render_solution.py --context /tmp/presales-context.json --out /tmp/customer-solution.md

# Inspect /tmp/customer-solution.md, then:

lark-cli docs +create \
  --folder-token "$PRESALES_OUTPUT_FOLDER_TOKEN" \
  --title "Customer Solution Draft (demo)" \
  --markdown @/tmp/customer-solution.md
```

## 6. Update project status

```bash
lark-cli base +record-upsert \
  --base-token "$PRESALES_BASE_TOKEN" \
  --table-id "$PRESALES_STATUS_TABLE" \
  --json '{"project_id":"demo-2026-001","status":"draft_generated","confidence":"high"}'
```

## 7. When in doubt about flags

```bash
lark-cli base +record-list --help
lark-cli docs +create --help
lark-cli schema base.app-table-record.list --format pretty
```
