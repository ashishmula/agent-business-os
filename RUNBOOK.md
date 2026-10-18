# Runbook

All commands run from the repo root on your Mac. Python 3.11+ only; nothing to install.

| I want to… | Run |
|---|---|
| See what's going on | open `state/status-board.md` (or `./abos board` to regenerate) |
| List tasks | `./abos ledger list` |
| Check nobody edited the ledger | `./abos ledger verify` |
| Query tasks with SQL | `./abos ledger export-sqlite` then `sqlite3 state/task-ledger/ledger.sqlite "select task_id,status from tasks"` |
| Bring in a Muse packet | save it as a `.json` file, then `./abos handoff receive path/to/file.json` |
| Run the tests | `./abos test` (result saved in `test-results/unit/`) |
| Scan files for secrets | `./abos secrets <files>` |

## After a crash or a new session

1. `./abos ledger verify` (must say OK).
2. Read `state/status-board.md`.
3. Continue from the task's `next_action`. Never rebuild state from chat memory.

## One-time setup (done for you on 2026-10-18)

`git config core.hooksPath .githooks` turns on the secret-scan pre-commit hook.
