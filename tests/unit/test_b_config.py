"""Tester B: config files parse and stay consistent with the design."""

import tomllib
import unittest

from helpers import ROOT

CONFIG = ROOT / "config"


class Config(unittest.TestCase):
    def load(self, name):
        with open(CONFIG / name, "rb") as handle:
            return tomllib.load(handle)

    def test_all_config_parses(self):
        for path in CONFIG.glob("*.toml"):
            with self.subTest(path.name), open(path, "rb") as handle:
                tomllib.load(handle)

    def test_thresholds_ordered(self):
        b = self.load("budgets.toml")
        c = b["context"]
        self.assertLess(c["warn_pct"], c["act_pct"])
        self.assertLess(c["act_pct"], c["hard_pct"])
        for w in b["windows"].values():
            self.assertLess(w["soft_pct"], w["hard_pct"])

    def test_critical_floors_are_t4(self):
        for rule in self.load("routing-rules.toml")["rule"]:
            if rule["risk"] == "CRITICAL":
                self.assertEqual(rule["floor"], "T4", rule["task"])

    def test_local_model_active_only_with_passing_grounded_evals(self):
        import json
        rules = self.load("routing-rules.toml")
        local = [m for m in self.load("model-registry.toml")["model"] if m["environment"] == "OLLAMA_LOCAL"]
        active = [m for m in local if m["status"] == "ACTIVE"]
        if rules["t1_enabled"]:
            self.assertTrue(active)
        for m in active:
            self.assertTrue(set(m["active_for"]) <= set(rules["t1_tasks"]))
            self.assertGreaterEqual(len(m["eval_records"]), 2)  # main set + held-out set
            for rel in m["eval_records"]:
                path = ROOT / rel
                if not path.exists():  # records live on the Mac; the mirror may lack them
                    self.skipTest(f"eval record not present here: {rel}")
                rec = json.loads(path.read_text())
                self.assertEqual((rec["result"], rec["grounding_check"], rec["invented_values"]), ("PASS", True, 0))

    def test_no_secrets_in_config(self):
        from abos.secrets import scan_text
        for path in CONFIG.glob("*.toml"):
            self.assertEqual(scan_text(path.read_text()), [], path.name)


if __name__ == "__main__":
    unittest.main()
