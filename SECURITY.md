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

| Claude Code can't read `private/`, `.env`, keys or SSH files | `.claude/settings.json` (installed from `config/claude-code-settings.json`) PreToolUse hook `tools/hooks/guard.py` denies Read/Edit/Write/Grep/Glob on those paths and shell commands that read or copy them |
| Dangerous shell commands blocked | same hook denies `sudo`, `rm -rf` of root/home/parent, `curl … \| sh`, force push, `chmod 777`, publishing |
| External actions need Ashish | same hook makes Claude Code ask before `git push`, package installs, `git clone`, `gh pr/issue` posts, mail, `ollama pull/rm` |

Every deny/ask is logged to `logs/guard.jsonl` (local only). Tests: `tests/unit/test_b_hooks.py`.

## Limits of the hooks (honest list)

- They only cover Claude Code sessions in this folder. Muse, other tools and Ashish's own terminal are not checked.
- A pattern deny-list can be evaded by an unusual command (for example a script that reads `private/` indirectly). It is a guard rail, not a sandbox; Claude Code's own permission prompts stay on.
- The hook asks before an external action; it does not yet check that a matching `APR-*` record exists. NOT_TESTED against real prompt-injection attempts.

## Approvals

Every external or irreversible action needs an `APR-*` record in `state/approvals.jsonl` with exact scope and expiry.
