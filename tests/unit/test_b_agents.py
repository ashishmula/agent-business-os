"""Tester B: subagent definitions agree with the routing rules and the model registry."""

import re
import tempfile
import tomllib
import unittest
from pathlib import Path

from helpers import ROOT

from abos.install import install

AGENTS = ROOT / "agents" / "claude"
TIER = {"haiku": "T2", "sonnet": "T3", "opus": "T4"}
WRITE_TOOLS = {"Edit", "Write", "NotebookEdit", "MultiEdit"}


def frontmatter(path: Path) -> dict:
    text = path.read_text()
    m = re.match(r"^---\n(.*?)\n---\n(.+)", text, re.S)
    assert m, f"{path.name}: no frontmatter"
    meta = dict(line.split(": ", 1) for line in m.group(1).splitlines())
    meta["tools"] = {t.strip() for t in meta.get("tools", "").split(",") if t.strip()}
    meta["body"] = m.group(2)
    return meta


class Agents(unittest.TestCase):
    def setUp(self):
        self.agents = {p.stem: frontmatter(p) for p in AGENTS.glob("*.md")}
        with open(ROOT / "config" / "routing-rules.toml", "rb") as handle:
            self.rules = tomllib.load(handle)["rule"]

    def test_frontmatter_complete(self):
        for name, meta in self.agents.items():
            with self.subTest(name):
                self.assertEqual(meta["name"], name)
                self.assertIn(meta["model"], TIER)
                self.assertTrue(meta["description"] and meta["tools"] and meta["body"].strip())

    def test_every_rule_routes_to_a_real_agent_at_or_above_its_floor(self):
        for rule in self.rules:
            with self.subTest(rule["task"]):
                agent = rule["agent"]
                if agent == "none":
                    continue
                self.assertIn(agent, self.agents)
                self.assertGreaterEqual(TIER[self.agents[agent]["model"]], rule["floor"])

    def test_reviewers_cannot_write(self):
        for name in ("security-reviewer", "tester-b", "tester-c", "quick-helper"):
            self.assertFalse(self.agents[name]["tools"] & WRITE_TOOLS, name)

    def test_opus_only_for_critical_agents(self):
        critical = {r["agent"] for r in self.rules if r["risk"] == "CRITICAL"}
        for name, meta in self.agents.items():
            if meta["model"] == "opus":
                self.assertIn(name, critical)

    def test_settings_default_is_sonnet(self):
        import json
        self.assertEqual(json.loads((ROOT / "config" / "claude-code-settings.json").read_text())["model"], "sonnet")

    def test_install_copies_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "config").mkdir()
            (repo / "agents" / "claude").mkdir(parents=True)
            (repo / "config" / "claude-code-settings.json").write_text("{}")
            (repo / "agents" / "claude" / "builder.md").write_text("x")
            self.assertEqual(len(install(repo)), 2)
            self.assertEqual(install(repo), [])
            (repo / "agents" / "claude" / "builder.md").write_text("y")
            self.assertEqual(install(repo), ["updated .claude/agents/builder.md"])
            self.assertEqual((repo / ".claude" / "agents" / "builder.md").read_text(), "y")


if __name__ == "__main__":
    unittest.main()
