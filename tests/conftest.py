import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "skills" / "ai-presales" / "scripts"

for path in (REPO_ROOT, SCRIPTS_DIR):
    p = str(path)
    if p not in sys.path:
        sys.path.insert(0, p)
