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

    def test_t1_off_and_no_active_local_model_until_benchmarked(self):
        self.assertFalse(self.load("routing-rules.toml")["t1_enabled"])
        local = [m for m in self.load("model-registry.toml")["model"] if m["environment"] == "OLLAMA_LOCAL"]
        self.assertTrue(all(m["status"] != "ACTIVE" for m in local))

    def test_no_secrets_in_config(self):
        from abos.secrets import scan_text
        for path in CONFIG.glob("*.toml"):
            self.assertEqual(scan_text(path.read_text()), [], path.name)


if __name__ == "__main__":
    unittest.main()
