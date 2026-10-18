#!/usr/bin/env python3
"""Claude Code status line + Governor sensor (PROMPT.md 9.2.1).

Reads the session JSON Claude Code sends on stdin, appends a snapshot to
state/context-sessions/<session>.jsonl when something meaningful changed, and prints one
line: context fill, 5-hour and 7-day plan usage, task, and the Governor level.
Must never crash or slow the UI: every failure falls back to a plain line.
"""

import json
import os
import re
import sys
import tomllib
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path(__file__).resolve().parents[2])
SESSIONS = ROOT / "state" / "context-sessions"


def thresholds() -> dict:
    try:
        with open(ROOT / "config" / "budgets.toml", "rb") as handle:
            cfg = tomllib.load(handle)
        return {"context": cfg["context"], "five": cfg["windows"]["five_hour"], "seven": cfg["windows"]["seven_day"]}
    except Exception:
        return {"context": {"warn_pct": 60, "act_pct": 75, "hard_pct": 85},
                "five": {"soft_pct": 70, "hard_pct": 90}, "seven": {"soft_pct": 70, "hard_pct": 90}}


def level(fill, five, seven, t) -> str:
    c = t["context"]
    if fill is not None and fill >= c["hard_pct"]:
        return "HARD: checkpoint + rotate now"
    if fill is not None and fill >= c["act_pct"]:
        return "ACT: checkpoint, then /compact or new session"
    if any(v is not None and v >= w["hard_pct"] for v, w in ((five, t["five"]), (seven, t["seven"]))):
        return "BUDGET HARD: pause non-critical work"
    if any(v is not None and v >= w["soft_pct"] for v, w in ((five, t["five"]), (seven, t["seven"]))):
        return "BUDGET SOFT: cheaper tier, queue non-urgent"
    if fill is not None and fill >= c["warn_pct"]:
        return "WARN: pointers only"
    return "ok"


def snapshot(data: dict) -> dict:
    cw = data.get("context_window") or {}
    rl = data.get("rate_limits") or {}
    name = data.get("session_name") or ""
    task = re.search(r"TASK-\d{4,}", name)
    return {
        "ts": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "session_id": data.get("session_id"),
        "session_name": name,
        "task_id": task.group(0) if task else None,
        "agent": (data.get("agent") or {}).get("name") or "main",
        "model": (data.get("model") or {}).get("id"),
        "context_window_size": cw.get("context_window_size"),
        "context_fill_pct": cw.get("used_percentage"),
        "total_input_tokens": cw.get("total_input_tokens"),
        "total_output_tokens": cw.get("total_output_tokens"),
        "current_usage": cw.get("current_usage"),
        "cost_usd_list_price": (data.get("cost") or {}).get("total_cost_usd"),
        "five_hour_pct": (rl.get("five_hour") or {}).get("used_percentage"),
        "five_hour_resets_at": (rl.get("five_hour") or {}).get("resets_at"),
        "seven_day_pct": (rl.get("seven_day") or {}).get("used_percentage"),
        "seven_day_resets_at": (rl.get("seven_day") or {}).get("resets_at"),
        "cache_hit_ratio": (data.get("prompt_cache") or {}).get("hit_ratio"),
        "measurement": "MEASURED",
        "source": "STATUSLINE",
    }


def record(snap: dict) -> None:
    if not snap["session_id"]:
        return
    SESSIONS.mkdir(parents=True, exist_ok=True)
    path = SESSIONS / f"{re.sub(r'[^A-Za-z0-9_-]', '_', snap['session_id'])}.jsonl"
    keys = ("context_fill_pct", "total_input_tokens", "total_output_tokens", "five_hour_pct",
            "seven_day_pct", "model", "task_id", "agent")
    if path.exists():
        lines = path.read_text().splitlines()
        if lines:
            last = json.loads(lines[-1])
            if all(last.get(k) == snap.get(k) for k in keys):
                return  # nothing changed; keep the log small
    with open(path, "a") as handle:
        handle.write(json.dumps(snap, sort_keys=True) + "\n")


def fmt(v) -> str:
    return "?" if v is None else f"{v:.0f}%"


def main() -> None:
    try:
        data = json.loads(sys.stdin.read() or "{}")
        snap = snapshot(data)
        record(snap)
        lvl = level(snap["context_fill_pct"], snap["five_hour_pct"], snap["seven_day_pct"], thresholds())
        model = (data.get("model") or {}).get("display_name") or snap["model"] or "?"
        task = snap["task_id"] or "no task (use /rename TASK-nnnn)"
        print(f"{model} · ctx {fmt(snap['context_fill_pct'])} · 5h {fmt(snap['five_hour_pct'])} · "
              f"7d {fmt(snap['seven_day_pct'])} · {task} · {lvl}")
    except Exception as exc:  # never break the UI
        print(f"abos statusline error: {type(exc).__name__}")


if __name__ == "__main__":
    main()
