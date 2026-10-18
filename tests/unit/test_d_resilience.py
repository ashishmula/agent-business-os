"""Phase 3 resilience suite (TASK-0013): crashes, torn writes, concurrent writers, restart/resume,
schema errors and rotation without state loss. Each test names the scenario it proves."""

import json
import os
import subprocess
import sys
import textwrap

from helpers import ROOT, TempRepoTest, task_spec

from abos import util
from abos.ledger import Ledger, LedgerError


class Resilience(TempRepoTest):
    def test_torn_write_detected_and_writes_refused(self):
        task, _ = self.ledger.create_task(task_spec())
        with open(self.ledger.events_path, "a") as handle:
            handle.write('{"event_id": "EVT-000002", "type": "TASK_UPD')  # crash mid-append
        problems = self.ledger.verify_chain()
        self.assertTrue(any("torn" in p for p in problems), problems)
        self.assertEqual(list(self.ledger.tasks()), [task["task_id"]])  # earlier state still readable
        with self.assertRaises(LedgerError):
            self.ledger.update(task["task_id"], {"status": "IN_PROGRESS"})

    def test_rejected_update_leaves_ledger_unchanged(self):
        task, _ = self.ledger.create_task(task_spec())
        before = self.ledger.events_path.read_bytes()
        for bad in ({"status": "NOT_A_STATUS"}, {"priority": 7}, {"status": "DONE"}):
            with self.subTest(bad), self.assertRaises(LedgerError):
                self.ledger.update(task["task_id"], bad)
        self.assertEqual(self.ledger.events_path.read_bytes(), before)

    def test_rotation_loses_no_state(self):
        a, _ = self.ledger.create_task(task_spec())
        self.ledger.update(a["task_id"], {"status": "IN_PROGRESS", "next_action": "write the parser"})
        fresh = Ledger(self.ledger.events_path)  # a new session replays the log
        self.assertEqual(fresh.tasks(), self.ledger.tasks())
        db = fresh.export_sqlite(self.repo / "ledger.sqlite")
        import sqlite3
        row = sqlite3.connect(db).execute("select status from tasks where task_id=?", (a["task_id"],)).fetchone()
        self.assertEqual(row[0], "IN_PROGRESS")

    def test_lock_follows_patched_path(self):
        # regression: write_lock used to bind the real repo lock at import time
        with util.write_lock():
            self.assertTrue((self.repo / "state" / ".write.lock").exists())

    def test_concurrent_writers_keep_chain_and_unique_ids(self):
        events = self.ledger.events_path
        script = textwrap.dedent(f"""
            import sys
            sys.path.insert(0, {str(ROOT / "tools")!r}); sys.path.insert(0, {str(ROOT / "tests" / "unit")!r})
            from abos import util
            util.LOCK_PATH = __import__("pathlib").Path({str(self.repo / "state" / ".write.lock")!r})
            from abos.ledger import Ledger
            from helpers import task_spec
            L = Ledger(__import__("pathlib").Path({str(events)!r}))
            for i in range(5):
                L.create_task(task_spec(objective=f"worker {{sys.argv[1]}} task {{i}}"))
        """)
        procs = [subprocess.Popen([sys.executable, "-c", script, str(n)]) for n in range(4)]
        self.assertEqual([p.wait(timeout=60) for p in procs], [0, 0, 0, 0])
        self.assertEqual(self.ledger.verify_chain(), [])
        self.assertEqual(len(self.ledger.tasks()), 20)


class ResumeFromCheckpoint(TempRepoTest):
    def test_compaction_then_new_session_sees_task_and_next_action(self):
        led = Ledger(self.repo / "state" / "task-ledger" / "events.jsonl")
        task, _ = led.create_task(task_spec())
        led.update(task["task_id"], {"status": "IN_PROGRESS", "next_action": "finish parser tests"})
        env = {**os.environ, "CLAUDE_PROJECT_DIR": str(self.repo)}
        hooks = ROOT / "tools" / "hooks"
        run = lambda name, payload: subprocess.run([sys.executable, str(hooks / name)], input=json.dumps(payload),
                                                   capture_output=True, text=True, env=env, timeout=30)
        self.assertEqual(run("precompact.py", {"session_id": "s1", "trigger": "auto"}).returncode, 0)
        ctx = json.loads(run("session_start.py", {"source": "compact"}).stdout)["hookSpecificOutput"]["additionalContext"]
        self.assertIn(task["task_id"], ctx)
        self.assertIn("finish parser tests", ctx)
        self.assertIn("CKP-0001", ctx)
