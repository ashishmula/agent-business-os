# 02 · Skills, MCP, security, metering and eval adoption matrix (Section 2A)

Checked 2026-10-18. Nothing here was installed, cloned or executed. "Pin" means the exact version/commit to record **at adoption time in Phase 2**; where a value is shown it is the latest registry release seen today, not yet a reviewed pin.

Class key: **FW** framework · **SK** skill · **TL** tool/MCP server · **SEC** security enforcement or utility · **OBS** metering/observability · **EVAL** testing/evaluation · **DOC** reference standard.

Decision key: `ADOPT` use as-is after Phase 2 isolation test · `ADAPT` use parts, reviewed and copied into our repo · `REJECT` · `INVESTIGATE FURTHER` · `NOT_NOW` (parked with reason, revisit at each gate).

## Selected set (the smallest that covers every need)

| Candidate | Class | Decision | Link | Intended agent / task | Permissions needed | Pin (seen today) | Acceptance test (Phase 2/3) | Monitoring | Fallback | Rollback |
|---|---|---|---|---|---|---|---|---|---|---|
| Claude Code status line JSON | OBS | **ADOPT** | [docs](https://code.claude.com/docs/en/statusline) | Governor: context %, 5h/7d plan usage, cost per session | Runs a local script; no network | Claude Code 2.1.302 | Mock JSON → ledger row with correct fields; real session row matches `/usage` | Ledger row count per session | Parse transcript JSONL | Remove `statusLine` from settings |
| Claude Code hooks | SEC + OBS | **ADOPT** | [docs](https://code.claude.com/docs/en/hooks) | Enforcement (PreToolUse deny-list, approval gate), checkpoint on PreCompact, usage capture on Stop/SubagentStop | Local scripts only | same | Blocked command returns exit 2 and is logged; PreCompact writes checkpoint | Hook error log | Manual checklist | Remove hook entries |
| Claude Code OpenTelemetry | OBS | **ADOPT** (console/file first) | [docs](https://code.claude.com/docs/en/monitoring-usage) | Per-request `claude_code.api_request` tokens, `token.usage` by type and model | Env vars only; local exporter | same | Totals within 2% of `/usage` for a test session | Exporter errors | Status line + ccusage | Unset env vars |
| Claude Code subagents | FW (runtime) | **ADOPT** | [docs](https://code.claude.com/docs/en/sub-agents) | Specialist agents with per-agent `model`, `tools` allowlist | Per-agent allowlist | same | Agent with `tools: Read, Grep` cannot Write | Routing log | Single session | Delete agent file |
| LangGraph core + SQLite checkpointer | FW | **ADOPT** (when first needed) | [repo](https://github.com/langchain-ai/langgraph) · [persistence](https://docs.langchain.com/oss/python/langgraph/persistence) | Durable workflows, resume after crash, HITL interrupt | Python venv, local SQLite file | `langgraph` 1.2.16 | Kill mid-run → resume at same step; interrupt waits for approval | Checkpoint table growth | Microsoft Agent Framework | Pin previous lock file |
| Ollama REST API (+ `ollama` py client) | TL | **ADOPT** | [API](https://docs.ollama.com/api) | T1 local extraction/classification; metering via `prompt_eval_count`, `eval_count`, durations | localhost:11434 only | `ollama` py 0.6.3 | Schema-valid JSON via `format` schema on 20 golden items | Tokens/sec, failures | Escalate to T2 | n/a (read-only API) |
| ccusage | OBS | **ADOPT** (offline mode) | [repo](https://github.com/ccusage/ccusage) | Daily/weekly roll-ups from local Claude Code JSONL | Read `~/.claude` logs | npm 20.0.35 (2026-10-17) | Daily totals match OTel totals; **verify it makes no network call in offline mode** (`NOT_VERIFIED`) | Run log | OTel roll-up script | Uninstall |
| jsonschema + SQLite (stdlib) + pytest | EVAL / T0 | **ADOPT** | PyPI | Schema validation of every handoff/ledger record; golden-task runner | Local | at adoption | Invalid record rejected; golden tasks run | Test results folder | — | — |
| gitleaks or `detect-secrets` (pre-commit) | SEC | **ADOPT** (pick one after review) | [gitleaks](https://github.com/gitleaks/gitleaks) | Block commits containing keys/tokens | Local git hook | `NOT_VERIFIED` (GitHub blocked here) | Fake key in a commit is blocked | Hook log | Manual grep | Remove hook |
| pip-audit + uv lock with hashes | SEC | **ADOPT** | [repo](https://github.com/pypa/pip-audit) | Dependency CVE check; hash-pinned installs | Local | `pip-audit` 2.10.1 | Known-vuln test package flagged | CI/test log | OSV web check | — |
| Semgrep CE / Bandit | SEC | **ADOPT** (Bandit first, Semgrep in Phase 3) | [semgrep](https://github.com/semgrep/semgrep) · [bandit](https://github.com/PyCQA/bandit) | Static scan of our own scripts | Local | semgrep 1.181.0 (LGPL-2.1+) · bandit 1.9.4 | Seeded `subprocess(shell=True)` flagged | Scan report | Code review | — |
| OWASP Top 10 for Agentic Applications 2026 | DOC | **ADOPT** (threat taxonomy) | [OWASP](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) | Threat model rows ASI01–ASI10 | none | 2026 edition | Each ASI has ≥1 control + ≥1 test | Threat model review per gate | — | — |
| OWASP secure-agent-playbook | SK + DOC | **ADAPT** | [repo](https://github.com/OWASP/secure-agent-playbook) | Copy reviewed plays (agent security audit, MCP server review, prompt-injection testing, threat modeling) into `/agents/security-reviewer/` | Read-only use | commit `NOT_VERIFIED` | Play produces filled template on our repo | Review log | Our own checklist | Delete copied files |
| anthropics/skills | SK | **ADAPT** (only `xlsx`, `pdf`, `skill-creator`) | [repo](https://github.com/anthropics/skills) | Financial model workbook, supplier PDF extraction, writing our own skills | Skill reads/writes files in repo | commit `NOT_VERIFIED` | Review every SKILL.md + scripts; run on sample file in a scratch dir | — | Manual scripts | Remove plugin |

## Investigated, not selected now

| Candidate | Class | Decision | Link | Reason / evidence | Revisit when |
|---|---|---|---|---|---|
| GitHub MCP server | TL | INVESTIGATE FURTHER | [repo](https://github.com/github/github-mcp-server) | MIT, official, `--read-only` flag and toolset allowlist exist [SRC-20]. Claude Code docs say CLI tools like `gh` are more context-efficient than MCP [SRC-33]. Only useful if the repo lives on GitHub (blocking Q4). If adopted: remote server, `--read-only`, `repos,issues,pull_requests` toolsets, fine-grained token scoped to this one repo. | Repo pushed to GitHub |
| LiteLLM (gateway/router/budgets) | TL / OBS | **REJECT** for now | [repo](https://github.com/BerriAI/litellm) | Native Claude Code model settings + Ollama API cover routing. PyPI 1.82.7 and 1.82.8 were **compromised on 2026-03-24** with a credential-stealing payload [SRC-22]. If ever needed: official Docker image pinned by digest, no host secrets mounted. | A second cloud provider is approved |
| Langfuse | OBS | INVESTIGATE FURTHER | [repo](https://github.com/langfuse/langfuse) | MIT except `ee` folders; self-host uses ClickHouse + Redis, heavy for a MacBook Air [SRC-21]. SQLite ledger + generated HTML report meets Section 9.6 first. | Ledger proves insufficient |
| OpenTelemetry → Prometheus + Grafana | OBS | NOT_NOW (optional after approval) | [docs](https://code.claude.com/docs/en/monitoring-usage) | Claude Code supports `prometheus` metrics exporter natively [SRC-32]. Good learning bridge to Grafana, but not needed for the gate. | Phase 3 dashboard |
| Arize Phoenix | OBS | REJECT | PyPI | Elastic-2.0 license; overlaps Langfuse/ledger. | — |
| promptfoo | EVAL | INVESTIGATE FURTHER | [repo](https://github.com/promptfoo/promptfoo) | MIT, active (0.124.1, 2026-10-08). Candidate for Phase 3 prompt-injection red-team suite. | Phase 3 |
| garak (NVIDIA) | EVAL / SEC | INVESTIGATE FURTHER | PyPI 0.17.1 | LLM vulnerability scanner; useful against the local Ollama models. | Phase 3 |
| inspect-ai / deepeval / ragas | EVAL | NOT_NOW | PyPI | Overlap with pytest golden tasks; add only if pytest harness is not enough. | Phase 3 |
| Guardrails AI / NeMo Guardrails / LLM Guard | SEC | NOT_NOW | PyPI | In-model guardrails are not a security boundary (Section 2A); `llm-guard` last release 2025-05. Enforcement lives in hooks and allowlists. | If an unattended public-facing agent is built |
| mem0 / Letta / Zep | TL (memory) | REJECT | PyPI | Section 10 wants canonical, version-controlled memory in the repo. External memory stores duplicate it and add a poisoning surface. `zep-python` last release 2024-09. | — |
| Temporal | FW | REJECT for now | PyPI `temporalio` 1.34.0 | Excellent durable execution but needs a server cluster; LangGraph SQLite covers our scale. Familiar to a backend dev, so a valid Phase 5+ option. | Volume grows |
| CrewAI, AutoGen, MetaGPT, ChatDev, Agency Swarm, OpenAI Agents SDK | FW | REJECT | see [01](01-framework-scorecard.md) | Scored below the primary/fallback. | — |
| Deep Agents | FW | NOT_NOW | [repo](https://github.com/langchain-ai/deepagents) | Duplicates Claude Code harness. | Need for unattended agent outside Claude Code |
| MCP Python SDK (`mcp` 2.3.0) | TL | NOT_NOW | PyPI | Only if we write our own MCP server (e.g. exposing the ledger read-only to Dot/Muse). | Dot/Muse gains MCP client support |
| Apify MCP (already connected on your device) | TL | INVESTIGATE FURTHER | — | Web scraping for Phase 4 research; scraped pages are untrusted input; costs money per run → needs approval and budget. | Phase 4 |
| Desktop Commander (already connected on your device) | TL | Keep out of project agents | — | Broad shell and filesystem access on the Mac; violates least privilege for specialist agents. | — |

## Environment compatibility notes

- **Skills** (`SKILL.md` folders) load natively in Claude Code only. Dot/Muse and Ollama cannot load them. Equivalent: the same instructions exported as a plain Markdown "play" inside a handoff bundle, reviewed once and versioned (Section 2A "adapter, not pretending").
- **MCP servers** work in Claude Code. Whether OpenAI Dots or Meta Muse can call a custom MCP server is `NOT_VERIFIED`; plan on file handoffs.
- **Security enforcement** (hooks, allowlists, pre-commit) is code outside the model. A security *skill* only guides a review; it never replaces these.
