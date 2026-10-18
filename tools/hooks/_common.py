"""Shared helpers for the Claude Code hook scripts. Read-only access to project state.

ROOT comes from CLAUDE_PROJECT_DIR (set by Claude Code for hooks) so tests can point the
hooks at a temp folder; the abos package itself is always loaded from this checkout.
"""

import json
import os
import re
import sys
import tomllib
from datetime import datetime, timezone
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))

from abos.ledger import Ledger  # noqa: E402

ROOT = Path(os.environ.get("CLAUDE_PROJECT_DIR") or TOOLS.parent)
SESSIONS = ROOT / "state" / "context-sessions"
CHECKPOINTS = ROOT / "state" / "checkpoints"

DEFAULT_THRESHOLDS = {"context": {"warn_pct": 60, "act_pct": 75, "hard_pct": 85},
                      "five": {"soft_pct": 70, "hard_pct": 90}, "seven": {"soft_pct": 70, "hard_pct": 90}}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_event() -> dict:
    try:
        data = json.loads(sys.stdin.read() or "{}")
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def thresholds() -> dict:
    try:
        with open(ROOT / "config" / "budgets.toml", "rb") as handle:
            cfg = tomllib.load(handle)
        return {"context": cfg["context"], "five": cfg["windows"]["five_hour"], "seven": cfg["windows"]["seven_day"]}
    except Exception:
        return DEFAULT_THRESHOLDS


def ledger() -> Ledger:
    return Ledger(ROOT / "state" / "task-ledger" / "events.jsonl")


def session_file(session_id: str) -> Path:
    return SESSIONS / f"{re.sub(r'[^A-Za-z0-9_-]', '_', session_id)}.jsonl"


def last_snapshot(session_id: str | None) -> dict:
    """Latest status-line snapshot for this session, or {} if none yet."""
    if not session_id:
        return {}
    path = session_file(session_id)
    try:
        lines = [line for line in path.read_text().splitlines() if line.strip()]
        return json.loads(lines[-1]) if lines else {}
    except (OSError, ValueError):
        return {}


def latest_checkpoint() -> dict:
    try:
        files = sorted(CHECKPOINTS.glob("CKP-*.json"))
        return json.loads(files[-1].read_text()) if files else {}
    except (OSError, ValueError):
        return {}
