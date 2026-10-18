"""Tester C: the loop-breaker hook trips on runaway repeats and never on normal varied work."""

import json
import unittest

from test_b_hooks import HookTest


class LoopBreaker(HookTest):
    def call(self, command, session="s1"):
        out = self.run_hook("loop_breaker.py", {"session_id": session, "tool_name": "Bash",
                                                "tool_input": {"command": command}})
        self.assertEqual(out.returncode, 0, out.stderr)
        if not out.stdout.strip():
            return "allow"
        return json.loads(out.stdout)["hookSpecificOutput"]["permissionDecision"]

    def test_fourth_identical_call_in_a_row_is_denied(self):
        self.assertEqual([self.call("ls") for _ in range(3)], ["allow"] * 3)
        self.assertEqual(self.call("ls"), "deny")
        log = (self.proj / "logs" / "loop-breaker.jsonl").read_text().splitlines()
        self.assertEqual(len(log), 1)
        self.assertNotIn("ls", json.loads(log[0])["fp"])  # history and log hold hashes, not commands

    def test_a_different_call_resets_the_streak(self):
        for _ in range(3):
            self.call("ls")
        self.assertEqual(self.call("pwd"), "allow")
        self.assertEqual(self.call("ls"), "allow")

    def test_ping_pong_loop_is_denied(self):
        results = [self.call(cmd) for _ in range(7) for cmd in ("ls", "pwd")]
        self.assertIn("deny", results)
        self.assertEqual(results[:12], ["allow"] * 12)  # six of each is still allowed

    def test_many_different_calls_are_never_denied(self):
        self.assertEqual({self.call(f"echo {i}") for i in range(40)}, {"allow"})

    def test_sessions_are_counted_separately(self):
        for _ in range(3):
            self.call("ls", session="a")
        self.assertEqual(self.call("ls", session="b"), "allow")

    def test_limits_come_from_budgets_toml(self):
        cfg = self.proj / "config" / "budgets.toml"
        cfg.write_text(cfg.read_text().replace("max_identical_in_a_row = 3", "max_identical_in_a_row = 1"))
        self.assertEqual(self.call("ls"), "allow")
        self.assertEqual(self.call("ls"), "deny")

    def test_bad_input_and_corrupt_history_fail_open(self):
        out = self.run_hook("loop_breaker.py", None, raw="not json")
        self.assertEqual((out.returncode, out.stdout), (0, ""))
        hist = self.proj / "state" / "context-sessions" / "s1.calls.jsonl"
        hist.parent.mkdir(parents=True)
        hist.write_text("{broken\n")
        self.assertEqual(self.call("ls"), "allow")


if __name__ == "__main__":
    unittest.main()
