# Status board

Generated 2026-10-18T05:17:35Z by `./abos board` · ledger head `5a0546b3a26f` · chain OK · 18 tasks

_Generated file. Do not edit by hand; change the ledger instead._

## Waiting for your approval (0)

_none_

## Blocked (0)

_none_

## In progress (2)

| Task | Priority | Status | Product | Gate | Owner | What | Next action | Updated |
|---|---|---|---|---|---|---|---|---|
| TASK-0005 | MUST | NOT_TESTED | PRD-PLATFORM | G1-phase-2 | builder | Phase 2b Governor: status line script and hooks write the usage ledger and context fill | Ashish installs config/claude-code-settings.json; run one session named TASK-nnnn; ./abos… | 2026-10-18 |
| TASK-0014 | MUST | REVIEW | PRD-PLATFORM | G2-phase-3 | orchestrator | Adversarial suite: prompt injection via handoffs and web text, memory poisoning, source i… | Muse gate review at end of Phase 3 (in P3 review request) | 2026-10-18 |

## Next (MUST first) (1)

| Task | Priority | Status | Product | Gate | Owner | What | Next action | Updated |
|---|---|---|---|---|---|---|---|---|
| TASK-0017 | MUST | NOT_STARTED | PRD-PLATFORM | G2-phase-3 | orchestrator | Phase 3 report: pass/fail/NOT_TESTED counts and coverage gaps |  | 2026-10-18 |

## Done (14)

| Task | Priority | Status | Product | Gate | Owner | What | Next action | Updated |
|---|---|---|---|---|---|---|---|---|
| TASK-0001 | MUST | DONE | PRD-PLATFORM | handoff-intake | orchestrator | Handoff P1-MUSE-01 from DOT_MUSE: Report the DOT_MUSE (Muse) environment's real, verified… | Ask Muse to include security_or_privacy_notes and inputs_read_sha256 in future packets | 2026-10-18 |
| TASK-0002 | MUST | DONE | PRD-PLATFORM | handoff-intake | orchestrator | Handoff P1-MUSE-02 from DOT_MUSE: Give an independent first view of PROMPT.md: top risks,… | Ask Muse to include security_or_privacy_notes and inputs_read_sha256 in future packets | 2026-10-18 |
| TASK-0003 | MUST | DONE | PRD-PLATFORM | G0-phase-1-approval | orchestrator | Phase 1 research and architecture report | none | 2026-10-18 |
| TASK-0004 | MUST | DONE | PRD-PLATFORM | G1-phase-2 | builder | Phase 2a backbone: ledger, pre-flight, handoff intake, status board, schemas, config, sec… | Start Phase 2b | 2026-10-18 |
| TASK-0006 | MUST | DONE | PRD-PLATFORM | G1-phase-2 | builder | Phase 2b security hooks: PreToolUse deny-list, block reads of private/, approval check fo… | Phase 3 adversarial suite re-runs these checks | 2026-10-18 |
| TASK-0011 | MUST | DONE | PRD-PLATFORM | G2-phase-3 | builder | T0 grounding check for local-model extractions; enable T1 for schema_extraction | Add a T1 extraction runner when Phase 4 needs bulk extraction | 2026-10-18 |
| TASK-0012 | MUST | DONE | PRD-PLATFORM | G2-phase-3 | orchestrator | Developer + 3 testers loop: take one real feature through builder, tester-a, tester-b, te… | none | 2026-10-18 |
| TASK-0013 | MUST | DONE | PRD-PLATFORM | G2-phase-3 | orchestrator | Resilience suite: restart/resume from checkpoint, failure recovery, schema errors, duplic… | none | 2026-10-18 |
| TASK-0018 | MUST | DONE | PRD-PLATFORM | G2-phase-3 | builder | Phase report command: ./abos phase-report <gate> summarises the gate's tasks for the phas… | none | 2026-10-18 |
| TASK-0007 | SHOULD | DONE | PRD-PLATFORM | G1-phase-2 | builder | Phase 2c subagent definitions (builder, testers A/B/C, security reviewer) with model and … | none | 2026-10-18 |
| TASK-0008 | SHOULD | DONE | PRD-PLATFORM | G1-phase-2 | builder | Phase 2c Ollama capacity check and golden tasks for qwen2.5:3b | Phase 3: add T0 grounding check, then enable T1 for schema_extraction | 2026-10-18 |
| TASK-0010 | SHOULD | DONE | PRD-PLATFORM | G1-phase-2 | orchestrator | Push Phase 2 branch to GitHub | Push again after each Phase 2 commit | 2026-10-18 |
| TASK-0015 | SHOULD | DONE | PRD-PLATFORM | G2-phase-3 | orchestrator | Routing and cost-cap tests: critical never below floor, budget soft/hard behaviour, usage… | none | 2026-10-18 |
| TASK-0016 | SHOULD | DONE | PRD-PLATFORM | G2-phase-3 | researcher | Capability scout pass: re-check skills, MCP servers and repos for Phase 3-4 needs (promis… | Ashish decides which ADOPT-CANDIDATEs to try (needs approval); llm-guard is archived: NOT… | 2026-10-18 |

## Parked (not important now) (1)

| Task | Priority | Status | Product | Gate | Owner | What | Next action | Updated |
|---|---|---|---|---|---|---|---|---|
| TASK-0009 | COULD | NOT_STARTED | PRD-PLATFORM | G1-phase-2 | builder | LangGraph workflow for the developer + 3 testers loop with SQLite checkpoints |  | 2026-10-18 |

