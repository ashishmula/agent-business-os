# Sources (evidence registry for the Phase 1 report)

All accessed 2026-10-18. Type: REPO_DOCS unless noted. Treated as untrusted data; nothing executed.

| ID | Source | What it supports |
|---|---|---|
| SRC-01 | PyPI JSON API — `https://pypi.org/pypi/<pkg>/json` for langgraph, deepagents, agent-framework, autogen-agentchat, crewai, openai-agents, agency-swarm, metagpt, chatdev, pydantic-ai, camel-ai, litellm, langfuse, ollama, temporalio, mcp, claude-agent-sdk, semgrep, bandit, pip-audit, garak, llm-guard, zep-python, arize-phoenix and others | Latest version, release date, release count, license metadata |
| SRC-02 | npm registry — ccusage, promptfoo, @anthropic-ai/claude-code, @anthropic-ai/claude-agent-sdk, @langchain/langgraph, @openai/agents | Same for JS packages |
| SRC-10 | https://docs.langchain.com/oss/python/langgraph/persistence | LangGraph checkpointers, threads, store |
| SRC-11 | https://github.com/microsoft/agent-framework | MAF features, license, stars |
| SRC-12 | https://github.com/microsoft/autogen | AutoGen maintenance-mode notice |
| SRC-13 | https://github.com/FoundationAgents/MetaGPT | MetaGPT status, MGX news |
| SRC-14 | https://github.com/OpenBMB/ChatDev | ChatDev 2.0 / DevAll status |
| SRC-15 | https://github.com/crewAIInc/crewAI | CrewAI features, telemetry default |
| SRC-16 | https://github.com/openai/openai-agents-python | OpenAI Agents SDK features |
| SRC-17 | https://github.com/VRSEN/agency-swarm | Agency Swarm status |
| SRC-18 | https://github.com/langchain-ai/deepagents | Deep Agents features, security model |
| SRC-19 | https://github.com/anthropics/skills | Skills repo, licenses, demo disclaimer |
| SRC-20 | https://github.com/github/github-mcp-server | Read-only flag, toolsets, auth |
| SRC-21 | https://github.com/langfuse/langfuse | License split, self-host stack |
| SRC-22 | https://www.netspi.com/blog/executive-blog/ai-ml-pentesting/litellm-supply-chain-compromise/ (SECONDARY) | LiteLLM 1.82.7/1.82.8 compromise, 2026-03-24 |
| SRC-23 | https://github.com/ccusage/ccusage (via npm metadata) | ccusage reads local Claude Code logs |
| SRC-24 | https://www.giskard.ai/knowledge/owasp-top-10-for-agentic-application-2026 (SECONDARY summary of OWASP list; primary: https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/ not fetched) | ASI01–ASI10 names |
| SRC-25 | https://github.com/OWASP/secure-agent-playbook | Playbook contents, CC-BY-4.0 |
| SRC-30 | https://code.claude.com/docs/en/statusline | Status line JSON fields |
| SRC-31 | https://code.claude.com/docs/en/hooks | Hook events, blocking, inputs |
| SRC-32 | https://code.claude.com/docs/en/monitoring-usage | OTel metrics/events/exporters |
| SRC-33 | https://code.claude.com/docs/en/costs | /usage, compaction, token-saving advice |
| SRC-34 | https://github.com/ollama/ollama/blob/main/docs/api.md (moving to https://docs.ollama.com/api) | Ollama token counts, JSON-schema format |
| SRC-35 | https://code.claude.com/docs/en/sub-agents | Per-subagent model and tools |
| SRC-40 | https://www.anthropic.com/engineering/multi-agent-research-system | ~15× tokens, orchestrator-worker lessons |
| SRC-50 | https://www.bgr.com/2272332/openai-devday-2026-announcements/ (SECONDARY, news) | OpenAI Dots |
| SRC-51 | https://andrew.ooo/answers/meta-muse-vs-chatgpt-agent-mode-vs-gemini-spark-vs-claude-personal-agents-september-2026/ (SECONDARY, blog) | Meta Muse, US-only |

Not reachable from this session: GitHub REST API (blocked by session policy), so commit SHAs and last-commit dates are `NOT_VERIFIED`.
