---
id: DEC-0001
date: 2026-10-18
decided_by: Ashish
status: APPROVED
evidence: reports/phase-1/README.md, reports/phase-1/01-framework-scorecard.md
---

# Phase 1 stack and Phase 2 start

**Decision:** Claude Code is the runtime; LangGraph core is the workflow engine when a checkpointed workflow is first needed; Microsoft Agent Framework is the fallback; the "selected set" in reports/phase-1/02 is adopted, free and open-source tools first. Phase 2 started 2026-10-18 (decision card + "start phase 2").

**Conditions from Ashish:** add components only when really needed; free APIs first.

**Dissent / risks on record:** Muse P1-MUSE-02 risks 1–5 (human relay, Phase 1 scope, Ollama on 8 GB, security by convention, provenance before backbone). Folded into the design; see reports/phase-1/README.md.

**Deviation recorded during Phase 2a:** config uses TOML (stdlib) instead of YAML; ledger is a hash-chained JSONL event log with an on-demand SQLite export instead of a SQLite file as the source of truth. Reason: no installs, git-diffable history.
