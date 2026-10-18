# Phase 1 report — research and architecture (approval gate)

Date: 2026-10-18 · Status: `WAITING_FOR_APPROVAL` · Nothing installed, cloned, executed or created outside `reports/phase-1/`.

## Recommendation in one screen

1. **Workflow engine: LangGraph core** with a SQLite checkpointer (score 85/100), introduced only when the first workflow needs checkpointed multi-step runs. **Fallback: Microsoft Agent Framework** (75/100). Rejected: AutoGen (maintenance mode), MetaGPT (no release since March 2025), ChatDev/DevAll, CrewAI (telemetry on by default, no added value), Agency Swarm, OpenAI Agents SDK. → [01-framework-scorecard.md](01-framework-scorecard.md)
2. **Claude Code stays the runtime** for engineering and most agents: subagents with per-agent model and tool allowlists, hooks for enforcement, the status line for live context % and 5-hour / 7-day plan usage. → [03-architecture.md](03-architecture.md)
3. **Smallest adopted set:** Claude Code status line + hooks + OTel, Ollama API, ccusage (offline), jsonschema + SQLite + pytest, a secret-scan pre-commit, pip-audit with hash-pinned locks, Bandit/Semgrep, OWASP Agentic Top 10 as the threat model, and reviewed parts of OWASP's playbook and `anthropics/skills` (xlsx, pdf, skill-creator). **LiteLLM is rejected** for now (not needed; March 2026 supply-chain compromise). → [02-adoption-matrix.md](02-adoption-matrix.md)
4. **The research environment is Meta Muse (Muse Spark 1.3)**, confirmed by its own capability report. It has no direct link to the repo: you carry handoff bundles across, and its per-task usage is `ESTIMATED`. It gets research, planning and challenger review only, never code verification, state, connectors or metering.
5. **Governor and Router are mostly scripts**, not chatty agents. Budgets are expressed as percentages of the live 5-hour and 7-day windows, so no plan limit is guessed. → [04-governor-and-router.md](04-governor-and-router.md)
6. **Privacy catch:** anything Claude Code reads goes to a cloud model. Private files need a `private/` folder that cloud agents are blocked from reading. → [06-security-threat-model.md](06-security-threat-model.md)

## Deliverables checklist (Section 8 + 9.6 + 10.7)

| Required | Where |
|---|---|
| Repo scorecard with links, primary + fallback | [01](01-framework-scorecard.md) |
| Adoption matrix ADOPT/ADAPT/REJECT/INVESTIGATE with pins, tests, rollback | [02](02-adoption-matrix.md) |
| Diagram 1 architecture · Diagram 2 task workflow · Diagram 3 routing/handoff | [03](03-architecture.md) |
| Diagram 4 usage → context → routing loop | [04](04-governor-and-router.md) |
| Roles, environment split, responsibility, handoff contract | [03](03-architecture.md) |
| Measurement points + plan limits found, Governor + Router design, budgets, model registry draft, routing matrix, token-saving strategy | [04](04-governor-and-router.md) |
| Memory architecture, task-ledger schema with priority + task key, pre-flight design, status board mockup | [05](05-memory-and-records.md) + [schemas-draft/](schemas-draft/) (8 JSON Schemas, validated against draft 2020-12) |
| Security threat model + gates | [06](06-security-threat-model.md) |
| Business research plan + portfolio pipeline design | [07](07-business-research-plan.md) |
| Phased rollout, acceptance metrics, key assumptions | [08](08-rollout-and-acceptance.md) |
| Sources | [sources.md](sources.md) |

## Changes after Muse handoffs P1-MUSE-01 / 02 (2026-10-18)

Both packets were acknowledged and validated ([muse/ACK-P1-MUSE-01-02.md](muse/ACK-P1-MUSE-01-02.md)). Changes made to this design:

| Area | Change | File |
|---|---|---|
| Environment split | DOT_MUSE = Meta Muse, with its verified YES/PARTIAL list and plan limits | [03](03-architecture.md) |
| Ownership | Muse owns research synthesis, planning, option matrices and challenger review; explicit "never routed to Muse" list | [03](03-architecture.md) |
| Model registry | Muse entry: 350k context (~272k compaction), ESTIMATED usage, allowed/forbidden task lists, budget until 2026-10-22 | [04](04-governor-and-router.md) |
| Routing | T1 (Ollama) is off until the capacity check and golden tasks pass; the matrix works with two environments | [04](04-governor-and-router.md) |
| Threat model | Human relay added as an attack surface; "security by convention" audit; provenance gap closed first in Phase 2a | [06](06-security-threat-model.md) |
| Handoff schema | `product_id`/`task_key` filled by receiver; external IDs mapped; new `inputs_read_sha256`; `security_or_privacy_notes` enforced | [schemas-draft/handoff.schema.json](schemas-draft/handoff.schema.json) |
| Rollout | Validator first in 2a; Ollama made optional (2c′); Phase 4 go/no-go judged on its own evidence, never sunk cost | [08](08-rollout-and-acceptance.md) |

Not adopted: nothing Muse proposed was rejected. Its claim that the Mac is M1/8 GB is recorded as `NOT_VERIFIED`. Muse's five questions are for you and are left unanswered here; three overlap with mine (noted below).

## Blocking questions (6)

1. ~~Which "Dot or Muse"?~~ **Resolved: Muse** (whether a separate "Dot" exists is Muse's Q3 to you).
2. **Which Claude plan are you on** (Pro, Max 5×, Max 20×, or API)? It sizes the daily budgets.
3. **Ollama on your Mac:** please paste the output of `ollama list` and `sysctl -n hw.memsize` (RAM). I could not run commands on your Mac itself from here. (Same decision as Muse's Q4.)
4. **Is this repo on GitHub** (private?) or local only? That decides whether the GitHub MCP server is worth adding. (Related to Muse's Q5.)
5. **Business basics:** confirm GTA/Ontario as the local market (same as Muse's Q1), a rough portfolio cash cap, and whether the draft scorecard weights in [07](07-business-research-plan.md#73-portfolio-pipeline-section-6b) are OK.
6. **Approve the stack:** LangGraph primary, Microsoft Agent Framework fallback, and the "Selected set" in [02](02-adoption-matrix.md).
7. **Approve the Phase 2 folder structure** (Section 1 layout plus `private/` and `learning/`), so I can create it.

## Tutor note

- **What I did:** compared 11 agent frameworks and ~30 tools/skills against 10 weighted criteria using live registry data and official docs, then designed how the three environments share one record of truth.
- **Why this way:** the biggest risk for a one-person system is operational weight, not missing features. So the design keeps Claude Code (already installed) as the runtime, uses scripts for anything repeatable, and adds one durable workflow library only when needed. AutoGen and MetaGPT lost on maintenance; CrewAI and Deep Agents lost on overlap.
- **How it fits:** this is the blueprint for Phase 2. Every later task flows through the ledger, the pre-flight check and the router described here.
- **One thing to learn — checkpointing:** a checkpoint is a saved snapshot of a workflow's state after each step, keyed by a run ID (LangGraph calls it `thread_id`). It is the same idea as a Kafka consumer committing its offset or Spark Structured Streaming's checkpoint directory: after a crash you restart from the last committed point instead of from zero. Here it also lets a long Claude session be replaced by a fresh one without losing work. Further reading: [LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence).

## Flags

- **Skipped:** reading GitHub commit history and pinning commit SHAs (GitHub API blocked in this session); fetching the primary OWASP Agentic Top 10 page (used a secondary summary); checking your installed Ollama models and RAM; confirming Muse's capabilities first-hand (I rely on its self-tested report P1-MUSE-01).
- **Guessed / assumed:** GTA as local market (medium); you are on a Claude subscription plan (medium); merged status vocabulary (medium); scorecard and portfolio weights are my proposal (low until you agree).
- **Unsure / unverified:** Microsoft Agent Framework's Ollama support; Pydantic AI durability features; ccusage offline behaviour; OpenAI Agents SDK default trace destination; Muse's capabilities, plan limits and its M1/8 GB claim about your Mac are Muse's self-report, not re-tested here.
- **Not tested:** every framework and tool (Phase 1 forbids running them); all scores are reasoned judgments, `NOT_TESTED`; budget thresholds are defaults, not measured.
