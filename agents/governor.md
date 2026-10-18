# Governor and Router: token, context-window and model-routing governance

Moved word for word from PROMPT v1, sections 9 (2026-10-18). Loaded on demand by `PROMPT.md` Section 9. Section numbers inside are v1's.

## 9. Token, context-window and model-routing governance (added requirement)

Two additional components are mandatory: **(A) Context & Token Governor** and **(B) Model Router**. Their purpose is to keep all work inside context windows and session/daily/weekly usage limits, attribute token usage to each agent, cut waste, and switch models sensibly — **without lowering output quality**. They are governance components, not extra "thinking" agents.

### 9.1 Design principle: measure with code, decide with rules, use an LLM only for judgment

- An always-on LLM that "watches" token usage would itself burn tokens. Implement monitoring with deterministic hooks, scripts, ledgers and thresholds. Invoke an LLM only to write a checkpoint summary, diagnose an unusual waste pattern, or propose an optimization — and meter that usage too.
- In Phase 1, discover and verify the real measurement points in each environment; do not assume them. Candidates to verify for **Claude Code**: the context-usage view, manual and automatic compaction, the session cost/usage view, status-line JSON input, hooks (for example session start, pre-compaction, post-tool-use, subagent stop, stop), per-subagent model settings, OpenTelemetry usage metrics, and usage fields in local session transcripts. For **Ollama**: per-request prompt and generation token counts from its API. For **Dot/Muse**: record whatever usage reporting genuinely exists; if none exists, log usage as `ESTIMATED` with the estimation method, never as measured.
- Discover the actual plan limits (session/daily/weekly windows, rate limits, context window per model) from current official sources or the account's own usage display. Never hardcode guessed numbers. Store each limit in config with its source and date checked.

### 9.2 Agent A — Context & Token Governor

1. **Context-window monitoring.** Track context fill % for every active session and subagent against that model's real window. Starting thresholds (configurable; tune after measurement):
   - `WARN` at 60%: log and flag; stop loading non-essential files; switch to pointers instead of pasted content.
   - `ACT` at 75%: write a checkpoint (Section 4 handoff envelope plus pointers to canonical records), then compact or continue in a fresh session/subagent seeded only with the checkpoint and task-relevant artifacts.
   - `HARD` at 85%: no new large reads; finish the current atomic step, checkpoint, rotate. A session must never hit its limit in the middle of writing a canonical file.
   - Rotation must not lose project truth. The new session first reads the latest checkpoint and ledgers (Section 5), then restates task ID, status, next action and open defects from the records. Any mismatch → `BLOCKED` and report.
2. **Per-agent token accounting.** Keep an append-only usage ledger. Per call/turn where measurable: timestamp, environment, session ID, agent, task ID, model and version, input tokens, output tokens, cache read/write tokens, tool-output size, latency, cost or plan-usage estimate, and a `MEASURED|ESTIMATED` flag. Roll up per agent, task, workstream, model and day.
3. **Budgets and reserve.** Set daily and per-session budgets per workstream and per agent, plus a protected reserve (default 20%, configurable) for critical work: review gates, regression tests, checkpoints and anything I mark urgent.
   - Soft limit (default 70% of the daily budget): the Router shifts eligible work to cheaper tiers; non-urgent work is queued.
   - Hard limit (default 90%): pause non-critical agents, checkpoint everything, and tell me what is paused, what is left, and when limits reset.
   - Never silently drop, truncate or half-finish work to stay under a limit.
4. **Waste detection and remediation.** Detect, with evidence: repeated reads of unchanged files; re-running research already in `/evidence` that is still fresh; oversized tool outputs or logs pulled into context; whole-file reads where a search or line range would do; long or repeated boilerplate prompts; subagents handed the whole project instead of a `context_brief`; retry loops; agents messaging each other instead of going through the orchestrator; an LLM doing work a script can do; a top-tier model used for low-risk bounded work.
   Remedies: pointer-based context (artifact IDs, paths, hashes); curated summaries with provenance in `/memory`; prompt-prefix caching where the platform supports it; filtering tool output (search, tail, structured fields); deterministic scripts; batching small similar tasks; concise structured handoffs; retry caps.
5. **"Same output" guarantee — every optimization is a controlled experiment.**
   - Keep a golden task set per agent role (representative tasks with acceptance criteria) in `/tests/eval`.
   - Before adopting any optimization (shorter prompt, cheaper model, smaller context, summary in place of full source), run the golden tasks before and after. Compare acceptance criteria, schema validity, citation and evidence-ID accuracy, defect detection and factual checks.
   - Adopt only if quality is within tolerance — default: zero acceptance-criterion regressions, zero lost citations/evidence IDs, zero new schema failures. Otherwise roll back and record the result.
   - Never save tokens by skipping tests, reviews, citations, verification, security checks or approval gates. Those costs are non-negotiable.
6. **Monitoring and reporting.** Provide a clear view of: usage per agent / model / task / day; context fill per active session; budget remaining and reset times; top waste findings with estimated savings (labeled as estimates); optimizations adopted and their measured effect. Default: a generated Markdown/HTML report plus a CSV/SQLite ledger in the repository (no secrets, no private content). Optional after approval: export metrics (for example OpenTelemetry → Prometheus/Grafana, or a tracing tool) for a live dashboard. Send updates on threshold crossings and as a daily summary — not on a noisy timer.
7. **Authority limits.** May: warn, checkpoint, rotate sessions, queue or pause non-critical work, and propose optimizations. May not: delete work, skip a gate, push a critical task below its quality floor, adopt its own optimization without eval evidence, raise budgets, buy plans/credits, or change account settings. Budget increases and plan changes need my approval.

### 9.3 Agent B — Model Router

1. **Inputs to every routing decision:** task type; risk class (`CRITICAL|STANDARD|LOW`); privacy class (whether and where it may go to a cloud model); expected context size; required capabilities (browsing, tools, code execution, long context); benchmark results (Section 3); the Governor's current budget and limit state; provider availability, rate-limit and error status.
2. **Tiers, lowest cost first** (examples to verify; no vendor is assumed best):
   - `T0` Deterministic code, no model: calculations, checksums, validation, state transitions, running tests, formatting, diffing, exact-rule deduplication.
   - `T1` Local Ollama: benchmarked bounded tasks (Section 3); private content where policy allows.
   - `T2` Small/fast cloud model: simple extraction, classification, short summaries, routine edits.
   - `T3` Mid-tier model: most implementation, coding and research synthesis.
   - `T4` Top-tier / deep research (top Claude tier; Dot/Muse where genuinely available): architecture, hard debugging, regulatory and financial reasoning, decision dossiers, red-team review.
3. **Rules.**
   - Route to the lowest tier that has met the task's quality bar on the benchmark. With no benchmark yet, start at a conservative tier and collect data.
   - Escalate one tier on: schema validation failure, missing evidence, reviewer rejection, a test failure attributable to model quality, or repeated retries. Log every escalation.
   - De-escalate only with eval evidence (9.2.5).
   - **Quality floors:** `CRITICAL` tasks (architecture approval, regulatory/quality matrices, financial model, security review, supplier shortlist, go/no-go gates) have a minimum tier and an independent reviewer on a different model or provider where possible. When budget is low, critical tasks wait or ask me — they are never downgraded to save tokens.
   - **Privacy:** private content never goes to a cloud model without my approval (Section 7). Route it to `T0`/`T1` or mark `BLOCKED`.
   - **Limits and outages:** when a provider is rate-limited or close to its usage limit, queue the work, move it to another approved provider/tier that meets the floor, or pause with a checkpoint — and say so in the status update.
   - **Reviewer independence:** for critical artifacts the reviewer must not be the same model-plus-prompt as the author.
4. **Mechanics — be honest about what can switch automatically.** Verify what each environment really supports. In Claude Code, candidates include per-subagent model settings, switching the session model, and plan-versus-execute model combinations; Ollama via its local API; Dot/Muse only through handoff bundles unless a real integration exists. Where a switch requires a human action (for example changing the main session's model, or moving a task to Dot/Muse), the Router produces a recommendation plus a ready-to-use handoff packet instead of claiming it switched. Evaluate model gateways/routers and budget libraries in the Section 2A audit; adopt one only if it adds value over native settings and passes security review.
5. **Routing log.** Every decision appends: task ID; chosen environment, model and tier; alternatives considered; reason; budget state; privacy class; outcome (`PASS|FAIL|ESCALATED`); tokens/cost. This feeds `model_and_tool_usage` in handoffs and updates the benchmark.
6. **Model registry** (config): model ID/version, environment, context window, measured strengths, cost/usage weight, privacy suitability, status (`ACTIVE|DEPRECATED`), source and date checked. When a model changes, re-run the golden tasks before routing critical work to it.

### 9.4 How the Orchestrator, Governor and Router interact

- The Orchestrator owns task assignment. Before dispatch it asks the Router for a tier; the Router reads the Governor's budget state. The Governor enforces context thresholds on running sessions and feeds usage back; the Router updates benchmarks from outcomes.
- Conflicts (for example budget says pause but the task is critical) escalate to me with the trade-off stated.
- Neither the Governor nor the Router messages specialist agents directly; both act through the Orchestrator and the shared records (Section 4).

### 9.5 Records and config to add (only after the repository structure is approved)

```text
config/budgets.yaml          # plan limits (with source/date), budgets, reserve, thresholds
config/model-registry.yaml   # models, windows, strengths, status
config/routing-rules.yaml    # tiers, floors, escalation rules, privacy routing
state/usage-ledger/          # append-only JSONL/CSV or SQLite
state/routing-log/           # one record per routing decision
state/context-sessions/      # active sessions, fill %, last checkpoint
tests/eval/golden-tasks/     # per-role golden tasks with acceptance criteria
test-results/eval/           # before/after evidence for every optimization
reports/usage/               # daily usage, waste findings, savings measured
```

Versioned schemas for the usage record, routing decision, budget state and checkpoint go in `/schemas`. Example usage record:

```json
{
  "usage_schema_version": "1.0",
  "timestamp": "2026-10-18T14:05:00Z",
  "environment": "CLAUDE_CODE|DOT_MUSE|OLLAMA_LOCAL",
  "session_id": "...",
  "agent": "...",
  "task_id": "TASK-0001",
  "model": "...",
  "tier": "T0|T1|T2|T3|T4",
  "input_tokens": 0,
  "output_tokens": 0,
  "cache_read_tokens": 0,
  "cache_write_tokens": 0,
  "context_fill_pct": 0,
  "latency_ms": 0,
  "cost_or_usage_estimate": "...",
  "measurement": "MEASURED|ESTIMATED",
  "estimation_method": "..."
}
```

### 9.6 Additions to the phase deliverables

- **Phase 1 adds:** the measurement points and plan limits actually found per environment (with sources, and what could not be verified); Governor and Router designs; initial budgets and thresholds; a draft model registry; the routing matrix with tiers and floors; a fourth Mermaid diagram of the usage → context → routing control loop; the token-saving strategy with expected savings labeled as estimates; and metering/routing/observability candidates in the Section 2A adoption matrix.
- **Phase 2 adds:** the usage ledger, hooks/scripts, thresholds, routing config and the first usage report.
- **Phase 3 adds tests for:** simulated context overflow and session rotation with a state-continuity check; soft and hard budget limits; reserve protection for critical tasks; escalation on schema failure; privacy blocking; provider rate-limit fallback; quality equivalence before/after an optimization; ledger accuracy against platform-reported usage.
- **Acceptance metrics (targets to confirm in Phase 1):** no session reaches its hard context limit unplanned; zero state loss across rotations in tests; usage attributed to an agent for at least 95% of measurable calls; a measured token reduction on golden tasks with zero acceptance-criterion regressions; zero critical tasks routed below their floor.
