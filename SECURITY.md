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

## Still convention only (open risks, closed in Phase 2b/2c)

- Cloud agents not reading `private/` → Claude Code `PreToolUse` hook (Phase 2b).
- Dangerous shell commands → `PreToolUse` deny-list (Phase 2b).
- Approval before external actions → approval records + hook (Phase 2b).

## Approvals

Every external or irreversible action needs an `APR-*` record in `state/approvals.jsonl` with exact scope and expiry.
