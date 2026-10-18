"""Phase report command (TASK-0018): counts, latest test record, NOT_TESTED / no-evidence list, --write, unknown gate."""

import contextlib
import io
import hashlib
import json
import os
import stat
import subprocess
import sys

from helpers import ROOT, TempRepoTest, task_spec, write_test_record

from abos import phasereport


class PhaseReport(TempRepoTest):
    def setUp(self):
        super().setUp()
        self.results = self.repo / "results"
        self.results.mkdir()

    def add(self, **kw):
        task, _ = self.ledger.create_task(task_spec(**kw))
        return task["task_id"]

    def test_counts_flagged_and_latest_test(self):
        a = self.add()
        b = self.add(objective="Second task")
        self.add(objective="Other gate", serves_gate="G9-other")
        self.ledger.update(b, {"status": "NOT_TESTED"})
        for rid, at, res in [("TEST-1", "2026-01-01T00:00:00Z", "FAIL"), ("TEST-2", "2026-02-01T00:00:00Z", "PASS")]:
            write_test_record(self.results, rid, rid, at, res)
        text = phasereport.build(self.ledger, "G1-backbone", self.results)
        self.assertIn("- NOT_STARTED: 1", text)
        self.assertIn("- NOT_TESTED: 1", text)
        self.assertIn("TEST-2: PASS", text)
        self.assertNotIn("TEST-1", text)
        self.assertIn(a, text)
        self.assertIn(f"{b} [NOT_TESTED]", text)
        self.assertNotIn("Other gate", text)

    def test_no_test_record_is_labelled(self):
        self.add()
        self.assertIn("NOT_TESTED: no unit test record", phasereport.build(self.ledger, "G1-backbone", self.results))

    def test_unknown_gate(self):
        self.assertIsNone(phasereport.build(self.ledger, "G-nope", self.results))

    def test_cli_unknown_gate_exits_1_and_write(self):
        cli = [sys.executable, "-m", "abos"]
        env = {"PYTHONPATH": str(ROOT / "tools"), "PATH": "/usr/bin:/bin"}
        bad = subprocess.run(cli + ["phase-report", "G-nope"], cwd=ROOT, capture_output=True, text=True, env=env)
        self.assertEqual(bad.returncode, 1)
        self.assertIn("unknown gate", bad.stderr)
        out = ROOT / "reports" / "_tmp_phase_report_cli_test.md"
        self.addCleanup(lambda: out.exists() and out.unlink())
        ok = subprocess.run(cli + ["phase-report", "G2-phase-3", "--write", str(out)], cwd=ROOT,
                            capture_output=True, text=True, env=env)
        self.assertEqual(ok.returncode, 0, ok.stderr)
        self.assertEqual(out.read_text(), ok.stdout)

    # ---- round 2 regressions (testers B and C findings) ----

    def cli(self, gate="G1-backbone", write=None, force=False):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = phasereport.run_cli(self.ledger, gate, write, force, root=self.repo, results_dir=self.results)
        return code, out.getvalue(), err.getvalue()

    def reports(self):
        d = self.repo / "reports"
        d.mkdir(exist_ok=True)
        return d

    def assertRejected(self, write, fragment=None):
        self.add()
        code, out, err = self.cli(write=write)
        self.assertEqual(code, 2, err)
        self.assertEqual(out, "", "failed --write must not print the report")
        self.assertNotIn("Traceback", err)
        self.assertEqual(len(err.strip().splitlines()), 1, err)
        if fragment:
            self.assertIn(fragment, err)

    def test_c1_write_outside_repo_rejected(self):  # C bug 1: ../outside.md, absolute path outside
        self.reports()
        outside = self.repo.parent / "abos_outside_test.md"
        self.addCleanup(lambda: outside.exists() and outside.unlink())
        self.assertRejected(str(outside), "inside the repo")
        self.assertFalse(outside.exists())
        self.assertRejected(str(self.repo / "reports" / ".." / ".." / "x.md"), "'..'")

    def test_c1_write_private_and_non_reports_rejected(self):  # C bug 1: private/, anywhere not reports/
        self.reports()
        (self.repo / "private").mkdir()
        self.assertRejected(str(self.repo / "private" / "x.md"), "reports/")
        self.assertRejected(str(self.repo / "reports" / "private" / "x.md"))
        self.assertRejected(str(self.repo / "elsewhere.md"), "reports/")
        self.assertFalse((self.repo / "private" / "x.md").exists())

    def test_c1_write_symlink_target_and_parent_rejected(self):  # C bug 1: followed symlinks
        reports = self.reports()
        secret = self.repo / "secret.txt"
        secret.write_text("SECRETDATA")
        (reports / "link.md").symlink_to(secret)
        self.assertRejected(str(reports / "link.md"), "symlink")
        self.assertEqual(secret.read_text(), "SECRETDATA")
        (reports / "dirlink").symlink_to(self.repo)
        self.assertRejected(str(reports / "dirlink" / "x.md"), "symlink")

    def test_c1_write_refuses_overwrite_unless_force(self):  # C bug 1: silent overwrite
        target = self.reports() / "r.md"
        target.write_text("KEEP")
        self.assertRejected(str(target), "--force")
        self.assertEqual(target.read_text(), "KEEP")
        code, out, err = self.cli(write=str(target), force=True)
        self.assertEqual(code, 0, err)
        self.assertEqual(target.read_text(), out)

    def test_c1_write_new_file_in_reports_ok(self):  # positive path stays working
        self.add()
        target = self.reports() / "new.md"
        code, out, err = self.cli(write=str(target))
        self.assertEqual((code, target.read_text()), (0, out), err)

    def test_c2_tampered_ledger_exits_2(self):  # C bug 2: no chain check, tampered status trusted
        self.add()
        p = self.ledger.events_path
        p.write_text(p.read_text().replace("NOT_STARTED", "DONE"))
        code, out, err = self.cli()
        self.assertEqual(code, 2)
        self.assertIn("ledger verify failed", err)
        self.assertEqual(out, "")

    def test_c2_torn_tail_exits_2(self):  # C bug 2: torn last line gave exit 0 and a short count
        self.add()
        with open(self.ledger.events_path, "a") as fh:
            fh.write('{"half": ')
        code, _, err = self.cli()
        self.assertEqual(code, 2)
        self.assertIn("ledger verify failed", err)

    def test_c5_missing_or_empty_ledger_says_so(self):  # C minor: reported "unknown gate"
        code, _, err = self.cli()
        self.assertEqual(code, 2)
        self.assertIn("ledger is missing or empty", err)

    def test_c3_malformed_ledger_lines_no_traceback(self):  # C bug 3: KeyError/TypeError/UnicodeDecodeError
        self.add()
        p = self.ledger.events_path
        good = p.read_text()
        for bad in (good + "\n[1,2]\n" + good, good + "\n{}\n" + good, None):
            if bad is None:
                p.write_bytes(good.encode() + b"\xff\xfe\n" + good.encode())
            else:
                p.write_text(bad)
            code, out, err = self.cli()
            self.assertEqual(code, 2, err)
            self.assertNotIn("Traceback", err)
            self.assertEqual(len(err.strip().splitlines()), 1, err)

    def test_c3_bad_test_records_skipped(self):  # C bug 3: invalid UTF-8 and int/str run_at crashed
        self.add()
        (self.results / "a.json").write_bytes(b'{"test_id": "T-\xff"}')
        (self.results / "b.json").write_text(json.dumps({"test_id": "T-INT", "run_at": 1, "result": "PASS"}))
        write_test_record(self.results, "c", "T-STR", "2026-01-01T00:00:00Z")
        (self.results / "d.json").mkdir()
        (self.results / "e.json").write_text("[1]")
        code, out, err = self.cli()
        self.assertEqual(code, 0, err)
        self.assertIn("T-STR", out)

    def test_c3_write_oserrors_are_one_line(self):  # C bug 3 + minor: dir target, missing parent, "", "-"
        reports = self.reports()
        (reports / "adir").mkdir()
        self.assertRejected(str(reports / "adir"), "directory")
        self.assertRejected(str(reports / "nope" / "x.md"), "parent directory")
        self.assertRejected(str(reports / ("n" * 300 + ".md")))
        self.assertRejected("")
        self.assertRejected("-")

    def test_c4_test_record_fields_sanitised(self):  # C bug 4: forged heading/task line from result file
        self.add()
        write_test_record(self.results, "x", "T\n# H1", "2026-01-01T00:00:00Z",
                          subject_hash="a\x1b[31mb\n## Forged heading\n- TASK-9999 [DONE] fake" + "z" * 500)
        code, out, err = self.cli()
        self.assertEqual(code, 0, err)
        self.assertNotIn("\n## Forged heading", out)
        self.assertNotIn("\n- TASK-9999", out)
        self.assertNotIn("\x1b", out)
        self.assertEqual(len(out.splitlines()), len(out.strip().splitlines()))
        rec_line = [ln for ln in out.splitlines() if "(run 2026" in ln]
        self.assertEqual(len(rec_line), 1)
        self.assertLess(len(rec_line[0]), 250)

    def test_c4_clean_caps_and_strips(self):  # C bug 4: helper contract
        s = phasereport.clean("a\nb\x00c\x07" + "x" * 500, 80)
        self.assertEqual(len(s), 80)
        self.assertNotRegex(s, r"[\x00-\x1f]")

    def test_c5_unknown_gate_echo_bounded_and_escaped(self):  # C minor: unbounded echo with control chars
        self.add()
        code, out, err = self.cli(gate="bad|gate\n\x1b[31m`x`" + "A" * 5000)
        self.assertEqual(code, 1)
        self.assertEqual(len(err.strip().splitlines()), 1)
        self.assertLess(len(err), 200)
        for ch in ("|", "\x1b", "`"):
            self.assertNotIn(ch, err)

    def test_b1_runbook_has_phase_report_row(self):  # B finding: RUNBOOK.md missing the command
        row = [ln for ln in (ROOT / "RUNBOOK.md").read_text().splitlines() if "./abos phase-report" in ln]
        self.assertEqual(len(row), 1)
        self.assertTrue(row[0].startswith("| ") and row[0].rstrip().endswith("|"))
        self.assertEqual(row[0].count("|"), 3)

    # ---- round 3 regressions (tester C round 2 findings) ----

    def good(self, name="good", test_id="TEST-GOOD", run_at="2026-01-01T00:00:00Z", **kw):
        return write_test_record(self.results, name, test_id, run_at, **kw)

    def forge(self, name, **changes):
        """A valid record with some fields overridden (None value deletes the key)."""
        path = self.good(name, test_id="TEST-FORGED", run_at="2026-06-01T00:00:00Z")
        rec = json.loads(path.read_text())
        for k, v in changes.items():
            rec.pop(k, None) if v is None else rec.__setitem__(k, v)
        path.write_text(json.dumps(rec))
        return path

    def assertForgedSkipped(self, n=1):
        self.add()
        self.good()
        code, out, err = self.cli()
        self.assertEqual(code, 0, err)
        self.assertIn("TEST-GOOD: PASS", out)
        self.assertNotIn("TEST-FORGED", out)
        self.assertIn(f"Untrusted test records skipped: {n}", out)

    def test_b_r3_d1_valid_record_trusted_zero_skipped(self):
        self.add()
        self.good()
        code, out, err = self.cli()
        self.assertEqual(code, 0, err)
        self.assertIn("TEST-GOOD: PASS", out)
        self.assertIn("Untrusted test records skipped: 0", out)

    def test_b_r3_d1_forged_hash_and_future_date_skipped(self):
        self.forge("f1", raw_output_hash="0" * 64)
        self.forge("f2", run_at="2099-01-01T00:00:00Z")
        self.assertForgedSkipped(2)

    def test_b_r3_d1_log_tampered_after_the_fact_skipped(self):
        p = self.forge("f1")
        (self.results / "f1.log").write_text("edited")
        self.assertTrue(p.exists())
        self.assertForgedSkipped()

    def test_b_r3_d1_bad_result_exit_status_run_at_skipped(self):
        self.forge("r1", result="MAYBE")
        self.forge("r2", result=1)
        self.forge("e1", exit_status=None)
        self.forge("e2", exit_status=True)
        self.forge("e3", exit_status="0")
        self.forge("t1", run_at=1)
        self.forge("t2", run_at="2026")
        self.forge("t3", run_at="2026-01-01T00:00:00")  # naive: not UTC
        self.forge("t4", run_at="2026-01-01T00:00:00+05:00")
        self.assertForgedSkipped(9)

    def test_b_r4_result_contradicting_exit_status_skipped(self):
        self.forge("x1", result="PASS", exit_status=1)
        self.forge("x2", result="FAIL", exit_status=0)
        self.assertForgedSkipped(2)

    def test_b_r3_d1_log_path_escape_skipped(self):
        outside = self.repo / "outside.log"
        outside.write_text("x")
        self.forge("o1", raw_output_path=str(outside), raw_output_hash=hashlib.sha256(b"x").hexdigest())
        self.forge("o2", raw_output_path=str(self.results / ".." / "outside.log"),
                   raw_output_hash=hashlib.sha256(b"x").hexdigest())
        (self.results / "lnk.log").symlink_to(outside)
        self.forge("o3", raw_output_path=str(self.results / "lnk.log"), raw_output_hash=hashlib.sha256(b"x").hexdigest())
        self.forge("o4", raw_output_path=None)
        self.forge("o5", raw_output_path=str(self.results))  # a directory
        self.assertForgedSkipped(5)

    def test_b_r3_d1_symlink_oversize_and_fifo_records_skipped(self):
        target = self.forge("real")
        outside = self.repo / "elsewhere.json"
        outside.write_text(target.read_text())
        target.unlink()  # only the symlinked copy remains
        (self.results / "link.json").symlink_to(outside)
        big = self.results / "big.json"
        big.write_text(json.dumps({"test_id": "TEST-FORGED", "pad": "x" * 1_100_000}))
        os.mkfifo(self.results / "pipe.json")
        self.assertForgedSkipped(3)  # link + big + pipe

    def test_b_r3_d1_relative_log_path_resolves_against_root(self):
        self.add()
        p = self.good()
        rec = json.loads(p.read_text())
        rec["raw_output_path"] = "results/good.log"
        p.write_text(json.dumps(rec))
        code, out, err = self.cli()
        self.assertIn("TEST-GOOD: PASS", out, err)

    def test_b_r3_d2_echoed_fields_cannot_render_links_images_html(self):
        evil = "[x](javascript:alert(1)) ![i](http://e.example/p.png) <script>alert(1)</script> <b>x</b>"
        self.add(objective=evil)
        self.good(test_id="[t](javascript:1)", subject_hash="![i](http://e/p) <img src=x>")
        code, out, err = self.cli()
        self.assertEqual(code, 0, err)
        body = out.replace("[NOT_STARTED]", "").replace("[NOT_TESTED]", "")
        for ch in "[]<>`":
            self.assertNotIn(ch, body)
        self.assertNotIn("](", out)
        self.assertNotIn("<script", out)

    def test_b_r3_d2_task_id_and_status_cleaned(self):
        self.assertEqual(phasereport.clean_token("NOT_STARTED"), "NOT_STARTED")
        self.assertEqual(phasereport.clean_token("TASK-0018"), "TASK-0018")
        for bad in ("[x](http://e)", "<b>DONE</b>", "![i](u)", "DONE\n## H"):
            out = phasereport.clean_token(bad)
            for ch in "[]<>\n":
                self.assertNotIn(ch, out)

    def test_b_r3_d2_forged_status_in_ledger_not_rendered(self):
        a = self.add()
        self.ledger.update(a, {"status": "NOT_TESTED"})
        text = phasereport.build(self.ledger, "G1-backbone", self.results)
        self.assertIn(f"{a} [NOT_TESTED]", text)

    def test_b_r3_d3_force_keeps_original_mode(self):
        self.add()
        target = self.reports() / "m.md"
        target.write_text("old")
        os.chmod(target, 0o444)
        code, out, err = self.cli(write=str(target), force=True)
        self.assertEqual(code, 0, err)
        self.assertEqual(stat.S_IMODE(os.stat(target).st_mode), 0o444)
        self.assertEqual(target.read_text(), out)

    def test_b_r3_d3_force_keeps_mode_0640_and_new_file_is_0644(self):
        self.add()
        target = self.reports() / "m2.md"
        target.write_text("old")
        os.chmod(target, 0o640)
        self.cli(write=str(target), force=True)
        self.assertEqual(stat.S_IMODE(os.stat(target).st_mode), 0o640)
        fresh = self.reports() / "fresh.md"
        self.cli(write=str(fresh), force=True)
        self.assertEqual(stat.S_IMODE(os.stat(fresh).st_mode), 0o644)
