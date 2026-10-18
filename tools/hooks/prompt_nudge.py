#!/usr/bin/env python3
"""UserPromptSubmit hook: if the last status-line reading crossed a Governor threshold, add one
factual line to the prompt context (PROMPT.md 9.2.2). Silent otherwise, and never blocks a prompt.
"""

from _common import last_snapshot, read_event, thresholds


def nudge(event: dict) -> str:
    snap = last_snapshot(event.get("session_id"))
    if not snap:
        return ""
    t = thresholds()
    fill, five, seven = snap.get("context_fill_pct"), snap.get("five_hour_pct"), snap.get("seven_day_pct")
    notes = []
    if fill is not None and fill >= t["context"]["hard_pct"]:
        notes.append(f"context is {fill:.0f}% full (hard limit {t['context']['hard_pct']}%): finish the current "
                     "atomic step, write a checkpoint, then start a new session")
    elif fill is not None and fill >= t["context"]["act_pct"]:
        notes.append(f"context is {fill:.0f}% full (act at {t['context']['act_pct']}%): write a checkpoint, "
                     "then /compact or start a new session")
    for name, value, key in (("5-hour", five, "five"), ("7-day", seven, "seven")):
        if value is not None and value >= t[key]["hard_pct"]:
            notes.append(f"{name} plan usage is {value:.0f}%: pause non-critical work and tell Ashish what is paused")
        elif value is not None and value >= t[key]["soft_pct"]:
            notes.append(f"{name} plan usage is {value:.0f}%: delegate eligible work to quick-helper (Haiku) "
                         "or Sonnet agents, avoid Opus except CRITICAL rows, and queue non-urgent work")
    return ("Governor: " + "; ".join(notes) + ".") if notes else ""


def main() -> None:
    try:
        text = nudge(read_event())
    except Exception:
        text = ""
    if text:
        print(text)


if __name__ == "__main__":
    main()
