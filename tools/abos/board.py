"""Generate state/status-board.md from the ledger (PROMPT.md 10.5). No LLM involved."""

from __future__ import annotations

from pathlib import Path

from . import REPO_ROOT
from .ledger import Ledger
from .util import now_iso

BOARD = REPO_ROOT / "state" / "status-board.md"
PRIORITY_ORDER = {"MUST": 0, "SHOULD": 1, "COULD": 2, "NOT_NOW": 3}

SECTIONS = [
    ("Waiting for your approval", lambda t: t["status"] == "WAITING_FOR_APPROVAL"),
    ("Blocked", lambda t: t["status"] in {"BLOCKED", "FAILED", "CHANGES_REQUESTED"}),
    ("In progress", lambda t: t["status"] in {"IN_PROGRESS", "REVIEW", "NOT_TESTED"}),
    ("Next (MUST first)", lambda t: t["status"] == "NOT_STARTED" and t["priority"] in {"MUST", "SHOULD"}),
    ("Done", lambda t: t["status"] in {"DONE", "VERIFIED", "PASSED", "SKIPPED_NOT_APPLICABLE"}),
    ("Parked (not important now)", lambda t: t["status"] == "NOT_STARTED" and t["priority"] in {"COULD", "NOT_NOW"}),
]


def render(ledger: Ledger | None = None) -> str:
    ledger = ledger or Ledger()
    tasks = sorted(ledger.tasks().values(), key=lambda t: (PRIORITY_ORDER[t["priority"]], t["task_id"]))
    events = ledger.events()
    head = events[-1]["hash"][:12] if events else "empty"
    chain = "OK" if not ledger.verify_chain() else "BROKEN — run `./abos ledger verify`"

    lines = [
        "# Status board",
        "",
        f"Generated {now_iso()} by `./abos board` · ledger head `{head}` · chain {chain} · {len(tasks)} tasks",
        "",
        "_Generated file. Do not edit by hand; change the ledger instead._",
        "",
    ]
    for title, keep in SECTIONS:
        rows = [t for t in tasks if keep(t)]
        lines.append(f"## {title} ({len(rows)})")
        lines.append("")
        if not rows:
            lines += ["_none_", ""]
            continue
        lines.append("| Task | Priority | Status | Product | Gate | Owner | What | Next action | Updated |")
        lines.append("|---|---|---|---|---|---|---|---|---|")
        for t in rows:
            lines.append(
                f"| {t['task_id']} | {t['priority']} | {t['status']} | {t['product_id']} | {t['serves_gate']} "
                f"| {t['owner_agent']} | {_cell(t['objective'])} | {_cell(t.get('next_action', ''))} | {t['updated_at'][:10]} |"
            )
        lines.append("")
    return "\n".join(lines)


def _cell(text: str, limit: int = 90) -> str:
    text = " ".join(str(text).split()).replace("|", "/")
    return text if len(text) <= limit else text[: limit - 1] + "…"


def write(ledger: Ledger | None = None, path: Path = BOARD) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render(ledger) + "\n")
    return path
