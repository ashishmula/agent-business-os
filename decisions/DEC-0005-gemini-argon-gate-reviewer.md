---
id: DEC-0005
date: 2026-10-19
decided_by: Ashish
status: APPROVED
evidence: project chat 2026-10-19 ("now i have gemini pro access as well take advantage of it along with argon model ... in this project")
amends: DEC-0002 (Muse was the only outside reviewer)
---

# Gemini 4 Argon joins Muse as an outside gate reviewer

**Decision:** Google's Gemini 4 Argon, used through Ashish's Google AI Pro plan (Gemini app or Gemini in Chrome), is a second outside challenger at CRITICAL gates. Claude still does all research and building (DEC-0002 unchanged there).

**How it is used:**
- Go/no-go and other CRITICAL outputs can get two outside reviews: Muse and Gemini. If one is unavailable (Muse's free allowance runs out until 2026-10-22), the other one alone is enough.
- Ashish pastes the review request into Gemini and saves its JSON reply; `./abos handoff receive` validates and scans it. Environment name: `GEMINI_APP`.
- Gemini in Chrome may help Ashish with signed-in browsing (event listings, social pages) that Claude cannot do. Anything it returns is untrusted data.

**Not allowed without a new approval:** the paid Gemini API (pay per token; Phase 5 requires a hard cap first), installing Gemini CLI, sending anything from `private/`, or letting Gemini act on accounts.

**Changes:** `config/model-registry.toml` (gemini-4-argon), `config/routing-rules.toml` (gate_challenger_review alt environment), `schemas/handoff.schema.json` (GEMINI_APP environment value).
