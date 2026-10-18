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
| Shell commands can't send data anywhere without Ashish | **Sandbox network proxy** with an empty allowlist: every host needs Ashish to approve the prompt (in unattended `claude -p` runs it is simply denied) |
| Secrets in environment variables don't reach commands | `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1` strips credentials from all subprocesses (allowlist-style, not a name list); `sandbox.credentials.envVars` kept as a second layer |
| Agents can't plant SSH keys or login scripts | Sandbox writes only to the project and temp folders (plus `denyWrite` on `~/.ssh`, `~/.aws`, `~/.gnupg`, LaunchAgents); `Edit(...)` deny rules for those paths and `~/.zshrc`, `~/.bashrc`, `~/.gitconfig` cover the file tools |
| File tools can't read `private/` or key files | **Permission deny rules** (`permissions.deny`: `Read(./private/**)` and others) |
| Planted instructions in memory, decisions, agent files | `./abos scan-memory` flags instruction-like text; pre-commit blocks it and the SessionStart hook warns agents to treat it as data (pattern-based: a reworded line can pass) |
| Early refusals + ask before external actions | `tools/hooks/guard.py` (PreToolUse). A **guard-rail, not a boundary**: a pattern list can be evaded. It denies obvious private/ and secret-exfiltration commands and asks before `git push`, installs, `git clone`, `gh` posts, mail, `ollama pull/rm`. Logs to `logs/guard.jsonl` |
| Agents can't quietly switch off the safety tooling | `guard.py` asks Ashish before any Edit/Write or shell write to `tools/hooks/`, `.claude/`, `.githooks/`, `config/claude-code-settings.json` or `tools/abos/secrets.py` (P3-MUSE-04). Same guard-rail limits as above |
| A stuck agent can't repeat one call forever | `tools/hooks/loop_breaker.py` denies the 4th identical tool call in a row or the 7th in 20. Exact repeats only; fails open by design (a cost guard must never stop work) |

Settings are installed from `config/claude-code-settings.json` with `./abos install-claude`. Tests: `tests/unit/test_b_hooks.py`.

## Limits (honest list)

- Everything above covers Claude Code sessions in this folder only. Muse, other apps and Ashish's own terminal are not checked.
- Hooks, the status line and MCP servers run outside the sandbox with full access (Claude Code docs, sandboxing page). Our hooks are local scripts that only read project state.
- `strictAllowlist` (deny unknown hosts with no prompt) only works from user or managed settings, not a repo file; here an unknown host produces a prompt instead.
- Hooks inside subagents: observed firing (the guard blocked tester-c subagent commands that mentioned `private/` in `test-results/devloop/r1-tester-c.json` and `r2-tester-c-blocked.json`, 2026-10-18). Not a dedicated test.
- Independent review: Muse P2-MUSE-03 rejected the regex guard as a boundary; P2-MUSE-03b accepted the sandbox design and found R3B-1 (home-folder writes) and R3B-3 (env-var name list, PyPI egress), both fixed and live-tested 2026-10-18 (`test-results/live/`).
- Permission `Write(...)` rules never match in Claude Code; only `Edit(...)` rules cover file writes (warning seen in a live run).
- `git commit --no-verify` skips the pre-commit hook, and a lost exec bit made it fail silently once. The SessionStart scan and `./abos scan-memory` (whole repo) are the backstops (P3-MUSE-04).
- The memory scan is a tripwire, not a wall: P3-MUSE-04 found 10 wordings that passed; they are now caught and tested, but new rewordings will pass. `reports/` is not scanned because it quotes untrusted text on purpose; `evidence/` is.
- Live injection from a fetched web page is NOT_TESTED (network is off). Phase 4 web reading waits for that attack to exist and pass (TASK-0026).
- The Governor's budget limits warn and checkpoint (`prompt_nudge.py`, `precompact.py`); nothing forces a pause in code. On the Claude Pro plan the plan itself caps spend. A hard money cap per task is required before any pay-per-use API (`PROMPT.md` Section 2).
- Loop-breaker history is in the project folder, so an agent could delete it, and a new session starts fresh. Whether subagents share the parent's session id is NOT_VERIFIED.

## Approvals

Every external or irreversible action needs an `APR-*` record in `state/approvals.jsonl` with exact scope and expiry.
