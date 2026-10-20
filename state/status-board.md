# Status board

Generated 2026-10-20T03:24:19Z by `./abos board` · ledger head `798007a6e384` · chain OK · 42 tasks

_Generated file. Do not edit by hand; change the ledger instead._

## Waiting for your approval (0)

_none_

## Blocked (0)

_none_

## In progress (1)

| Task | Priority | Status | Product | Gate | Owner | What | Next action | Updated |
|---|---|---|---|---|---|---|---|---|
| TASK-0005 | MUST | NOT_TESTED | PRD-PLATFORM | G1-phase-2 | builder | Phase 2b Governor: status line script and hooks write the usage ledger and context fill | Ashish: start one claude session, run /rename TASK-0005 governor check, ask one small que… | 2026-10-18 |

## Next (MUST first) (1)

| Task | Priority | Status | Product | Gate | Owner | What | Next action | Updated |
|---|---|---|---|---|---|---|---|---|
| TASK-0022 | SHOULD | NOT_STARTED | PRD-PLATFORM | G2-phase-3 | tester-c | One unconstrained red-team run against the boundary (Muse R3C-6) |  | 2026-10-18 |

## Done (38)

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
| TASK-0014 | MUST | DONE | PRD-PLATFORM | G2-phase-3 | orchestrator | Adversarial suite: prompt injection via handoffs and web text, memory poisoning, source i… | none; live web-page injection continues as TASK-0026 | 2026-10-18 |
| TASK-0017 | MUST | DONE | PRD-PLATFORM | G2-phase-3 | orchestrator | Phase 3 report: pass/fail/NOT_TESTED counts and coverage gaps | none; Phase 4 needs its own approval and waits for TASK-0026 | 2026-10-18 |
| TASK-0018 | MUST | DONE | PRD-PLATFORM | G2-phase-3 | builder | Phase report command: ./abos phase-report <gate> summarises the gate's tasks for the phas… | none | 2026-10-18 |
| TASK-0019 | MUST | DONE | PRD-PLATFORM | handoff-intake | orchestrator | Handoff P2-MUSE-03c from DOT_MUSE: Verify the four R3B follow-ups against the 03c config … | none | 2026-10-18 |
| TASK-0023 | MUST | DONE | PRD-PLATFORM | G2-phase-3 | builder | Tool-loop circuit breaker: PreToolUse hook denies a call repeated as a loop (Governor was… | Ashish: run ./abos install-claude so live sessions load the new hook | 2026-10-18 |
| TASK-0024 | MUST | DONE | PRD-PLATFORM | G2-phase-3 | builder | Switch to PROMPT v2-slim: split v1 word for word into agents/*.md, fix phase/scope/status… | Ashish: run ./abos install-claude so live sessions load the new hook | 2026-10-18 |
| TASK-0025 | MUST | DONE | PRD-PLATFORM | handoff-intake | orchestrator | Handoff P3-MUSE-04 from DOT_MUSE: Gate review of TASK-0014 (adversarial suite + memory-po… | none | 2026-10-18 |
| TASK-0026 | MUST | DONE | PRD-PLATFORM | G3-phase-4 | tester-c | Live web-page injection attack: a fetched page carrying planted instructions must be trea… | Rerun tools/live/web-injection.sh after Claude Code or model upgrades | 2026-10-18 |
| TASK-0027 | MUST | DONE | PRD-COFFEE-PROTEIN | G3-phase-4 | researcher | R0 Market selection: score Canada, US, UK/EU, Australia and other online-reachable market… | none | 2026-10-18 |
| TASK-0028 | MUST | DONE | PRD-COFFEE-PROTEIN | G3-phase-4 | researcher | R1 Market, segments, jobs/pains, substitutes and competitor table for coffee-protein prod… |  | 2026-10-18 |
| TASK-0029 | MUST | DONE | PRD-COFFEE-PROTEIN | G3-phase-4 | researcher | R2 Unit pricing scan: price per serving and per gram of protein, GTA retail and online |  | 2026-10-18 |
| TASK-0030 | MUST | DONE | PRD-COFFEE-PROTEIN | G3-phase-4 | researcher | R3 At least 3 niche/positioning routes with kill criteria | R5/R7/R8/R9 for coffee-rave route | 2026-10-18 |
| TASK-0031 | MUST | DONE | PRD-COFFEE-PROTEIN | G3-phase-4 | researcher | R4 Format decision matrix: RTD vs powder, dairy vs plant |  | 2026-10-18 |
| TASK-0032 | MUST | DONE | PRD-COFFEE-PROTEIN | G3-phase-4 | researcher | R5 Canada regulatory path: Health Canada/CFIA, supplemented foods, caffeine, labelling |  | 2026-10-18 |
| TASK-0033 | MUST | DONE | PRD-COFFEE-PROTEIN | G3-phase-4 | researcher | R6 Manufacturer longlist to shortlist of 3+ co-packers (no contact) |  | 2026-10-18 |
| TASK-0034 | MUST | DONE | PRD-COFFEE-PROTEIN | G3-phase-4 | researcher | R7 Quality and testing plan |  | 2026-10-18 |
| TASK-0035 | MUST | DONE | PRD-COFFEE-PROTEIN | G3-phase-4 | builder | R8 Financial model: 3+ scenarios, landed COGS, break-even, runway within CAD 10-15k |  | 2026-10-18 |
| TASK-0036 | MUST | DONE | PRD-COFFEE-PROTEIN | G3-phase-4 | researcher | R9 Go-to-market: B2C vs B2B vs hybrid, demand tests, stop-loss |  | 2026-10-18 |
| TASK-0037 | MUST | DONE | PRD-COFFEE-PROTEIN | G3-phase-4 | orchestrator | R10 Roadmap, decision dossier and go/no-go | Ashish go/no-go | 2026-10-20 |
| TASK-0038 | MUST | DONE | PRD-PLATFORM | handoff-intake | orchestrator | Handoff P4-GEMINI-01b from GEMINI_APP: Challenger review of the Phase 4 go/no-go dossier | Micro-test only (preceded by a CAD 300–600 digital waitlist + guerilla benchmark-tasting … | 2026-10-20 |
| TASK-0039 | MUST | DONE | PRD-COFFEE-PROTEIN | G3-phase-4 | researcher | R11 verify Gemini's rule claims (import licence, sampling, CASL) |  | 2026-10-20 |
| TASK-0040 | MUST | DONE | PRD-COFFEE-PROTEIN | G3-phase-4 | researcher | R12 Toronto events, retail benchmarks, ad cost benchmarks |  | 2026-10-20 |
| TASK-0041 | MUST | DONE | PRD-COFFEE-PROTEIN | G3-phase-4 | builder | Micro-test kit: plan, scorer (./abos microtest), page draft, approval request |  | 2026-10-20 |
| TASK-0007 | SHOULD | DONE | PRD-PLATFORM | G1-phase-2 | builder | Phase 2c subagent definitions (builder, testers A/B/C, security reviewer) with model and … | none | 2026-10-18 |
| TASK-0008 | SHOULD | DONE | PRD-PLATFORM | G1-phase-2 | builder | Phase 2c Ollama capacity check and golden tasks for qwen2.5:3b | Phase 3: add T0 grounding check, then enable T1 for schema_extraction | 2026-10-18 |
| TASK-0010 | SHOULD | DONE | PRD-PLATFORM | G1-phase-2 | orchestrator | Push Phase 2 branch to GitHub | Push again after each Phase 2 commit | 2026-10-18 |
| TASK-0015 | SHOULD | DONE | PRD-PLATFORM | G2-phase-3 | orchestrator | Routing and cost-cap tests: critical never below floor, budget soft/hard behaviour, usage… | none | 2026-10-18 |
| TASK-0016 | SHOULD | DONE | PRD-PLATFORM | G2-phase-3 | researcher | Capability scout pass: re-check skills, MCP servers and repos for Phase 3-4 needs (promis… | Ashish decides which ADOPT-CANDIDATEs to try (needs approval); llm-guard is archived: NOT… | 2026-10-18 |
| TASK-0020 | SHOULD | DONE | PRD-PLATFORM | G2-phase-3 | tester-c | Repeatable permission probe: re-run the r3c Write/Read/credential probes after every Clau… | Run tools/live/permission-probe.sh after every Claude Code upgrade | 2026-10-18 |
| TASK-0042 | SHOULD | DONE | PRD-COFFEE-PROTEIN | G3-phase-4 | researcher | R13 protein-pocket cup idea (Ashish): existing products, cost, rules, test plan |  | 2026-10-20 |

## Parked (not important now) (2)

| Task | Priority | Status | Product | Gate | Owner | What | Next action | Updated |
|---|---|---|---|---|---|---|---|---|
| TASK-0009 | COULD | NOT_STARTED | PRD-PLATFORM | G1-phase-2 | builder | LangGraph workflow for the developer + 3 testers loop with SQLite checkpoints |  | 2026-10-18 |
| TASK-0021 | COULD | NOT_STARTED | PRD-PLATFORM | G2-phase-3 | tester-c | Keychain and app credential stores as read targets in the adversarial suite (Muse R3C-5) |  | 2026-10-18 |

