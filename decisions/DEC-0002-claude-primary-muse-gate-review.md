---
id: DEC-0002
date: 2026-10-18
decided_by: Ashish
status: APPROVED
evidence: project thread, Ashish "go ahead" to the Claude-vs-Muse recommendation
supersedes_part_of: DEC-0001 (Muse as research environment)
---

# Claude does research and building; Muse only reviews at gates

**Decision:** All research synthesis, planning and building run in Claude Code, where the ledger, tests and memory live. Meta Muse is used only as an independent challenger on CRITICAL gate outputs (for example the Phase 1 report, regulatory matrix, financial go/no-go), a handful of times rather than daily.

**Why:** every Muse task needs Ashish to relay files by hand, Muse cannot read the repo or ledger, and its free weekly allowance runs out. A second model from a different provider still has value as a reviewer because it catches errors Claude would repeat.

**Changes:** `config/routing-rules.toml` (research_synthesis -> CLAUDE_CODE T3; new gate_challenger_review -> DOT_MUSE), `config/model-registry.toml` (Muse allowed_tasks narrowed), `config/budgets.toml` (Muse policy).

**Risk on record:** Claude-only research loses the cross-provider check on STANDARD work. Mitigation: Tester B reviews research claims against sources; CRITICAL rows still get the Muse review.
