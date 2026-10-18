# 01 · Framework scorecard and recommendation

Checked: 2026-10-18. Evidence IDs (`SRC-xx`) resolve in [sources.md](sources.md).
GitHub's API was blocked from this session, so star counts come from the public repo pages (WebFetch) and release activity comes from PyPI/npm registries. Last-commit dates could not be read from GitHub pages (`NOT_VERIFIED`).

## What is being compared

A **framework** here means the workflow/orchestration layer: the code that runs a graph of steps, saves state between steps (checkpointing), pauses for human approval and resumes after a crash. In backend terms it plays the role Spring Batch or a Kafka Streams topology plays for data jobs: it is the runtime that owns "which step is next" and "where did we stop".

It is not the same as a **skill** (instructions an agent loads), a **tool/MCP server** (a capability, like a REST client), or **security enforcement** (permission checks that run outside the model).

## Scoring criteria (weights sum to 100)

| # | Criterion | Weight | Why it matters here |
|---|---|---|---|
| C1 | Durable state, checkpoint and resume | 15 | Section 5/10: resume at the right step after crash or session rotation |
| C2 | Human-in-the-loop approvals | 10 | Section 7: approval gates before external actions |
| C3 | Local model (Ollama) support | 10 | T1 tier and privacy routing |
| C4 | Maintenance and release activity | 10 | Avoid legacy/maintenance-mode projects |
| C5 | License | 5 | Commercial use for a business |
| C6 | Security posture / least-privilege fit | 10 | Section 7, OWASP ASI |
| C7 | Observability without forced cloud export | 10 | Section 9 metering |
| C8 | Operational simplicity (higher = simpler) | 15 | One person runs this on a MacBook Air |
| C9 | Fit with Claude Code + file handoffs | 10 | Claude Code is the engineering authority |
| C10 | Low lock-in / portability | 5 | Swap later without redesign |

Scores are 1 (poor) to 5 (strong). Weighted total = Σ(weight × score) / 5, out of 100. Scores are a reasoned judgment from the evidence listed, not a benchmark: no framework was installed or run (Phase 1 rule), so every row is `NOT_TESTED`.

## Scored table

| Candidate | Version / last release (registry) | License | Stars (page) | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 | C10 | **Total** | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **LangGraph** (core) | `langgraph` 1.2.16 · 2026-10-16 · 281 releases | MIT | n/a | 5 | 5 | 5 | 5 | 5 | 3 | 4 | 3 | 4 | 4 | **85** | **PRIMARY** |
| Pydantic AI (extra candidate) | `pydantic-ai` 2.57.0 · 2026-10-16 | MIT | n/a | 3* | 3* | 4 | 5 | 5 | 4 | 4 | 4 | 4 | 4 | 78 | INVESTIGATE FURTHER |
| Claude Code / Claude Agent SDK (baseline, already in use) | `claude-code` 2.1.302 · 2026-10-16; `claude-agent-sdk` 0.2.168 | Proprietary terms | n/a | 3 | 4 | 1 | 5 | 2 | 4 | 5 | 5 | 5 | 2 | 76 | ADOPT as engineering runtime, not workflow engine |
| **Microsoft Agent Framework** | `agent-framework` 1.22.0 · 2026-10-15 | MIT | 12.6k | 4 | 4 | 3* | 5 | 5 | 3 | 5 | 3 | 3 | 3 | **75** | **FALLBACK** |
| LangChain Deep Agents | `deepagents` 0.7.28 · 2026-10-16 | MIT | ~30.3k | 5 | 5 | 5 | 5 | 5 | 2 | 4 | 2 | 2 | 3 | 75 | NOT_NOW (overlaps Claude Code) |
| OpenAI Agents SDK | `openai-agents` 0.24.0 · 2026-10-15 | MIT | 28.6k | 3 | 4 | 3 | 5 | 5 | 3 | 3* | 4 | 3 | 3 | 71 | REJECT for now |
| CrewAI | `crewai` 1.15.28 · 2026-10-14 | MIT | 59.7k | 3 | 3 | 4 | 5 | 5 | 2 | 3 | 3 | 3 | 3 | 66 | REJECT |
| AutoGen | `autogen-agentchat` 0.7.5 · 2025-09-30 | MIT (code) | 60.4k | 3 | 3 | 4 | 1 | 5 | 3 | 3 | 3 | 2 | 2 | 57 | REJECT (maintenance mode) |
| Agency Swarm | `agency-swarm` 1.11.0 · 2026-08-03 | MIT | 4.5k | 2 | 2 | 3 | 3 | 5 | 3 | 3 | 3 | 2 | 2 | 54 | REJECT |
| ChatDev 2.0 / DevAll | `chatdev` 0.1.0 · 2026-03-21 (1 release) | Apache-2.0 | 34.5k | 2 | 2 | 3* | 3 | 5 | 2 | 2 | 2 | 1 | 2 | 45 | REJECT |
| MetaGPT | `metagpt` 0.8.2 · 2025-03-09 | MIT | 70.9k | 2 | 2 | 3 | 1 | 5 | 2 | 2 | 2 | 1 | 2 | 41 | REJECT |

`*` = claim not confirmed in the source read; scored conservatively.

## Evidence notes per candidate

- **LangGraph** — Checkpointers: `InMemorySaver` (dev), `SqliteSaver` (local file), `PostgresSaver` (prod); state is scoped by `thread_id`; checkpointers enable human-in-the-loop, time travel and fault tolerance; a separate Store holds cross-thread memory [SRC-10]. Most active release cadence of the set [SRC-01]. Weak spots: the surrounding LangChain/LangSmith ecosystem is large; we would use core `langgraph` + `langgraph-checkpoint-sqlite` only and no hosted LangSmith (C6/C8 docked for that discipline burden).
- **Microsoft Agent Framework** — Python and .NET; graph workflows with "checkpointing, streaming, human-in-the-loop, and time-travel"; built-in OpenTelemetry [SRC-11]. 1.x on PyPI [SRC-01]. Quickstart is Azure/Foundry-centric and the README does not name Ollama, so C3 is unconfirmed. It is the successor to AutoGen [SRC-12].
- **AutoGen** — README: "AutoGen is now in maintenance mode. It will not receive new features or enhancements and is community managed going forward." New users are sent to Microsoft Agent Framework [SRC-12]. Rejected on maintenance status, not quality.
- **MetaGPT** — No PyPI release since 2025-03-09; newest README news item is March 2025 and the team's focus moved to the commercial MGX product [SRC-13]. Software-company role-play design does not fit a business-ops workflow.
- **ChatDev 2.0 / DevAll** — "Zero-Code Multi-Agent Platform" released 2026-01-07; v1 moved to a maintenance branch; one PyPI release; runs a server on port 6400 and needs an LLM key in `.env` [SRC-14]. A platform, not a library we can embed; high operational load.
- **CrewAI** — Crews (role agents) + Flows (event workflows). Anonymous telemetry is **on by default** (opt out with `OTEL_SDK_DISABLED=true`); `share_crew` would send goals and task outputs [SRC-15]. Commercial AMP upsell. Nothing it does is missing from LangGraph for our needs.
- **OpenAI Agents SDK** — Sessions, handoffs, guardrails, HITL, tracing; non-OpenAI models through LiteLLM/any-llm extras [SRC-16]. The LiteLLM path carries the March 2026 supply-chain incident risk [SRC-22]; default trace export destination not confirmed.
- **Agency Swarm** — Extends OpenAI Agents SDK; directional communication flows (`>`), thread save/load callbacks [SRC-17]. Smallest community; adds a layer on top of a layer.
- **Deep Agents** — LangGraph-based harness with planning, sub-agents, filesystem backends, HITL, skills, MCP; any tool-calling model incl. Ollama [SRC-18]. Its own security policy is "trust the LLM" — enforcement must live in the sandbox. It duplicates what Claude Code already does, so `NOT_NOW`; revisit if we need an unattended agent outside Claude Code.
- **Pydantic AI** — Added as a credible lighter alternative; very active [SRC-01]. Durable-execution and HITL claims not read in this session → `INVESTIGATE FURTHER` before it could replace the fallback.
- **Claude Code / Agent SDK** — Already the engineering environment. Strong native metering (status line JSON with context %, 5-hour and 7-day plan usage; OpenTelemetry token and cost metrics; 30+ hook events, many of which can block) [SRC-30..33]. It runs Claude models only, and its workflow memory is per-session, so it is the runtime for engineering work and agents, not the durable workflow engine.

### "Multi-hundred-agent" claims
ChatDev, MetaGPT and CAMEL (`camel-ai` 0.2.90, last release 2026-03-22 [SRC-01]) market large agent societies. Anthropic's own write-up reports multi-agent systems use about **15× the tokens of chat** and help mainly on broad, parallel research, while tasks with many dependencies (most coding) gain less [SRC-40]. For a one-person business the agent count should be small: 1 orchestrator, a handful of specialists created on demand, and deterministic scripts for everything repeatable.

## Recommendation

**Primary: LangGraph core** (`langgraph` + SQLite checkpointer), used narrowly as the durable workflow engine for multi-step runs that must survive restarts (research pipelines, Ollama batch extraction, the developer + 3 testers loop). Wrapped behind a thin adapter so workflow definitions are plain YAML/JSON in `/workflows`, not LangGraph-specific code.

**Fallback: Microsoft Agent Framework (Python)** — same capability class (checkpoint, HITL, OTel), MIT, active; swap via the adapter if LangGraph fails Phase 3 tests. Verify Ollama connectivity before relying on it.

**Runtime: Claude Code** stays the engineering authority and the place most agents run (subagents with per-agent model and tool allowlists, hooks for enforcement and metering).

**Honest caveat:** for the first weeks of Phase 2, plain Python + SQLite + Claude Code hooks may be all that is needed. LangGraph is introduced only when the first workflow needs checkpointed multi-step execution outside a Claude Code session. That keeps the "smallest set" rule from Section 2A.
