#!/usr/bin/env python3
"""PreCompact hook: write a checkpoint before Claude Code compacts the conversation (PROMPT.md 9.2.3).

The checkpoint holds pointers (ledger head, open tasks, files) rather than content, so a
fresh or compacted session can resume from the records instead of from chat memory.
Never blocks compaction: any error is swallowed and the hook exits 0 with no output.
"""

import json

from _common import CHECKPOINTS, ROOT, last_snapshot, ledger, now_iso, read_event

OPEN = {"IN_PROGRESS", "REVIEW", "NOT_TESTED", "BLOCKED", "CHANGES_REQUESTED", "WAITING_FOR_APPROVAL"}


def build(event: dict) -> dict:
    led = ledger()
    events = led.events()
    tasks = led.tasks()
    snap = last_snapshot(event.get("session_id"))
    open_tasks = sorted(t for t, v in tasks.items() if v.get("status") in OPEN)
    task_id = snap.get("task_id") or (open_tasks[0] if open_tasks else "UNASSIGNED")
    current = tasks.get(task_id, {})
    numbers = [int(p.stem.split("-")[1]) for p in CHECKPOINTS.glob("CKP-*.json") if p.stem.split("-")[1].isdigit()]
    pointers = [{"artifact_id": "task-ledger", "path_or_uri": "state/task-ledger/events.jsonl",
                 "version_or_hash": events[-1]["hash"] if events else "empty"}]
    for out in current.get("outputs", [])[:10]:
        pointers.append({k: out[k] for k in ("artifact_id", "path_or_uri", "version_or_hash")})
    trigger = (event.get("trigger") or "auto").lower()
    return {
        "checkpoint_id": f"CKP-{max(numbers, default=0) + 1:04d}",
        "created_at": now_iso(),
        "trigger": "MANUAL" if trigger == "manual" else "PRECOMPACT",
        "session_id": event.get("session_id") or "unknown",
        "task_id": task_id,
        "current_step": f"{task_id}: {current.get('status', 'no ledger task')} - {current.get('objective', '')[:200]}",
        "next_action": current.get("next_action") or "Read state/status-board.md and pick the next MUST task",
        "pending_approvals": [],
        "ledger_hash": events[-1]["hash"] if events else "empty",
        "pointers": pointers,
        "summary": (f"Compaction ({trigger}) at context {snap.get('context_fill_pct', '?')}%. "
                    f"Open tasks: {', '.join(open_tasks) or 'none'}. Chain "
                    f"{'OK' if not led.verify_chain() else 'BROKEN'}.")[:3000],
    }


def main() -> None:
    try:
        checkpoint = build(read_event())
        CHECKPOINTS.mkdir(parents=True, exist_ok=True)
        path = CHECKPOINTS / f"{checkpoint['checkpoint_id']}.json"
        with open(path, "x") as handle:  # never overwrite an earlier checkpoint
            json.dump(checkpoint, handle, indent=2)
    except Exception:
        pass  # a failed checkpoint must not stop compaction


if __name__ == "__main__":
    main()
