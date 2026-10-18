# TASK-0012 Developer + 3 testers loop (feature: TASK-0018 `./abos phase-report`)

Status: DONE. The feature went through builder, tester-a, tester-b and tester-c in 3 rounds on a separate
git worktree (`p3-devloop`), each role as a real Claude Code subagent (Sonnet) started with `claude -p` on
Ashish's Mac under the reviewed settings. Raw outputs: `test-results/devloop/` (cost USD 4.07 in total, list
prices, counted against the Pro plan).

## Rounds

| Round | Role | Verdict | Evidence |
|---|---|---|---|
| 1 | builder | built `tools/abos/phasereport.py`, CLI, 4 tests | r1-builder.json, TEST-20261018045624 |
| 1 | tester-a | 5/5 acceptance criteria PASS, 8 spec tests | r1-tester-a.json, TEST-20261018045707 |
| 1 | tester-b | integration PASS; RUNBOOK row missing (FAIL) | r1-tester-b.json |
| 1 | tester-c | 4 defects: `--write` could write anywhere (incl. through symlinks), no ledger integrity check, raw tracebacks, forged test-record text rendered as report lines | r1-tester-c.json |
| 2 | builder | fixed all round-1 defects + RUNBOOK row, regression tests | r2-builder.json, TEST-20261018050222 |
| 2 | tester-c | round-1 defects fixed; 2 new medium ones: forged test records trusted, links/HTML rendered | r2-tester-c.json |
| 3 | builder | records trusted only with matching log hash, valid date, PASS/FAIL; all echoed fields escaped; `--force` keeps file mode | r3-builder.json, TEST-20261018051247 |
| 3 | tester-c | mode FIXED; records and markdown PARTIAL (a PASS record could point at a real log while saying exit 1; bare URLs print as text) | r3-tester-c.json |
| close | orchestrator | record must agree with its exit_status; test added | TEST-20261018051618 (141 tests, PASS) |

Testers reported 9 defects in round 1 (all fixed), 5 in round 2 (3 fixed; no backup on `--force` and a `ledger add` traceback accepted as low) and 2 partials in round 3 (1 fixed; bare `http://` text that some viewers auto-link accepted as low). 13 fixed in total.

## What the loop itself taught us

- **It works and is worth it:** tester-a passed every acceptance criterion in round 1, yet tester-c found
  4 real defects. Spec tests alone would have shipped a command that could overwrite any file.
- **Role boundary slipped once:** in round 2 the builder edited two of tester-a's tests (they wrote outside
  `reports/`, which the fix now forbids). Reasonable change, wrong owner. Next time the builder must report
  it and tester-a must make the edit.
- **Tester-c needs a ready copy:** in round 2 its own `cp`/`tar` of the repo was denied, so it only read the
  code. Giving it a disposable copy as its working folder fixed that. One run also ended in an API error
  and was re-run.
- **Tester-c touched a real report in its copy** (overwrote then restored `adversarial-suite.md`). It was a
  copy, so no harm, but tester prompts must say "create your own files under reports/tmp-*".

## Known limits (NOT_TESTED or accepted)

- Test records are unsigned: anyone who can write the repo can forge a record with a real log. Same limit as
  the ledger itself (hash chain, not signatures).
- A ledger truncated at the end still passes the chain check (design limit, known from TASK-0013).
- `clean_md` turns `_` into `?` in objectives (cosmetic: "NOT?TESTED").
- `--force` keeps no backup; `ledger add` with a huge spec argument shows a traceback (outside this feature).
