"""Tester B: integration, persistence and workflow transitions."""

import json
import unittest

from helpers import MUSE_01, TempRepoTest, handoff_bundle, task_spec
from abos import board, handoff
from abos.ledger import Ledger, LedgerError


class LedgerPersistence(TempRepoTest):
    def test_create_update_survive_restart(self):
        task, pre = self.ledger.create_task(task_spec())
        self.assertEqual((task["task_id"], pre["result"]), ("TASK-0001", "RUN"))
        self.ledger.update("TASK-0001", {"status": "IN_PROGRESS"})
        fresh = Ledger(self.ledger.events_path)  # simulates a new session reading from disk
        self.assertEqual(fresh.get("TASK-0001")["status"], "IN_PROGRESS")
        self.assertEqual(fresh.verify_chain(), [])

    def test_duplicate_request_is_reused_not_duplicated(self):
        self.ledger.create_task(task_spec())
        task, pre = self.ledger.create_task(task_spec(objective="build the STATUS board generator."))
        self.assertEqual(pre["result"], "REUSE")
        self.assertEqual(len(self.ledger.tasks()), 1)

    def test_done_requires_outputs_and_evidence(self):
        self.ledger.create_task(task_spec())
        with self.assertRaises(LedgerError):
            self.ledger.update("TASK-0001", {"status": "DONE"})
        self.ledger.update("TASK-0001", {
            "status": "DONE",
            "outputs": [{"artifact_id": "board", "path_or_uri": "state/status-board.md", "version_or_hash": "ab" * 32}],
            "evidence_ids": ["TEST-0001"],
        })
        self.assertEqual(self.ledger.get("TASK-0001")["status"], "DONE")

    def test_critical_needs_review_before_done(self):
        self.ledger.create_task(task_spec(risk_class="CRITICAL"))
        out = [{"artifact_id": "x", "path_or_uri": "x", "version_or_hash": "x"}]
        with self.assertRaises(LedgerError):
            self.ledger.update("TASK-0001", {"status": "DONE", "outputs": out, "evidence_ids": ["TEST-1"]})

    def test_missing_dependency_blocks_task(self):
        self.ledger.create_task(task_spec())
        task, pre = self.ledger.create_task(task_spec(objective="Second step", depends_on=["TASK-0001"]))
        self.assertEqual((pre["result"], task["status"]), ("BLOCKED", "BLOCKED"))

    def test_sqlite_export_is_queryable(self):
        import sqlite3
        self.ledger.create_task(task_spec())
        db = self.ledger.export_sqlite(self.repo / "l.sqlite")
        rows = sqlite3.connect(db).execute("SELECT task_id, status FROM tasks").fetchall()
        self.assertEqual(rows, [("TASK-0001", "NOT_STARTED")])


class HandoffToBoard(TempRepoTest):
    def test_valid_bundle_flows_to_ledger_and_board(self):
        ack = handoff.receive(self.write_bundle(handoff_bundle()), self.ledger, repo=self.repo)
        self.assertEqual(ack["result"], "ACCEPTED_WITH_WARNINGS")  # no inputs_read_sha256
        self.assertEqual(ack["checks"]["input_freshness"], "NOT_VERIFIED")
        self.assertTrue((self.repo / ack["stored_as"]).exists())
        self.assertIn(ack["ledger_task_id"], board.render(self.ledger))

    def test_real_muse_packet_accepted_with_warning(self):
        raw = MUSE_01.read_text()
        ack = handoff.receive(self.write_bundle(None, raw=raw), self.ledger, repo=self.repo)
        self.assertEqual(ack["result"], "ACCEPTED_WITH_WARNINGS")
        self.assertTrue(any("security_or_privacy_notes" in w for w in ack["warnings"]))
        self.assertTrue(all(v.startswith("EXT-MUSE-") for v in ack["evidence_map"].values()))

    def test_fresh_input_hash_passes(self):
        (self.repo / "PROMPT.md").write_text("brief")
        from abos.util import sha256_file
        b = handoff_bundle(inputs_read_sha256={"PROMPT.md": sha256_file(self.repo / "PROMPT.md")})
        ack = handoff.receive(self.write_bundle(b), self.ledger, repo=self.repo)
        self.assertEqual((ack["result"], ack["checks"]["input_freshness"]), ("ACCEPTED", "PASS"))

    def test_board_has_all_sections(self):
        text = board.render(self.ledger)
        for title in ["Waiting for your approval", "Blocked", "In progress", "Next (MUST first)", "Done", "Parked"]:
            self.assertIn(title, text)


if __name__ == "__main__":
    unittest.main()
