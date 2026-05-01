"""Privacy scan: catch leaks of forbidden tokens, real customer markers,
and private Feishu URLs anywhere in the repo (with a small exclude list).
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Files that are allowed to mention forbidden patterns *by name* — they are the
# rule-definition or test-definition files themselves, plus the canonical
# design doc.
ALLOWED_PATHS = {
    "skills/ai-presales/references/privacy-rules.md",
    "tests/test_privacy_scan.py",
    "docs/superpowers/specs/2026-05-01-ai-presales-feishu-cli-skill-design.md",
}

# Top-level directories to skip entirely.
SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", "node_modules", "build", "dist"}

# Forbidden patterns. Each entry is (label, compiled_regex).
# The regex must be tight enough that it does not flag placeholder tokens like
# "$PRESALES_BASE_TOKEN" or "<token>" or env-var references.
PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("real-customer marker", re.compile(r"真实客户")),
    ("Feishu app token (cli_a*)", re.compile(r"\bcli_a[a-zA-Z0-9]{16,}")),
    ("Feishu user/tenant token (t-*)", re.compile(r"\bt-[a-zA-Z0-9]{30,}")),
    (
        "populated app_secret / app_id / bot_token",
        re.compile(
            r"\b(?:app_secret|app_id|bot_token|refresh_token|access_token)\s*[=:]\s*['\"]?[a-zA-Z0-9_-]{12,}",
            re.IGNORECASE,
        ),
    ),
    (
        "populated generic secret/token",
        re.compile(
            r"\b(?:secret|token)\s*[=:]\s*['\"]?[A-Za-z0-9_-]{20,}",
            re.IGNORECASE,
        ),
    ),
    (
        "private Feishu URL",
        re.compile(
            r"https?://[a-zA-Z0-9.-]+\.feishu\.(?:cn|com)/(?:wiki|base|docs|sheets|drive)/[a-zA-Z0-9]{10,}",
        ),
    ),
]

# Extensions that are worth scanning. Skip binary types.
SCAN_EXTENSIONS = {
    ".md",
    ".py",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".txt",
    ".cfg",
    ".ini",
    ".sh",
    ".env",
    ".example",
    "",  # files without extension (e.g. LICENSE)
}


def _iter_files() -> list[Path]:
    files: list[Path] = []
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix.lower() not in SCAN_EXTENSIONS:
            continue
        files.append(path)
    return files


def test_no_forbidden_patterns_anywhere():
    leaks: list[str] = []
    for path in _iter_files():
        rel = path.relative_to(REPO_ROOT).as_posix()
        if rel in ALLOWED_PATHS:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for label, pattern in PATTERNS:
            for match in pattern.finditer(text):
                line_no = text.count("\n", 0, match.start()) + 1
                leaks.append(f"{rel}:{line_no} [{label}] {match.group(0)[:80]}")
    assert not leaks, "privacy scan failed — leaks found:\n" + "\n".join(leaks)


def test_scan_actually_runs_on_some_files():
    """Sanity check that the test sees the expected repo files."""
    files = _iter_files()
    rels = {p.relative_to(REPO_ROOT).as_posix() for p in files}
    assert "README.md" in rels
    assert "skills/ai-presales/SKILL.md" in rels
    assert "examples/offline/sales-report.json" in rels
