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
