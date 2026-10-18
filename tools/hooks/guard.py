#!/usr/bin/env python3
"""PreToolUse guard: enforces SECURITY.md rules outside the model (threat model ASI02, ASI03, ASI05).

deny  -> the tool call is blocked, the reason is shown to Claude
ask   -> Claude Code asks Ashish before running it (approval gate)
allow -> nothing printed; normal permission rules apply

Every deny/ask is appended to logs/guard.jsonl (git-ignored) with the command redacted
to its first 200 characters. Fails closed: if the input can't be parsed, the call is denied.
"""

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path(__file__).resolve().parents[2])
LOG = ROOT / "logs" / "guard.jsonl"

SENSITIVE_PATH = re.compile(r"(^|/)(private)(/|$)|(^|/)\.env(\.|$)|\.(pem|key)$|(^|/)\.ssh(/|$)|(^|/)secrets(/|$)")

# (pattern, decision, reason)
BASH_RULES = [
    (r"(^|[\s;&|])(cat|less|more|head|tail|cp|mv|grep|rg|base64|open|scp)\b[^\n]*(\s|/|^)(private/|\.env\b|\.ssh/|[^\s]+\.pem\b)",
     "deny", "reads or copies private/, .env, keys or SSH files (cloud model must not see them)"),
    (r"\brm\s+(-[a-zA-Z]*r[a-zA-Z]*f|-[a-zA-Z]*f[a-zA-Z]*r)[a-zA-Z]*\s+(/|~|\$HOME|\.\.?)(\s|/?$)",
     "deny", "recursive force delete of a root, home or parent directory"),
    (r"\b(curl|wget)\b[^\n|]*\|\s*(sudo\s+)?(ba|z)?sh\b", "deny", "pipes a downloaded script into a shell"),
    (r"\bsudo\b", "deny", "sudo is never needed for this project"),
    (r"\bchmod\s+(-R\s+)?777\b", "deny", "world-writable permissions"),
    (r"\bgit\s+push\b[^\n]*(--force|-f\b|--mirror)", "deny", "force push rewrites history"),
    (r"\bgit\s+(reset\s+--hard|clean\s+-[a-z]*f)", "ask", "discards local work"),
    (r"\bgit\s+push\b", "ask", "pushing to GitHub needs Ashish's approval (CLAUDE.md)"),
    (r"\b(pip3?|uv|npm|pnpm|yarn|brew|gem|cargo)\s+(install|add|i)\b", "ask", "installing a package needs a reviewed, pinned adoption (Section 2A)"),
    (r"\bgit\s+clone\b", "ask", "cloning external code needs approval (Section 2A)"),
    (r"\b(npm|twine|cargo)\s+publish\b|\bgh\s+release\s+create\b", "deny", "publishing is an external action"),
    (r"\bgh\s+(pr|issue)\s+(create|comment|merge|close)\b", "ask", "posts to GitHub on Ashish's behalf"),
    (r"\b(mail|sendmail|osascript)\b", "ask", "may send messages or control apps"),
    (r"\bollama\s+(pull|rm|push)\b", "ask", "downloads or deletes local models (disk/RAM on an 8 GB Mac)"),
]
_COMPILED = [(re.compile(p), d, r) for p, d, r in BASH_RULES]


def decide(event: dict) -> tuple[str, str]:
    tool = event.get("tool_name", "")
    inp = event.get("tool_input") or {}
    if tool == "Bash":
        cmd = inp.get("command", "")
        verdicts = [(d, r) for rx, d, r in _COMPILED if rx.search(cmd)]
        for wanted in ("deny", "ask"):
            for d, r in verdicts:
                if d == wanted:
                    return d, r
        return "allow", ""
    for key in ("file_path", "path", "notebook_path"):
        value = inp.get(key)
        if value and SENSITIVE_PATH.search(_rel(value)):
            return "deny", f"{tool} on a protected path ({key}); private/, .env, keys and SSH files stay local"
    pattern = inp.get("pattern") or ""
    if tool == "Glob" and SENSITIVE_PATH.search(pattern):
        return "deny", "glob into a protected path"
    return "allow", ""


def _rel(path: str) -> str:
    try:
        return str(Path(path).resolve().relative_to(ROOT.resolve()))
    except ValueError:
        return path


def log(event: dict, decision: str, reason: str) -> None:
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        inp = event.get("tool_input") or {}
        entry = {
            "ts": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "session_id": event.get("session_id"),
            "agent": event.get("agent_type") or "main",
            "tool": event.get("tool_name"),
            "target": str(inp.get("command") or inp.get("file_path") or inp.get("path") or "")[:200],
            "decision": decision,
            "reason": reason,
        }
        with open(LOG, "a") as handle:
            handle.write(json.dumps(entry) + "\n")
    except OSError:
        pass


def main() -> None:
    try:
        event = json.loads(sys.stdin.read())
    except Exception:
        event, decision, reason = {}, "deny", "guard could not parse hook input (fail closed)"
    else:
        decision, reason = decide(event)
    if decision == "allow":
        return
    log(event, decision, reason)
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": decision,
        "permissionDecisionReason": f"abos guard: {reason}",
    }}))


if __name__ == "__main__":
    main()
