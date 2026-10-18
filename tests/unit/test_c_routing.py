"""Tester C: Model Router and cost caps (TASK-0015). Exhaustive over every rule and input."""

import itertools
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from helpers import ROOT

from abos import router

CFG, BUDGETS = router.load(ROOT / "config")
TASKS = [r["task"] for r in CFG["rule"]]
COMBOS = list(itertools.product(TASKS, [None, "LOW", "STANDARD", "CRITICAL"], ["INTERNAL", "PRIVATE"],
                                router.LEVELS, range(4)))
idx = router.TIERS.index


def floor_of(task):
    return next(r for r in CFG["rule"] if r["task"] == task)["floor"]


class RouterInvariants(unittest.TestCase):
    def decisions(self):
        for task, risk, privacy, budget, failures in COMBOS:
            d = router.route(task, CFG, BUDGETS, risk=risk, privacy=privacy, budget=budget, failures=failures)
            yield (task, risk, privacy, budget, failures), d

    def test_never_below_floor(self):
        below = [k for k, d in self.decisions() if idx(d["tier"]) < idx(floor_of(k[0]))]
        self.assertEqual(below, [], f"{len(below)} of {len(COMBOS)} routes below floor")

    def test_critical_never_shifted_down_or_paused(self):
        for (task, risk, privacy, budget, failures), d in self.decisions():
            if d["risk"] != "CRITICAL" or privacy == "PRIVATE":
                continue
            base = router.route(task, CFG, BUDGETS, risk=risk, failures=failures)
            self.assertEqual(d["tier"], base["tier"], (task, budget))
            self.assertNotEqual(d["action"], "PAUSE", (task, budget))

    def test_private_never_leaves_local_tiers(self):
        for k, d in self.decisions():
            if k[2] == "PRIVATE" and d["action"] != "BLOCKED":
                self.assertIn(d["tier"], ("T0", "T1"), k)

    def test_t1_only_for_enabled_tasks(self):
        for k, d in self.decisions():
            if d["tier"] == "T1":
                self.assertIn(k[0], CFG["t1_tasks"], k)

    def test_config_floors_not_above_start(self):
        for r in CFG["rule"]:
            self.assertLessEqual(idx(r["floor"]), idx(r["start_tier"]), r["task"])


class RouterCases(unittest.TestCase):
    def r(self, task, **kw):
        return router.route(task, CFG, BUDGETS, **kw)

    def test_soft_budget_moves_eligible_work_down(self):
        self.assertEqual(self.r("routine_code_edit")["tier"], "T3")
        self.assertEqual(self.r("routine_code_edit", budget="SOFT")["tier"], "T2")

    def test_soft_budget_stops_at_floor(self):
        self.assertEqual(self.r("new_code", budget="SOFT")["tier"], "T3")  # floor T3

    def test_soft_budget_skips_t1_when_not_enabled(self):
        d = self.r("short_summary", budget="SOFT")  # T2 -> T1 not allowed for this task
        self.assertEqual(d["tier"], "T2")

    def test_hard_budget_pauses_non_critical_runs_critical(self):
        self.assertEqual(self.r("research_synthesis", budget="HARD")["action"], "PAUSE")
        d = self.r("architecture_or_security_review", budget="HARD")
        self.assertEqual((d["action"], d["tier"]), ("RUN", "T4"))

    def test_risk_override_upgrades_never_downgrades(self):
        self.assertEqual(self.r("short_summary", risk="CRITICAL", budget="SOFT")["tier"], "T2")
        self.assertEqual(self.r("architecture_or_security_review", risk="LOW")["risk"], "CRITICAL")

    def test_failures_escalate_then_stop(self):
        self.assertEqual(self.r("short_summary", failures=1)["tier"], "T3")
        self.assertEqual(self.r("short_summary", failures=3)["action"], "ESCALATE_TO_ASHISH")

    def test_private_routing(self):
        local = self.r("schema_extraction", privacy="PRIVATE")
        self.assertEqual((local["tier"], local["environment"]), ("T1", "OLLAMA_LOCAL"))
        self.assertEqual(self.r("deterministic", privacy="PRIVATE")["tier"], "T0")
        self.assertEqual(self.r("research_synthesis", privacy="PRIVATE")["action"], "BLOCKED")
        self.assertEqual(self.r("research_synthesis", privacy="PRIVATE", cloud_approval="APR-9999")["action"], "RUN")

    def test_unknown_task_blocked(self):
        self.assertEqual(self.r("send_supplier_email")["action"], "BLOCKED")

    def test_agent_and_environment_from_rule(self):
        d = self.r("gate_challenger_review")
        self.assertEqual((d["environment"], d["tier"]), ("DOT_MUSE", "T4"))


class BudgetThresholds(unittest.TestCase):
    """Router level and the prompt nudge must switch at exactly the configured percentages."""

    def test_levels_at_boundaries(self):
        soft, hard = BUDGETS["windows"]["five_hour"]["soft_pct"], BUDGETS["windows"]["five_hour"]["hard_pct"]
        cases = [(None, None, "OK"), (soft - 0.1, None, "OK"), (soft, None, "SOFT"), (hard - 0.1, None, "SOFT"),
                 (hard, None, "HARD"), (10, soft, "SOFT"), (soft, hard, "HARD"), (100, 0, "HARD")]
        for five, seven, want in cases:
            self.assertEqual(router.budget_level(five, seven, BUDGETS), want, (five, seven))

    def test_nudge_agrees_with_router(self):
        tmp = tempfile.TemporaryDirectory(); self.addCleanup(tmp.cleanup)
        proj = Path(tmp.name); (proj / "config").mkdir()
        shutil.copy(ROOT / "config" / "budgets.toml", proj / "config")
        sessions = proj / "state" / "context-sessions"; sessions.mkdir(parents=True)
        env = {**os.environ, "CLAUDE_PROJECT_DIR": str(proj)}
        for five in (0, 69.9, 70, 89.9, 90, 99):
            (sessions / "s1.jsonl").write_text(json.dumps({"session_id": "s1", "five_hour_pct": five,
                                                           "seven_day_pct": 0, "context_fill_pct": 10}) + "\n")
            out = subprocess.run([sys.executable, str(ROOT / "tools/hooks/prompt_nudge.py")],
                                 input=json.dumps({"session_id": "s1", "prompt": "hi"}),
                                 capture_output=True, text=True, env=env, timeout=30).stdout
            level = router.budget_level(five, 0, BUDGETS)
            self.assertEqual("pause non-critical" in out, level == "HARD", five)
            self.assertEqual("delegate eligible work" in out, level == "SOFT", five)


class RouteCli(unittest.TestCase):
    def test_cli_exit_codes(self):
        run = lambda *a: subprocess.run(["sh", str(ROOT / "abos"), "route", *a], capture_output=True, text=True, timeout=30)
        ok = run("new_code", "--five", "10")
        self.assertEqual(ok.returncode, 0, ok.stderr)
        self.assertEqual(json.loads(ok.stdout)["agent"], "builder")
        self.assertEqual(run("new_code", "--five", "95").returncode, 3)


if __name__ == "__main__":
    unittest.main()
