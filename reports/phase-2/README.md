# Phase 2 report: the backbone (2026-10-18)

Branch `phase-2-backbone` on GitHub (main unchanged). Approval records: APR-0001 (start Phase 2), APR-0002 (push this branch).

## What exists now

| Part | What it does | Proof |
|---|---|---|
| Task ledger (`./abos ledger`) | Every task, status and output in a hash-chained log; edits are detected; a pre-flight check stops repeated work | 61 unit tests, TEST-* records in `test-results/unit/` |
| Handoff intake (`./abos handoff receive`) | Checks Muse packets for schema, secrets and hidden instructions before use | P1-MUSE-01/02 ingested |
| Status board | `state/status-board.md`, generated from the ledger | regenerated on every change |
| Governor | Status line (context %, 5h and 7d usage), checkpoint before compaction, budget nudges, `./abos usage report` | hook tests; status line itself NOT_TESTED live |
| Security guard | Blocks reads of `private/` and key files and dangerous commands; asks before pushes and installs | hook tests + live deny (LIVE-20261018034052) |
| Model routing | Sonnet default; Haiku helper for simple jobs; Opus only for critical reviews; 8 subagents | live: main on Sonnet, helper on Haiku |
| Local model | qwen2.5:3b passed 20 extraction tasks (96.9%) | EVAL-20261018033333; kept off until a grounding check exists |

## Decisions
DEC-0001 stack (LangGraph only when needed, stdlib backbone). DEC-0002 Claude does research and building; Muse reviews critical gates.

## Gate checklist (end of Phase 2)
- [x] Backbone, Governor, guard, routing built and tested
- [ ] Ashish approves Phase 2 and the start of Phase 3
- [ ] Muse review P2-MUSE-03 of the Phase 1 report and the guard (`P2-MUSE-03-review-request.md`); Muse's free allowance resets 2026-10-22

## Flags
- **Not tested:** status line and usage report in a real interactive session (only runs in Terminal Claude Code).
- **Guessed:** the 20 golden listings were written by Claude, so the local-model score may be optimistic.
- **Unsure:** the guard is a pattern list; a determined script could get around it. Muse's review is meant to find those gaps.
- **Skipped:** LangGraph (TASK-0009) parked until a multi-step workflow needs checkpoints.

## Phase 3 preview
Agent team workflows: developer + 3 testers loop, the T0 grounding check that unlocks the local model, waste detection in the usage report, and templates for product workstreams. No business research until Phase 4 is approved.
