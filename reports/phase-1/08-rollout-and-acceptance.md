# 08 · Phased rollout, acceptance metrics and key assumptions

## 8.1 Rollout

| Phase | Scope | Exit gate (your approval) |
|---|---|---|
| **1** (this report) | Research and architecture only | Approve stack, structure, schemas; answer blocking questions |
| **2a** Backbone | **First:** handoff validator + secret scan for incoming bundles (closes Muse's provenance gap). Then: approved folder structure; schemas; SQLite task ledger + pre-flight + status board scripts; handoff validator; `.gitignore` for `private/`; secret-scan pre-commit | Status board generated from a real ledger; validator rejects bad handoff |
| **2b** Governor + Router | Status line script → usage ledger; Stop/SubagentStop/PreCompact/SessionStart hooks; OTel to local file; budgets.yaml, routing-rules.yaml, model-registry.yaml; first usage report | First daily usage report with ≥95% attribution |
| **2c** Agents | Subagent files (Builder, Testers A/B/C, Security Reviewer) with allowlists; LangGraph workflow for the developer+3-testers loop | One feature taken through the full loop with stored evidence |
| **2c′** Ollama (optional) | Capacity check, then golden tasks. Skipped and recorded `NOT_NOW` if the Mac can't run a useful model; the system stays two-environment | T1 golden tasks pass, or deferral recorded |
| **2d** Muse lane | First research handoff bundle round-trip (R1 scoping only), batched to respect Muse's budget | Bundle validated and ACKed |
| **3** Tests | Restart/resume, failure recovery, permissions, prompt injection, source integrity, routing, schema errors, cost caps, memory poisoning, duplicate/delta/stale, NOT_NOW not executed | Published pass/fail/NOT_TESTED counts and coverage gaps |
| **4** Business validation | Section 7 plan + portfolio pipeline | Quantified go/no-go. This is the real money gate (Muse risk 5): it is judged only on Phase 4 evidence, and Phase 1–3 effort is never an argument for "go" |
| **5** Execution | Each external action separately approved | Per action |

Each adopted component: isolated test → pin exact version/commit → least-privilege check → functional/security/eval tests → rollback noted.

## 8.2 Acceptance metrics (targets to confirm)

| Metric | Target |
|---|---|
| Sessions hitting hard context limit unplanned | 0 |
| State loss across rotations in tests | 0 |
| Measurable calls attributed to an agent | ≥ 95% |
| Golden-task token reduction after optimizations | measured > 0 with 0 acceptance regressions |
| Critical tasks routed below floor | 0 |
| Handoffs accepted without schema/hash validation | 0 |
| Secrets found in repo/reports/memory | 0 |
| External actions without an approval record | 0 |
| Duplicate tasks re-run instead of reused (Phase 3 test) | 0 |
| Governor/Router own LLM tokens | < 5% of total (ESTIMATED target) |

## 8.3 Key assumptions

| Assumption | Confidence | Why |
|---|---|---|
| The git repo on your Mac is the only canonical store | high | Only environment with verified version control |
| No shared folder or API exists between Claude Code and Muse | high | Confirmed by Muse (P1-MUSE-02 risk 1) |
| Ollama is installed (`~/.ollama` exists) | medium | Folder seen, binary/models not checked |
| T1 local tier may not be usable on this Mac | medium | Muse reports M1/8 GB (unverified); design now works without T1 |
| Claude Pro plan | high | Ashish, 2026-10-18 |
| GTA is home base; target markets chosen by evidence in Phase 4 | high | Ashish, 2026-10-18 |
| Portfolio cash cap CAD 10–15k; free tools first | high | Ashish, 2026-10-18 |
| One person operates the system; low ops tolerance | high | Brief + context |
| Merged status vocabulary (5.2) is acceptable | medium | Sections 4 and 6A lists differ |
