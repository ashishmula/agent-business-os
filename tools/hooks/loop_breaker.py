#!/usr/bin/env python3
"""PreToolUse hook: circuit breaker for runaway tool loops (Governor waste detection, PROMPT.md 9).

An agent stuck in a loop repeats the same tool call with the same arguments. This hook keeps a
short per-session history of call fingerprints (tool name + hash of its input) and trips when:
- the same call is about to run more than `max_identical_in_a_row` times back to back, or
- the same call is about to run more than `max_same_in_window` times in the last `window` calls
  (catches A, B, A, B ping-pong loops).

A trip denies that one call with a reason telling the agent to stop, change approach or ask Ashish.
Normal work is never counted as a loop: many different calls in a row are fine.

Fails open (unlike guard.py): this is a cost guard, not a security boundary, so a broken history
file must not stop work. Every trip is appended to logs/loop-breaker.jsonl (git-ignored); the
history holds hashes only, never the command text.
"""

import hashlib
import json
import os
import re
import sys
import tomllib
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path(__file__).resolve().parents[2])
HISTORY = ROOT / "state" / "loop-breaker"  # not context-sessions: the usage report reads every *.jsonl there
LOG = ROOT / "logs" / "loop-breaker.jsonl"
DEFAULTS = {"max_identical_in_a_row": 3, "max_same_in_window": 6, "window": 20}


def limits() -> dict:
    try:
        with open(ROOT / "config" / "budgets.toml", "rb") as handle:
            cfg = tomllib.load(handle).get("loop_breaker", {})
        return {k: int(cfg.get(k, v)) for k, v in DEFAULTS.items()}
    except Exception:
        return dict(DEFAULTS)


def fingerprint(event: dict) -> str:
    body = json.dumps([event.get("tool_name", ""), event.get("tool_input") or {}], sort_keys=True, default=str)
    return hashlib.sha256(body.encode()).hexdigest()[:16]


def history_file(session_id: str) -> Path:
    return HISTORY / f"{re.sub(r'[^A-Za-z0-9_-]', '_', session_id)}.jsonl"


def load(path: Path) -> list[str]:
    try:
        return [json.loads(line)["fp"] for line in path.read_text().splitlines() if line.strip()]
    except (OSError, ValueError, KeyError, TypeError):
        return []


def decide(history: list[str], fp: str, lim: dict) -> str:
    """Return a trip reason, or "" to let the call run. `history` is oldest first."""
    streak = 0
    for past in reversed(history):
        if past != fp:
            break
        streak += 1
    if streak >= lim["max_identical_in_a_row"]:
        return f"the same tool call already ran {streak} times in a row"
    recent = history[-(lim["window"] - 1):] if lim["window"] > 1 else []
    count = recent.count(fp)
    if count >= lim["max_same_in_window"]:
        return f"the same tool call already ran {count} times in the last {lim['window']} calls"
    return ""


def record(path: Path, history: list[str], fp: str, lim: dict) -> None:
    keep = (history + [fp])[-lim["window"]:]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps({"fp": item}) + "\n" for item in keep))


def log_trip(event: dict, fp: str, reason: str) -> None:
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        entry = {"ts": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
                 "session_id": event.get("session_id"), "agent": event.get("agent_type") or "main",
                 "tool": event.get("tool_name"), "fp": fp, "reason": reason}
        with open(LOG, "a") as handle:
            handle.write(json.dumps(entry) + "\n")
    except OSError:
        pass


def main() -> None:
    try:
        event = json.loads(sys.stdin.read() or "{}")
        session_id = event.get("session_id")
        if not isinstance(event, dict) or not session_id:
            return
        lim, fp, path = limits(), fingerprint(event), history_file(session_id)
        history = load(path)
        reason = decide(history, fp, lim)
        record(path, history, fp, lim)
    except Exception:
        return
    if not reason:
        return
    log_trip(event, fp, reason)
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": (f"abos loop breaker: {reason}. This looks like a loop. Stop repeating it: "
                                     "read the last result, change approach, or checkpoint and ask Ashish."),
    }}))


if __name__ == "__main__":
    main()
