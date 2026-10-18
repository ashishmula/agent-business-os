# Architecture

The approved design lives in [reports/phase-1/](reports/phase-1/README.md). Key files:
diagrams and roles in [03](reports/phase-1/03-architecture.md), Governor and Router in
[04](reports/phase-1/04-governor-and-router.md), memory and records in [05](reports/phase-1/05-memory-and-records.md).

## What is built (Phase 2a)

| Piece | Where | What it does |
|---|---|---|
| `./abos` CLI | `tools/abos/` | Standard-library Python only, no installs |
| Task ledger | `state/task-ledger/events.jsonl` | Append-only, hash-chained event log; current state is replayed from it. `./abos ledger export-sqlite` builds a SQLite copy for SQL queries |
| Pre-flight check | `tools/abos/ledger.py` | REUSE / DELTA / BLOCKED / PARKED / REJECTED / RUN before any task is recorded |
| Handoff intake | `./abos handoff receive <file>` | Secret scan, JSON parse, schema check, instruction scan, input freshness, evidence mapping, ACK, ledger task |
| Status board | `state/status-board.md` | Generated after every ledger change |
| Schemas | `schemas/` | v1.0, checked by `tools/abos/schema.py` (fails closed on unsupported keywords) |
| Config | `config/*.toml` | Budgets, routing rules, model registry, freshness |
| Test runner | `./abos test` | Runs `tests/unit`, stores raw output + hash in `test-results/unit/` |

Config is TOML rather than YAML because Python's standard library reads TOML (`tomllib`), so no package is needed.
