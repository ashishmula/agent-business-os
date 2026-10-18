# Learning log

Longer explanations live here once, and reports link to them.

## 2026-10-18 · Event-sourced ledger
The task ledger is an append-only log of events (`TASK_CREATED`, `TASK_UPDATED`). The current state of every task is computed by replaying the log, the same way a Kafka Streams app rebuilds a table from a topic. Each event stores the hash of the previous one (a hash chain), so editing or deleting an old line breaks the chain and `./abos ledger verify` reports it. Benefit: full history, easy git diffs, tamper evidence. Cost: replay gets slower with many events, which is when a SQLite index becomes worth keeping.

## 2026-10-18 · Pre-flight check
Before a task is recorded, a script computes a `task_key` (hash of the normalized objective, scope, product and input hashes) and compares it with the ledger: reuse finished fresh work, redo only the delta when inputs changed, block on unfinished dependencies, park low-priority work, reject tasks with no definition of done. It is the agent version of an idempotency key on a REST API.

## 2026-10-18 · Checkpointing
A checkpoint is a saved snapshot after each step, like a Kafka consumer offset or a Spark streaming checkpoint: after a crash you resume from the last saved step. See https://docs.langchain.com/oss/python/langgraph/persistence.
