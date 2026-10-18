# Phase 3 report: testing the system

Status: WAITING_FOR_APPROVAL (end of Phase 3, APR-0003). Branch `phase-2-backbone`, commits e79a9a3 → 8336037 and the
report commit after it. Nothing was merged to main, installed, bought or sent to anyone.

## Result in one line

Every Phase 3 test task is done. One CRITICAL task (the adversarial suite) is waiting for Muse's gate review. Tests found
and fixed 17 real defects, and the remaining gaps are listed below as NOT_TESTED.

## Counts (`./abos phase-report G2-phase-3`)

| Status | Tasks |
|---|---|
| DONE | 6: TASK-0011 grounding, 0012 dev+testers loop, 0013 resilience, 0015 routing/cost caps, 0016 capability scout, 0018 phase-report command |
| REVIEW | 1: TASK-0014 adversarial suite (CRITICAL, needs Muse) |
| WAITING_FOR_APPROVAL | 1: TASK-0017 this report |

Unit suite: 141 tests, 140 pass, 1 skipped (TEST-20261018051618 on the Mac). The skip means `.claude/settings.json`
is older than `config/claude-code-settings.json`. **Ashish: run `./abos install-claude` once.**
Live Claude Code runs on the Mac: 1 adversarial run (8 attacks) and 10 subagent runs in the developer loop.

## What each test found

| Task | Found and fixed | Report |
|---|---|---|
| 0013 resilience | A crash mid-write broke every ledger read. The lock path was frozen at import. | ledger notes |
| 0014 adversarial | All 7 live attacks were blocked, and planted memory was ignored. The pre-commit hook had silently stopped running because of a lost exec bit. | [adversarial-suite.md](adversarial-suite.md) |
| 0015 routing | 1056 routes had 0 below their floor. Escalating a failed script went to the disabled local tier. | ledger notes |
| 0012/0018 loop | 13 defects in the new command: writes anywhere, no ledger check, forged test records trusted, rendered links, lost file mode, and others. Spec tests alone passed it in round 1. | [dev-test-loop.md](dev-test-loop.md) |
| 0016 scout | Not a test. 15 reusable tools were shortlisted. llm-guard is archived, so its NOT_NOW becomes REJECT. | [capability-scout.md](capability-scout.md) |

## NOT_TESTED or accepted limits

- TASK-0005: status line and usage report in a live interactive session. This is the Phase 2 gate and needs one Terminal session.
- Sandbox as the second layer for home-folder writes in the Phase 3 run. The guard stopped them first; the sandbox alone blocked them in the Phase 2 live run.
- Live prompt injection from fetched web pages. Network is denied in Phase 3, so only the offline golden items cover this.
- The memory scan is pattern-based, so a reworded poisoning line can pass.
- Test records and the ledger are hash-checked, not signed, so anyone with write access to the repo can forge them.
- The router is advisory. CLAUDE.md tells agents to use it, but nothing forces a live session to obey it.

## Cost

The live Claude Code runs used USD 4.26 at list price (adversarial run 0.19, developer loop 4.07), counted against the Pro plan. No paid tools were used.

## What Ashish decides next

1. Send [P3-MUSE-04-review-request.md](P3-MUSE-04-review-request.md) to Muse once the free allowance resets (after 2026-10-22), then paste the reply here.
2. Optionally, approve trying the two free ADOPT-CANDIDATEs that replace home-made code: **gitleaks** for secret scanning and **Anthropic's security-guidance plugin**. Each would be installed only after its approval record and a read of its hooks.
3. Approve Phase 4 (business research). This needs its own approval. Recommended timing is after Muse's review, unless you want research to start in parallel.
