---
id: DEC-0002
date: 2026-10-18
decided_by: Ashish
status: APPROVED
evidence: project thread ("go ahead"; then to Muse: "i asked it to do so the research will be in one place"); Muse accepted in its P2-MUSE-03 follow-up
supersedes_part_of: DEC-0001 (Muse as research environment)
---

# Claude does research and building; Muse only reviews at gates

**Decision:** All research synthesis, planning and building run in Claude Code. Meta Muse is the independent challenger on CRITICAL gate outputs only (for example the Phase 1 report, the security guard, regulatory matrix, financial go/no-go).

**Ashish's reason, in his words:** "i asked it to do so the research will be in one place."

**Why it holds up:** one repo, one research trail, no stale handoffs with Ashish as the courier. This removes Muse's own Risk 1 from P1-MUSE-02. Muse agreed in the P2-MUSE-03 follow-up and confirmed its role as gate challenger.

**Process note:** Claude first recorded this after Ashish's "go ahead" without his reasoning; Muse correctly flagged that it looked like a silent change to the approved design. This record now carries his reasoning.

**Changes:** `config/routing-rules.toml` (research_synthesis -> CLAUDE_CODE T3 researcher agent; gate_challenger_review -> DOT_MUSE), `config/model-registry.toml` (Muse allowed_tasks narrowed), `config/budgets.toml` (Muse policy).

**Risk on record:** Claude-only research loses the cross-provider check on STANDARD work. Mitigation: Tester B checks claims against sources; CRITICAL rows still get the Muse review.
