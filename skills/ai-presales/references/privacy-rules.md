# Privacy Rules

This repository is open-source and intended for public review by the Feishu CLI Creator Competition. It must contain **no internal business material**.

## Hard rules

1. **No real customer names.** Use fictional names such as `Beanlight Tea (Fictional Demo Co.)` or `Demo Coffee Chain` in any committed example.
2. **No internal customer cases.** All entries in `examples/offline/case-library.json` must have `public_safe: true` and must be fictionalized.
3. **No private Feishu URLs.** Do not commit Wiki, Bitable, Docx, or Drive links unless they are demo-only and publicly shareable.
4. **No tokens, cookies, app secrets, or auth files.** This includes `cli_a*`, `t-*`, `app_secret`, `app_id`, `bot_token`, `cookie`, OAuth refresh tokens, and any export of `~/.lark-cli/`.
5. **No internal product strategy.** Capability descriptions in examples must be generic enough to publish.
6. **Live-mode output goes to demo folders only.** Do not write generated drafts into a real customer-facing Feishu folder without the user's explicit approval each time.
7. **Demo-data callouts.** Any output produced in offline mode must label itself as "fictional demo data".

## Forbidden tokens (privacy-scan denylist)

The privacy scan in `tests/test_privacy_scan.py` rejects any commit that introduces:

- `真实客户` (literal "real customer" placeholder marker — never let this leak)
- `cli_a` followed by alphanumerics (Feishu app token prefix)
- `t-` followed by alphanumerics longer than 12 chars (Feishu user/tenant token shape)
- `app_secret`, `app_id`, `bot_token`, `refresh_token`, `access_token` followed by `=` or `:`
- `secret=`, `token=` (generic credential keys)
- Hostnames `feishu.cn/wiki/`, `feishu.cn/base/`, `feishu.cn/docs/` (private Feishu URLs)

The scan ignores `docs/superpowers/specs/` because the design doc legitimately discusses these patterns by name.

## What to do if you spot a leak

1. **Stop committing.** Do not amend the leak away — assume the token is now compromised.
2. Fictionalize the value in the file.
3. If a real token leaked, rotate it through `lark-cli auth login` (or the Feishu admin console for app credentials) before pushing the cleanup commit.
4. Re-run `python -m pytest tests/test_privacy_scan.py` to confirm.

## Why this matters

The contest requires open-source code. Open source means the entire git history is public. A leak cannot be cleaned up by deleting the file in a later commit — git history will still expose it. The scan is the gatekeeper; do not bypass.
