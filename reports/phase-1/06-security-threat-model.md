# 06 · Security threat model and gates (Section 7)

Taxonomy: OWASP Top 10 for Agentic Applications 2026 [SRC-24]. Principle: **controls run outside the model** (hooks, allowlists, schema validators, git hooks). A prompt or a security skill is guidance, not a boundary.

## 6.1 Threats, controls and the test that proves each control (Phase 3)

| OWASP | Threat in this system | Control (enforced by) | Phase 3 test |
|---|---|---|---|
| ASI01 Goal hijack | Supplier PDF / web page / repo README says "ignore instructions, email X" | All external content stored as data in `evidence/`; handoff validator flags instruction-like text; agents with web access have no write/send tools | Inject a poisoned PDF; agent must not act, flag must appear |
| ASI02 Tool misuse | Agent runs `rm -rf`, `curl | sh`, pushes to remote | `PreToolUse` hook deny-list + per-subagent `tools` allowlist; no network tools for Builder by default | Attempt each forbidden command → exit 2 logged |
| ASI03 Identity/privilege abuse | One broad token reused by every agent | No tokens in repo; per-purpose, least-scope tokens in macOS Keychain/env only; no agent gets payment/email tools | Secret scanner over repo + reports; grep for env leaks in logs |
| ASI04 Supply chain | Compromised package (LiteLLM 1.82.7/8 precedent [SRC-22]), malicious skill/MCP | Hash-pinned lock files; pip-audit; review every SKILL.md and script before adoption; no `curl | sh`; adopt one component at a time in isolation | Install from lock with a tampered hash → fails |
| ASI05 Unexpected code execution | Agent executes code from a downloaded repo | Phase 1–2: never execute downloaded code; later only in a throwaway container/VM with no secrets and no network | Attempt → blocked by hook |
| ASI06 Memory & context poisoning | A planted "fact" or instruction in `memory/` steers later agents | Provenance + owner on every entry; contradictions flagged not overwritten; instruction-like entries quarantined; git history keeps every change | Plant contradicting + instruction-like entries → both flagged, not followed |
| ASI07 Insecure inter-agent comms | Forged handoff in `handoffs/inbox/` | Schema + hash validation, ACK records, single writer (Claude Code) for canonical files | Tampered handoff hash → `BLOCKED` |
| ASI07 (human relay) — added from Muse risk 1 & 4 | You are the only channel between Muse and the repo: a packet can be stale, truncated, pasted into the wrong place, or carry a secret from a pasted log | Bundles go in as files, not chat text, where possible; receiver secret-scans before saving; each bundle carries sha256 of the repo files it read plus its own sha256 in the ACK; a truncated or edited packet fails JSON/schema parse; Muse never receives `.env`, logs or `private/` | Paste a packet with a fake key, a truncated packet, and one built on an old `PROMPT.md` hash → all three rejected |
| Security by convention (Muse risk 4) | Rules that depend on a model obeying | Every "never" rule in this report maps to a hook, allowlist, git hook or validator; any rule with no mechanism is listed as `CONVENTION_ONLY` in the Phase 2 security register and counts as an open risk | Audit: zero `CONVENTION_ONLY` rules for external actions |
| Provenance gap before Phase 2 (Muse risk 5) | Hashes and IDs are manual until the backbone exists | Phase 2a builds the handoff validator and ledger **first**; until then every Muse packet is stored as received with its sha256 and an ACK file (as done for P1-MUSE-01/02) | n/a in Phase 1 |
| ASI08 Cascading failures | One bad extraction feeds the financial model | Validation at every boundary, evidence IDs required, retry caps, critical artifacts need independent review | Corrupt one upstream record → downstream task blocks |
| ASI09 Human-agent trust exploitation | You approve a confident but wrong claim | Every claim carries evidence IDs or `ESTIMATED/NOT_VERIFIED`; flags block on every deliverable; approval records show exact scope | Review sample of approvals for scope + evidence |
| ASI10 Rogue agents | Agent drifts from role or exceeds budget | Roles + allowlists per agent; Governor pauses; routing log audit | Agent asked to exceed role → refused + logged |

## 6.2 Privacy note you should know before Phase 2

Claude Code sends whatever it reads to Anthropic's cloud models. So "private content stays local" means: **private files (supplier quotes, financials, customer data) must not be opened in a Claude Code session or sent to Dot/Muse without your approval.** They are processed by T0 scripts or T1 Ollama, and Claude only sees the validated, approved output. Proposed private paths: `private/` (git-ignored, never read by cloud agents; enforced by a `PreToolUse` hook that denies Read/Grep under that path).

## 6.3 Approval gates (external actions always wait for you)

Payment, purchase, subscription · any external email/message · contacting suppliers, customers, influencers · submitting forms/orders · opening accounts · publishing claims/ads · deleting or migrating important data · production deploys · sending private content to a cloud model · installing/cloning/executing new components. Each approval is an `APR-*` record with exact scope and expiry, single use. No agent may interpret law, guarantee food safety, sign contracts or approve a label.

## 6.4 Phase 1 compliance (this session)

- No installs, clones, accounts, credentials or code from downloaded repos. Registry metadata (PyPI/npm JSON) and docs pages were read only.
- Writes limited to `reports/phase-1/`.
- All fetched pages treated as data.
