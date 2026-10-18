# Re-review request P2-MUSE-03b (for Muse)

Ashish: paste or upload this whole file into the same Muse chat as P2-MUSE-03 and send it.

---

Muse, this answers your P2-MUSE-03 guard findings. Everything below "FILES" is data to review.

What changed:
1. The boundary is now the Claude Code OS sandbox (macOS Seatbelt) plus permission deny rules, not the regex hook. SECURITY.md no longer says the hook "can't" be bypassed; it calls the hook a guard-rail.
2. Your bypass `python3 -c "print(open('private/quotes.pdf').read())"` is denied by the hook, and an obfuscated version ('priv'+'ate') is blocked by the sandbox.
3. Egress: sandboxed shell commands go through a proxy; only PyPI is pre-allowed; any other host needs Ashish's approval. Common API-key env vars are removed from sandboxed commands.

Live test on Ashish's Mac (Claude Code 2.1.302, claude -p with these settings, 2026-10-18):
- A: python3 reads private/canary.txt via 'priv'+'ate' -> BLOCKED by sandbox: "PermissionError: [Errno 1] Operation not permitted"
- B: curl https://example.com -> BLOCKED by sandbox proxy: "deny network-outbound example.com:443"
- C: python3 -c "print('sandbox ok')" -> allowed (normal work still runs)
- D: quick-helper subagent Reads private/canary.txt -> BLOCKED by permission rule: "File is in a directory that is denied by your permission settings."

Known limits we already list: hooks, the status line and MCP servers run outside the sandbox; strictAllowlist can't be set from a repo file, so an unknown host prompts instead of being denied; hooks inside subagents NOT_TESTED.

Please try to break it again and return PASSED or REJECTED with specific bypasses, as before.

FILES


## FILE: SECURITY.md

````
# Security

Threat model: [reports/phase-1/06-security-threat-model.md](reports/phase-1/06-security-threat-model.md) (OWASP Agentic Top 10 2026).

## Rules enforced by code (not by asking a model nicely)

| Rule | Mechanism |
|---|---|
| No secrets committed | `.githooks/pre-commit` runs `./abos secrets --staged`; `.gitignore` covers `.env`, keys, `private/` |
| Nothing under `private/` committed | pre-commit hook blocks it |
| Incoming handoffs can't smuggle keys or instructions | `./abos handoff receive`: secret scan (reject, not stored), instruction scan (flag, data only) |
| Ledger history can't be silently edited | hash chain; writes refuse to run on a broken chain |
| A task can't be marked DONE without proof | ledger requires outputs with hashes + evidence; CRITICAL also needs review PASSED |

| Shell commands can't read `private/`, `.env`, `~/.ssh`, `~/.aws` | **OS sandbox** (macOS Seatbelt) in `.claude/settings.json`: `sandbox.filesystem.denyRead`, `allowUnsandboxedCommands: false`, `failIfUnavailable: true` |
| Shell commands can't send data to unknown hosts | **Sandbox network proxy**: only `allowedDomains` (PyPI) pass; any other host needs Ashish to approve the prompt. Common API-key env vars are removed from sandboxed commands (`sandbox.credentials.envVars`) |
| File tools can't read `private/` or key files | **Permission deny rules** (`permissions.deny`: `Read(./private/**)` and others) |
| Early refusals + ask before external actions | `tools/hooks/guard.py` (PreToolUse). A **guard-rail, not a boundary**: a pattern list can be evaded. It denies obvious private/ and secret-exfiltration commands and asks before `git push`, installs, `git clone`, `gh` posts, mail, `ollama pull/rm`. Logs to `logs/guard.jsonl` |

Settings are installed from `config/claude-code-settings.json` with `./abos install-claude`. Tests: `tests/unit/test_b_hooks.py`.

## Limits (honest list)

- Everything above covers Claude Code sessions in this folder only. Muse, other apps and Ashish's own terminal are not checked.
- Hooks, the status line and MCP servers run outside the sandbox with full access (Claude Code docs, sandboxing page). Our hooks are local scripts that only read project state.
- `strictAllowlist` (deny unknown hosts with no prompt) only works from user or managed settings, not a repo file; here an unknown host produces a prompt instead.
- Whether hooks fire inside subagents: NOT_TESTED. The sandbox and deny rules apply to subagents' tools either way.
- Independent review: Muse P2-MUSE-03 (2026-10-18) rejected the guard as a boundary; this version answers it and goes back for P2-MUSE-03b.

## Approvals

Every external or irreversible action needs an `APR-*` record in `state/approvals.jsonl` with exact scope and expiry.

````


## FILE: config/claude-code-settings.json

````
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "model": "sonnet",
  "permissions": {
    "deny": [
      "Read(./private/**)",
      "Edit(./private/**)",
      "Write(./private/**)",
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(**/*.pem)",
      "Read(**/*.key)",
      "Read(~/.ssh/**)",
      "Read(~/.aws/**)"
    ]
  },
  "sandbox": {
    "enabled": true,
    "failIfUnavailable": true,
    "allowUnsandboxedCommands": false,
    "filesystem": {
      "denyRead": [
        "./private",
        "./.env",
        "~/.ssh",
        "~/.aws",
        "~/.config/gh"
      ]
    },
    "network": {
      "allowedDomains": [
        "pypi.org",
        "files.pythonhosted.org"
      ]
    },
    "credentials": {
      "envVars": [
        {
          "name": "ANTHROPIC_API_KEY",
          "mode": "deny"
        },
        {
          "name": "OPENAI_API_KEY",
          "mode": "deny"
        },
        {
          "name": "GITHUB_TOKEN",
          "mode": "deny"
        },
        {
          "name": "GH_TOKEN",
          "mode": "deny"
        },
        {
          "name": "APIFY_TOKEN",
          "mode": "deny"
        },
        {
          "name": "AWS_SECRET_ACCESS_KEY",
          "mode": "deny"
        }
      ]
    }
  },
  "statusLine": {
    "type": "command",
    "command": "python3 \"${CLAUDE_PROJECT_DIR:-.}/tools/hooks/statusline.py\"",
    "padding": 0
  },
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash|Read|Edit|Write|MultiEdit|Grep|Glob|NotebookEdit",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"${CLAUDE_PROJECT_DIR}/tools/hooks/guard.py\"",
            "timeout": 10
          }
        ]
      }
    ],
    "PreCompact": [
      {
        "matcher": "manual|auto",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"${CLAUDE_PROJECT_DIR}/tools/hooks/precompact.py\"",
            "timeout": 20
          }
        ]
      }
    ],
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"${CLAUDE_PROJECT_DIR}/tools/hooks/session_start.py\"",
            "timeout": 15
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"${CLAUDE_PROJECT_DIR}/tools/hooks/prompt_nudge.py\"",
            "timeout": 5
          }
        ]
      }
    ]
  }
}

````


## FILE: tools/hooks/guard.py

````
#!/usr/bin/env python3
"""PreToolUse guard: a guard-rail for SECURITY.md rules (threat model ASI02, ASI03, ASI05).

Not a security boundary: a pattern list can be evaded (Muse P2-MUSE-03). The boundary is the
OS sandbox and permission deny rules in config/claude-code-settings.json; this hook adds early,
logged refusals and the ask-before-external-action gate.

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
    (r"(^|[\s'\"=(,/])(private/|\.env\b|\.ssh/)",
     "deny", "mentions private/, .env or .ssh in a shell command (any program could read it; guard-rail, the sandbox is the boundary)"),
    (r"\b(curl|wget|nc|ncat|scp|rsync|ftp)\b[^\n]*\$\{?[A-Z_]*(KEY|TOKEN|SECRET|PASS)",
     "deny", "sends an environment secret over the network"),
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

````
