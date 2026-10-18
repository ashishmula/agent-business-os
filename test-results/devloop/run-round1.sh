#!/bin/zsh
cd /Users/ashishmula/abos-devloop
out=/Users/ashishmula/abos-devloop-out
common="Work only inside this folder. Do not commit, push, install packages or change the ledger status of any task."
run() { # role prompt
  claude -p "$2" --settings .claude/settings.json --allowedTools "Bash,Read,Edit,Write,Glob,Grep,Task,Agent" --output-format json < /dev/null > $out/$1.json 2> $out/$1.err
  echo "$1 exit=$?" >> $out/progress.txt
}
run builder "Use the builder subagent for TASK-0018 (read it with ./abos ledger show TASK-0018). Implement ./abos phase-report <gate> [--write PATH] in a new module tools/abos/phasereport.py wired into tools/abos/__main__.py, with a small unit test in tests/unit/test_b_phasereport.py. Then run ./abos test. $common Reply with: files changed, test_id, NOT_TESTED items."
run tester-a "Use the tester-a subagent on TASK-0018 (./abos ledger show TASK-0018). The builder has implemented ./abos phase-report in tools/abos/phasereport.py. Write spec tests in tests/unit/test_a_phasereport.py covering each acceptance criterion, run ./abos test, and report PASS/FAIL/NOT_TESTED per criterion with test names and the test_id. $common"
run tester-b "Use the tester-b subagent on TASK-0018. Check ./abos phase-report integrates with the rest of the system: run ./abos test, ./abos ledger verify, ./abos phase-report G2-phase-3 and compare its counts with ./abos ledger list by hand, and check RUNBOOK.md or CLAUDE.md mention it if they should. Report item, PASS/FAIL/NOT_TESTED, evidence. $common"
run tester-c "Use the tester-c subagent on TASK-0018. Try to break ./abos phase-report: odd gate names (empty, very long, path-like such as ../../private, shell metacharacters), --write to paths outside the repo and into private/, a ledger with a torn last line (use a temp copy), missing test-results folder. Use a temp folder for experiments. Report each attempt with command and observed result. $common"
echo ALL_DONE >> $out/progress.txt
