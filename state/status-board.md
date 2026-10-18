# Status board

Generated 2026-10-18T03:19:01Z by `./abos board` · ledger head `a3616e3f8040` · chain OK · 10 tasks

_Generated file. Do not edit by hand; change the ledger instead._

## Waiting for your approval (0)

_none_

## Blocked (0)

_none_

## In progress (3)

| Task | Priority | Status | Product | Gate | Owner | What | Next action | Updated |
|---|---|---|---|---|---|---|---|---|
| TASK-0003 | MUST | REVIEW | PRD-PLATFORM | G0-phase-1-approval | orchestrator | Phase 1 research and architecture report | Muse challenger review P1-MUSE-03 at the end-of-Phase-2 gate (DEC-0002) | 2026-10-18 |
| TASK-0005 | MUST | NOT_TESTED | PRD-PLATFORM | G1-phase-2 | builder | Phase 2b Governor: status line script and hooks write the usage ledger and context fill | Ashish installs config/claude-code-settings.json; run one session named TASK-nnnn; ./abos… | 2026-10-18 |
| TASK-0006 | MUST | REVIEW | PRD-PLATFORM | G1-phase-2 | builder | Phase 2b security hooks: PreToolUse deny-list, block reads of private/, approval check fo… | Install settings; independent security review (different model) before DONE | 2026-10-18 |

## Next (MUST first) (2)

| Task | Priority | Status | Product | Gate | Owner | What | Next action | Updated |
|---|---|---|---|---|---|---|---|---|
| TASK-0007 | SHOULD | NOT_STARTED | PRD-PLATFORM | G1-phase-2 | builder | Phase 2c subagent definitions (builder, testers A/B/C, security reviewer) with model and … |  | 2026-10-18 |
| TASK-0008 | SHOULD | NOT_STARTED | PRD-PLATFORM | G1-phase-2 | builder | Phase 2c Ollama capacity check and golden tasks for qwen2.5:3b |  | 2026-10-18 |

## Done (4)

| Task | Priority | Status | Product | Gate | Owner | What | Next action | Updated |
|---|---|---|---|---|---|---|---|---|
| TASK-0001 | MUST | DONE | PRD-PLATFORM | handoff-intake | orchestrator | Handoff P1-MUSE-01 from DOT_MUSE: Report the DOT_MUSE (Muse) environment's real, verified… | Ask Muse to include security_or_privacy_notes and inputs_read_sha256 in future packets | 2026-10-18 |
| TASK-0002 | MUST | DONE | PRD-PLATFORM | handoff-intake | orchestrator | Handoff P1-MUSE-02 from DOT_MUSE: Give an independent first view of PROMPT.md: top risks,… | Ask Muse to include security_or_privacy_notes and inputs_read_sha256 in future packets | 2026-10-18 |
| TASK-0004 | MUST | DONE | PRD-PLATFORM | G1-phase-2 | builder | Phase 2a backbone: ledger, pre-flight, handoff intake, status board, schemas, config, sec… | Start Phase 2b | 2026-10-18 |
| TASK-0010 | SHOULD | DONE | PRD-PLATFORM | G1-phase-2 | orchestrator | Push Phase 2 branch to GitHub | Push again after each Phase 2 commit | 2026-10-18 |

## Parked (not important now) (1)

| Task | Priority | Status | Product | Gate | Owner | What | Next action | Updated |
|---|---|---|---|---|---|---|---|---|
| TASK-0009 | COULD | NOT_STARTED | PRD-PLATFORM | G1-phase-2 | builder | LangGraph workflow for the developer + 3 testers loop with SQLite checkpoints |  | 2026-10-18 |

