"""Tester C: the micro-test scorer never passes on missing data and never stores personal data."""

import tempfile
import unittest
from pathlib import Path

import helpers  # noqa: F401  (puts tools/ on sys.path)
from abos.microtest import MicrotestError, load_config, read_rows, score

HEADER = "kind,event,score,scanned,signed_up,prefers,reinvite,spend_cad\n"


def write_csv(text: str) -> Path:
    path = Path(tempfile.mkdtemp()) / "tally.csv"
    path.write_text(text)
    return path


def taste_rows(n, score_val=5, scanned=1, signed=1, prefers="can", events=("run-club", "coffee-rave")):
    return "".join(f"taste,{events[i % len(events)]},{score_val},{scanned},{signed},{prefers},1,\n" for i in range(n))


class Microtest(unittest.TestCase):
    cfg = load_config()

    def run_score(self, body):
        return score(read_rows(write_csv(HEADER + body), self.cfg), self.cfg)

    def gate(self, report, name):
        return next(g for g in report["gates"] if g["gate"] == name)

    def test_strong_event_data_passes(self):
        report = self.run_score(taste_rows(320))
        self.assertEqual(report["overall"], "PASS")
        self.assertEqual(report["format_preference"], {"can": 320, "pouch": 0})

    def test_no_data_is_not_tested_never_pass(self):
        report = self.run_score("")
        self.assertEqual(report["overall"], "NOT_TESTED")
        self.assertTrue(all(g["result"] == "NOT_TESTED" for g in report["gates"]))

    def test_too_few_tasters_is_not_tested(self):
        self.assertEqual(self.gate(self.run_score(taste_rows(10)), "taste_top_box")["result"], "NOT_TESTED")

    def test_low_scores_fail_taste_gate(self):
        report = self.run_score(taste_rows(320, score_val=3))
        self.assertEqual(self.gate(report, "taste_top_box")["result"], "FAIL")
        self.assertEqual(report["overall"], "FAIL")

    def test_one_event_reinviting_is_not_enough(self):
        report = self.run_score(taste_rows(320, events=("run-club",)))
        self.assertEqual(self.gate(report, "organizer_reinvites")["result"], "FAIL")

    def test_personal_data_columns_refused(self):
        with self.assertRaises(MicrotestError):
            read_rows(write_csv("kind,email\ntaste,a@b.c\n"), self.cfg)
        with self.assertRaises(MicrotestError):
            read_rows(write_csv("kind,Phone\ntaste,555\n"), self.cfg)

    def test_bad_values_fail_loudly(self):
        for body in ("taste,x,7,1,0,,0,\n", "taste,x,4,yes,0,,0,\n", "lemonade,x,4,1,0,,0,\n",
                     "taste,x,4,1,0,bottle,0,\n", "ads,,,,3,,,-5\n", "taste,x,4,1,2,,0,\n"):
            with self.assertRaises(MicrotestError, msg=body):
                self.run_score(body)

    def test_ads_gates(self):
        cheap = self.run_score("ads,,,,25,,,200\nads,,,,25,,,200\n")
        self.assertEqual(self.gate(cheap, "ads_cost_per_signup")["result"], "PASS")
        overspent = self.run_score("ads,,,,50,,,700\n")
        self.assertEqual(self.gate(overspent, "ads_spend_cap")["result"], "FAIL")
        zero = self.run_score("ads,,,,0,,,300\n")
        self.assertEqual(self.gate(zero, "ads_cost_per_signup")["result"], "FAIL")


if __name__ == "__main__":
    unittest.main()
