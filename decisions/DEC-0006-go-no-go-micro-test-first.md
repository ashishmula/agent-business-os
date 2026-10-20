# DEC-0006: Go/no-go answer is "micro-test first"

- Date: 2026-10-20
- Decided by: Ashish (R10 "You choose" gate). He said "proceed further with your research and building" while the go/no-go card was open; Claude took that as the recommended option and said so in the thread. Ashish can still change it.
- Status: Accepted (recorded by Claude from that message)

## Decision
Run the cheap demand test before spending real money: an optional step 0 (waitlist page + small Toronto ad test, CAD 300-600), then the micro-test (2-3 events with free samples, about CAD 2,500-4,100). The best plan (custom can) is no-go today. The budget plan (powder within CAD 15k) waits for the micro-test result.

## Why
- R10 recommendation, confirmed by the Gemini 4 Argon outside review (R10 section 11, TASK-0038).
- No audience yet and only one sober dance date in the next 90 days, so demand is the biggest unknown.

## What it does not allow
Phase 4 is still desk research (APR-0005). Publishing the page, running ads, buying samples, booking events or contacting organizers each need a new approval (draft: reports/phase-4/micro-test-kit/APR-request.md).

## Pass/fail
Thresholds live in config/microtest.toml and are scored by `./abos microtest <tally.csv>`. A gate with no data is NOT_TESTED, never PASS.
