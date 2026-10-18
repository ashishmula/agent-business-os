# Runbook

All commands run from the repo root on your Mac. Python 3.11+ only; nothing to install.

| I want to… | Run |
|---|---|
| See what's going on | open `state/status-board.md` (or `./abos board` to regenerate) |
| List tasks | `./abos ledger list` |
| Check nobody edited the ledger | `./abos ledger verify` |
| Query tasks with SQL | `./abos ledger export-sqlite` then `sqlite3 state/task-ledger/ledger.sqlite "select task_id,status from tasks"` |
| Bring in a Muse packet | save it as a `.json` file, then `./abos handoff receive path/to/file.json` |
| Summarise a gate's tasks for the phase report | `./abos phase-report <gate> [--write reports/<file>.md] [--force]` (verifies the ledger first; `--write` only under `reports/`, no overwrite without `--force`) |
| Run the tests | `./abos test` (result saved in `test-results/unit/`) |
| Re-check the safety boundary after a Claude Code upgrade | `tools/live/permission-probe.sh` (runs 2 short Claude Code sessions with canary files; prints PASS or FAIL; record in `test-results/live/`) |
| Scan files for secrets | `./abos secrets <files>` |
| See token use per task/day | `./abos usage report` → `reports/usage/<date>.md` |
| Attribute a Claude Code session to a task | type `/rename TASK-0005 short name` in Claude Code |
| See what the guard blocked | `tail logs/guard.jsonl` |

## Claude Code in this folder (Phase 2b)

Install or update it with `./abos install-claude` (copies the reviewed `config/claude-code-settings.json` and `agents/claude/*.md` into `.claude/`), then restart Claude Code. Models are chosen automatically: Sonnet by default, subagents pinned per `config/routing-rules.toml`. After that, opening Claude Code in this folder loads it: the bottom status line shows model · context % · 5-hour % · 7-day % · task · Governor level. `ok` means carry on; `ACT` means checkpoint and `/compact`; `BUDGET SOFT` means use a cheaper model. Before compaction a checkpoint lands in `state/checkpoints/`, and a new session starts with a short summary of the ledger.

## After a crash or a new session

1. `./abos ledger verify` (must say OK).
2. Read `state/status-board.md`.
3. Continue from the task's `next_action`. Never rebuild state from chat memory.

## One-time setup (done for you on 2026-10-18)

`git config core.hooksPath .githooks` turns on the secret-scan pre-commit hook.
