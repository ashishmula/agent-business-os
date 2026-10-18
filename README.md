# agent-business-os

A multi-agent operating system that coordinates **Claude Code**, **Dot/Muse** and **local Ollama models** with one shared source of truth — first used for a white-label coffee-protein shake business, then for a portfolio of other white-label products started small locally (`PROMPT.md` Section 6B), and reusable for future projects.

**Status:** Phase 1 (research and architecture) — not started. Nothing installed or built yet.

## Files

| File | What it is |
|---|---|
| `PROMPT.md` | The full project brief. Sections 1–8 are the original prompt. Added: **6B** product portfolio beyond coffee-protein · **9** token/context governor and model router · **10** memory for every agent and workflow · **11** tutor mode. |
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

## Memory for every agent and workflow (Section 10)

- One task ledger: every task has an owner, status, priority (**MUST / SHOULD / COULD / NOT_NOW**), the reason it exists, inputs and outputs with hashes.
- Each workflow remembers which steps are done, skipped (with reason) or next — so a crash or new session resumes at the right step.
- Each agent has a small memory file: what it has done, lessons learned, pitfalls.
- Before any task, a pre-flight check: already done? → reuse it. Inputs changed? → redo only the changed part. Dependencies done? Is it a MUST right now?
- A status board you can read at a glance: Done · In progress · Next · Blocked · Waiting for you · Parked.

## Tutor mode (Section 11)

After each deliverable, agents explain in plain language what they did and why, and flag anything skipped, guessed or unverified. If you ask for something wrong or unsafe, they stop and explain the mistake instead of just complying.

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
