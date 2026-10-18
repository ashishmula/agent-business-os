#!/usr/bin/env python3
"""SessionStart hook: give a new, resumed or compacted session the facts it needs from the
records (ledger head, chain status, open tasks, latest checkpoint) so it does not rely on chat memory.

Output is factual state only, no instructions beyond pointing at the records.
"""

import json

from _common import latest_checkpoint, ledger, read_event

SHOW = [("Waiting for Ashish's approval", {"WAITING_FOR_APPROVAL"}),
        ("In progress or review", {"IN_PROGRESS", "REVIEW", "NOT_TESTED"}),
        ("Blocked", {"BLOCKED", "FAILED", "CHANGES_REQUESTED"})]


def context(event: dict) -> str:
    led = ledger()
    events = led.events()
    tasks = led.tasks()
    problems = led.verify_chain()
    lines = [f"agent-business-os state at session start ({event.get('source', 'startup')}):",
             f"- Ledger: {len(events)} events, head {events[-1]['hash'][:12] if events else 'empty'}, "
             f"chain {'OK' if not problems else 'BROKEN (' + str(len(problems)) + ' problems; run ./abos ledger verify)'}."]
    for title, statuses in SHOW:
        rows = [f"{t} {v['status']} {v['objective'][:70]}" for t, v in sorted(tasks.items()) if v.get("status") in statuses]
        if rows:
            lines.append(f"- {title}: " + "; ".join(rows[:6]))
    nxt = [t for t, v in sorted(tasks.items()) if v.get("status") == "NOT_STARTED" and v.get("priority") == "MUST"]
    if nxt:
        lines.append(f"- Next MUST tasks: {', '.join(nxt[:6])}")
    ckp = latest_checkpoint()
    if ckp:
        lines.append(f"- Latest checkpoint {ckp.get('checkpoint_id')} ({ckp.get('created_at')}): "
                     f"{ckp.get('current_step', '')[:150]} Next: {ckp.get('next_action', '')[:150]}")
    lines.append("- Full board: state/status-board.md. Session name should contain the task id (/rename TASK-nnnn) "
                 "so usage is attributed.")
    return "\n".join(lines)


def main() -> None:
    try:
        text = context(read_event())
    except Exception as exc:
        text = f"agent-business-os: could not read project state ({type(exc).__name__}); run ./abos ledger verify."
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": text}}))


if __name__ == "__main__":
    main()
