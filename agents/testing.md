# Testing: developer + testers loop and its memory

Moved word for word from PROMPT v1, sections 5 (2026-10-18). Loaded on demand by `PROMPT.md` Section 9. Section numbers inside are v1's.

## 5. Continuous coordination and developer/tester memory

The orchestrator must ask for/produce status updates whenever a task reaches a milestone, changes assumptions, fails, is blocked, needs approval, or hands off—not on an arbitrary noisy timer. Each update should show: task ID; owner; status; latest artifact hash; what changed; evidence; tests passed/failed/not run; dependencies; blocker; next action; expected recipient; cost/token/latency; and approval need.

Mandatory example: Developer modifies a feature. Tester A checks unit/specification behavior; Tester B checks integration, persistence and workflow transitions; Tester C attempts adversarial cases and regression. A deterministic runner stores exact commands, test IDs, software versions, exit status, raw results and timestamps. When any test fails, create a linked defect and route a reproducible report to the developer. After the fix, rerun the failed tests and impacted tests, preserve the old failure record, and append the new result with the new version/hash. Any coverage not run remains `NOT_TESTED`; unavailable external service is `BLOCKED`; a model’s verbal assurance is not evidence. Set retry limits and escalate persistent failure.

On restart or switching environments, the first operation is to read the latest checkpoint, task ledger, open defects, approvals, evidence references and model-routing results. Continue from the next validated action; do not reconstruct or assume state from chat memory.
