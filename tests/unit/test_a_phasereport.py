"""Tester A spec tests for TASK-0018 (phase-report). One test per acceptance criterion (AC1..AC5)."""

import json
import re
import subprocess
import sys

from helpers import ROOT, TempRepoTest, task_spec, write_test_record

from abos import phasereport

GATE = "G1-backbone"


class PhaseReportSpec(TempRepoTest):
    def setUp(self):
        super().setUp()
        self.results = self.repo / "results"
        self.results.mkdir()

    def add(self, **kw):
        task, _ = self.ledger.create_task(task_spec(**kw))
        return task["task_id"]

    def section(self, text, title):
        m = re.search(rf"## {re.escape(title)}\n(.*?)(?:\n## |\Z)", text, re.S)
        self.assertIsNotNone(m, f"missing section {title}")
        return m.group(1)

    def test_ac1_counts_by_status_match_ledger_for_gate(self):
        ids = [self.add(objective=f"task {i}") for i in range(4)]
        self.add(objective="other gate", serves_gate="G9-other")
        self.ledger.update(ids[0], {"status": "NOT_TESTED"})
        self.ledger.update(ids[1], {"status": "NOT_TESTED"})
        text = phasereport.build(self.ledger, GATE, self.results)
        sec = self.section(text, "Counts by status")
        expected = {}
        for t in self.ledger.tasks().values():
            if t["serves_gate"] == GATE:
                expected[t["status"]] = expected.get(t["status"], 0) + 1
        got = {m[0]: int(m[1]) for m in re.findall(r"- (\w+): (\d+)", sec)}
        self.assertEqual(got, expected)
        self.assertEqual(sum(got.values()), 4)
        self.assertEqual(got["NOT_TESTED"], 2)

    def test_ac2_latest_test_record_with_id_and_result(self):
        for rid, at, res in [("T-OLD", "2026-01-01T00:00:00Z", "FAIL"), ("T-NEW", "2026-03-01T00:00:00Z", "PASS"),
                             ("T-MID", "2026-02-01T00:00:00Z", "FAIL")]:
            write_test_record(self.results, rid, rid, at, res)
        (self.results / "junk.json").write_text("{not json")
        self.add()
        sec = self.section(phasereport.build(self.ledger, GATE, self.results), "Latest unit test record")
        self.assertIn("T-NEW", sec)
        self.assertIn("PASS", sec)
        self.assertNotIn("T-OLD", sec)
        self.assertNotIn("T-MID", sec)

    def test_ac2_no_record_is_labelled_not_tested(self):
        self.add()
        sec = self.section(phasereport.build(self.ledger, GATE, self.results), "Latest unit test record")
        self.assertIn("NOT_TESTED", sec)

    def test_ac3_not_tested_or_no_evidence_listed_separately(self):
        nt = self.add(objective="nt task")
        noev = self.add(objective="noev task")
        ev = self.add(objective="has evidence task")
        self.ledger.update(nt, {"status": "NOT_TESTED"})
        self.ledger.update(ev, {"evidence_ids": ["EV-1"]})
        text = phasereport.build(self.ledger, GATE, self.results)
        sec = self.section(text, "NOT_TESTED or no evidence")
        self.assertIn(nt, sec)
        self.assertIn(noev, sec)
        self.assertNotIn(ev, sec)

    def test_ac3_all_evidenced_lists_none(self):
        a = self.add()
        self.ledger.update(a, {"evidence_ids": ["EV-1"]})
        sec = self.section(phasereport.build(self.ledger, GATE, self.results), "NOT_TESTED or no evidence")
        self.assertNotIn(a, sec)

    def _cli(self, *args):
        env = {"PYTHONPATH": str(ROOT / "tools"), "PATH": "/usr/bin:/bin"}
        return subprocess.run([sys.executable, "-m", "abos", *args], cwd=ROOT, capture_output=True, text=True, env=env)

    def test_ac4_write_path_writes_same_text_as_markdown(self):
        out = ROOT / "reports" / "_tmp_phase_report_a_ac4.md"  # --write is confined to reports/ (round 2)
        self.addCleanup(lambda: out.exists() and out.unlink())
        r = self._cli("phase-report", "G2-phase-3", "--write", str(out))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(out.exists())
        self.assertEqual(out.read_text(), r.stdout)
        self.assertTrue(out.read_text().startswith("# "))  # Markdown heading

    def test_ac5_unknown_gate_clear_message_exit_1(self):
        r = self._cli("phase-report", "G-does-not-exist")
        self.assertEqual(r.returncode, 1)
        msg = (r.stderr + r.stdout).lower()
        self.assertIn("unknown gate", msg)
        self.assertIn("g-does-not-exist", msg)
        self.assertNotIn("traceback", msg)

    def test_ac5_unknown_gate_does_not_write_file(self):
        out = ROOT / "reports" / "_tmp_phase_report_a_ac5.md"
        self.addCleanup(lambda: out.exists() and out.unlink())
        r = self._cli("phase-report", "G-does-not-exist", "--write", str(out))
        self.assertEqual(r.returncode, 1)
        self.assertFalse(out.exists())
