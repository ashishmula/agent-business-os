"""Shared fixtures: every test gets its own temp repo so real state is never touched."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from abos import handoff, util  # noqa: E402
from abos.ledger import Ledger  # noqa: E402

MUSE_01 = ROOT / "reports" / "phase-1" / "muse" / "P1-MUSE-01.json"


def write_test_record(directory, name, test_id, run_at, result="PASS", log_text=None, **extra) -> Path:
    """Write a trustworthy unit-test record (valid log + sha256, absolute log path) into directory/name.json."""
    import hashlib
    directory = Path(directory)
    log = directory / f"{name}.log"
    log.write_text(log_text if log_text is not None else f"log for {test_id}\n")
    rec = {"test_id": test_id, "run_at": run_at, "result": result, "exit_status": 0 if result == "PASS" else 1,
           "raw_output_path": str(log), "raw_output_hash": hashlib.sha256(log.read_bytes()).hexdigest()}
    rec.update(extra)
    path = directory / f"{name}.json"
    path.write_text(json.dumps(rec))
    return path


def task_spec(**overrides) -> dict:
    spec = {
        "project_id": "COFFEE-PROTEIN-OS",
        "product_id": "PRD-PLATFORM",
        "objective": "Build the status board generator",
        "owner_agent": "builder",
        "priority": "MUST",
        "priority_reason": "gate G1 needs it",
        "serves_gate": "G1-backbone",
        "acceptance_criteria": ["board renders all sections"],
    }
    spec.update(overrides)
    return spec


def handoff_bundle(**overrides) -> dict:
    bundle = {
        "handoff_schema_version": "1.0",
        "project_id": "COFFEE-PROTEIN-OS",
        "task_id": "P2-TEST-01",
        "parent_task_ids": [],
        "from_environment": "DOT_MUSE",
        "from_agent": "Muse",
        "to_environment": "CLAUDE_CODE",
        "to_agent": "orchestrator",
        "status": "DONE",
        "objective": "Test bundle",
        "context_brief": "",
        "inputs": [],
        "findings_or_changes": ["a finding"],
        "evidence_ids": ["SRC-0001"],
        "acceptance_criteria": [{"id": "AC-1", "state": "PASS", "evidence": "x"}],
        "assumptions_and_confidence": [],
        "known_failures": [],
        "untested_gaps": [],
        "security_or_privacy_notes": [],
        "model_and_tool_usage": [],
        "next_action": "none",
        "approval_required": False,
    }
    bundle.update(overrides)
    return bundle


class TempRepoTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        self.ledger = Ledger(self.repo / "state" / "task-ledger" / "events.jsonl")
        self._saved = (util.LOCK_PATH, handoff.INBOX, handoff.ACKS)
        util.LOCK_PATH = self.repo / "state" / ".write.lock"
        handoff.INBOX = self.repo / "handoffs" / "inbox"
        handoff.ACKS = self.repo / "handoffs" / "acks"

    def tearDown(self):
        util.LOCK_PATH, handoff.INBOX, handoff.ACKS = self._saved
        self._tmp.cleanup()

    def write_bundle(self, bundle, name="bundle.json", raw: str | None = None) -> Path:
        path = self.repo / name
        path.write_text(raw if raw is not None else json.dumps(bundle))
        return path
