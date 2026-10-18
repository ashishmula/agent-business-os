"""Tester A: unit/specification behaviour (schema validator, task key, pre-flight rules)."""

import unittest
from datetime import date

from helpers import task_spec  # noqa: F401  (sets sys.path)
from abos import schema
from abos.ledger import preflight
from abos.util import task_key


class SchemaValidator(unittest.TestCase):
    S = {
        "type": "object",
        "required": ["a"],
        "additionalProperties": False,
        "properties": {
            "a": {"type": "string", "pattern": "^X-[0-9]+$"},
            "b": {"type": "integer", "minimum": 0, "maximum": 5},
            "c": {"enum": ["P", "Q"]},
            "d": {"type": "array", "items": {"type": "string", "maxLength": 3}},
            "e": {"type": ["string", "null"]},
        },
    }

    def test_valid(self):
        self.assertEqual(schema.validate({"a": "X-1", "b": 3, "c": "P", "d": ["ab"], "e": None}, self.S), [])

    def test_each_rule_fails(self):
        errs = schema.validate({"b": 9, "c": "Z", "d": ["toolong"], "zz": 1, "e": 3}, self.S)
        text = " ".join(errs)
        for needle in ["missing required property 'a'", "above maximum", "not in", "longer than",
                       "unexpected property 'zz'", "expected type"]:
            self.assertIn(needle, text)

    def test_bool_is_not_integer(self):
        self.assertTrue(schema.validate({"a": "X-1", "b": True}, self.S))

    def test_unsupported_keyword_fails_closed(self):
        with self.assertRaises(schema.UnsupportedKeyword):
            schema.validate({}, {"type": "object", "oneOf": []})

    def test_repo_schemas_supported(self):
        self.assertEqual(schema.check_all_schemas(), {})


class TaskKey(unittest.TestCase):
    def test_rewording_and_input_order_do_not_change_key(self):
        a = task_key("Build the  Board!", "", "PRD-X", ["h2", "h1"])
        b = task_key("build the board", "", "PRD-X", ["h1", "h2"])
        self.assertEqual(a, b)

    def test_changed_input_changes_key(self):
        self.assertNotEqual(task_key("o", "", "P", ["h1"]), task_key("o", "", "P", ["h9"]))


class Preflight(unittest.TestCase):
    def _task(self, **kw):
        t = task_spec(**kw)
        t.setdefault("depends_on", [])
        t["task_key"] = task_key(t["objective"], "", t["product_id"], [])
        return t

    def test_no_acceptance_criteria_rejected(self):
        self.assertEqual(preflight(self._task(acceptance_criteria=[]), {})["result"], "REJECTED")

    def test_not_now_parked(self):
        self.assertEqual(preflight(self._task(priority="NOT_NOW"), {})["result"], "PARKED")

    def test_missing_dependency_blocked(self):
        self.assertEqual(preflight(self._task(depends_on=["TASK-0099"]), {})["result"], "BLOCKED")

    def test_done_and_fresh_reused(self):
        old = {**self._task(), "task_id": "TASK-0001", "status": "DONE", "freshness_date": "2099-01-01"}
        pre = preflight(self._task(), {"TASK-0001": old}, today=date(2026, 10, 18))
        self.assertEqual((pre["result"], pre["reused_task_id"]), ("REUSE", "TASK-0001"))

    def test_done_but_stale_is_delta(self):
        old = {**self._task(), "task_id": "TASK-0001", "status": "DONE", "freshness_date": "2026-01-01"}
        self.assertEqual(preflight(self._task(), {"TASK-0001": old}, today=date(2026, 10, 18))["result"], "DELTA")

    def test_open_duplicate_reused_not_rerun(self):
        old = {**self._task(), "task_id": "TASK-0001", "status": "IN_PROGRESS"}
        self.assertEqual(preflight(self._task(), {"TASK-0001": old})["result"], "REUSE")

    def test_new_task_runs(self):
        self.assertEqual(preflight(self._task(), {})["result"], "RUN")


if __name__ == "__main__":
    unittest.main()


class ParityWithJsonschema(unittest.TestCase):
    """Optional cross-check: our validator agrees with the reference library when it is installed."""

    def test_same_verdicts(self):
        try:
            import jsonschema
        except ImportError:
            self.skipTest("jsonschema not installed (optional)")
        import json
        from helpers import MUSE_01, handoff_bundle, task_spec  # noqa: F811
        cases = [
            ("handoff", handoff_bundle()),
            ("handoff", handoff_bundle(status="BAD")),
            ("handoff", json.loads(MUSE_01.read_text())),
            ("task", {**task_spec(), "task_id": "TASK-0001", "task_key": "a" * 64, "status": "DONE",
                      "updated_at": "2026-10-18T00:00:00Z"}),
            ("task", {**task_spec(), "task_id": "T1"}),
        ]
        for name, inst in cases:
            ours = not schema.check(inst, name)
            ref = jsonschema.Draft202012Validator(schema.load_schema(name)).is_valid(inst)
            self.assertEqual(ours, ref, (name, inst.get("task_id")))
