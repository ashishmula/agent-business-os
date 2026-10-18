# agent-business-os

A multi-agent operating system that coordinates **Claude Code**, **Dot/Muse** and **local Ollama models** with one shared source of truth — first used for a white-label coffee-protein shake business, then for a portfolio of other white-label products started small locally (`PROMPT.md` Section 6B), and reusable for future projects.

**Status:** Phase 1 (research and architecture) — not started. Nothing installed or built yet.

## Files

| File | What it is |
|---|---|
| `PROMPT.md` | The full project brief. Sections 1–8 are the original prompt; **Section 9** adds the token/context governance and model-routing agents. |
| `CLAUDE.md` | Short standing rules Claude Code loads every session (current phase, what it may write, what to read first). |
| `prompt-source/` | The original prompt, unchanged, for reference. |

## The two governance agents (Section 9)

**Context & Token Governor**
- Watches how full each session's context window is (warn 60%, act 75%, hard stop 85% — tunable).
- Before a session fills up, it saves a checkpoint and continues the work in a fresh session that starts from that checkpoint — so nothing is lost.
- Tracks tokens per agent, per task, per model, per day in a ledger; flags waste (re-reading files, re-doing research, huge logs in context, top models on easy jobs).
- Daily budgets with a protected reserve for critical work; slows or pauses non-critical work before limits are hit.
- Any token-saving change must pass a before/after quality test — same output or it's rolled back.
- Built mostly as scripts and hooks, not a chatty LLM, so monitoring doesn't itself burn tokens.

**Model Router**
- Sends each task to the cheapest option that has proven good enough: plain code → local Ollama → small → mid → top-tier model.
- Moves up a tier when output fails checks; moves down only with test evidence.
- Critical work (architecture, regulatory, financial, security, go/no-go) has a minimum tier and is never downgraded to save tokens.
- Private content stays local unless you approve otherwise.
- Logs every routing decision with its reason.

## How to start

```bash
git clone <this-repo-url>
cd agent-business-os
claude
```

Then say: **"Start Phase 1."** Claude Code reads `CLAUDE.md` automatically and `PROMPT.md` on the first session, and writes its Phase 1 report to `reports/phase-1/`, then stops for your approval.

## Phases

1. Research and architecture — approval gate
2. Build the minimal orchestration backbone, ledgers and routing
3. Test resume, failure recovery, security, routing and token limits
4. Coffee-protein market validation and go/no-go
5. Execution tasks — each with separate approval
