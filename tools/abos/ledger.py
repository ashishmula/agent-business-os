"""Task ledger as an append-only, hash-chained event log (PROMPT.md 10.1, 10.3, 10.4).

events.jsonl is the canonical record and is committed to git. Current task state is
rebuilt by replaying the events (like rebuilding a table from a Kafka topic), so
nothing is ever overwritten and every change keeps its history. `export_sqlite`
builds a throwaway SQLite copy for ad-hoc SQL queries.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import date
from pathlib import Path

from . import REPO_ROOT, schema
from .util import dumps, normalize_text, now_iso, sha256_bytes, task_key, write_lock

LEDGER_DIR = REPO_ROOT / "state" / "task-ledger"
EVENTS = LEDGER_DIR / "events.jsonl"

STATUSES = {
    "NOT_STARTED", "IN_PROGRESS", "BLOCKED", "WAITING_FOR_APPROVAL", "REVIEW",
    "CHANGES_REQUESTED", "FAILED", "NOT_TESTED", "VERIFIED", "PASSED", "DONE",
    "SKIPPED_NOT_APPLICABLE",
}
FINISHED = {"DONE", "VERIFIED"}
GENESIS = "0" * 64


class LedgerError(ValueError):
    pass


class Ledger:
    def __init__(self, events_path: Path = EVENTS):
        self.events_path = Path(events_path)

    # ---------- reading ----------

    def events(self) -> list[dict]:
        """Parsed events. A torn last line (crash mid-append) is skipped here and reported by verify_chain."""
        if not self.events_path.exists():
            return []
        lines = [line for line in self.events_path.read_text().splitlines() if line.strip()]
        out = []
        for i, line in enumerate(lines):
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                if i == len(lines) - 1:
                    break  # torn tail; verify_chain blocks writes until it is repaired
                raise LedgerError(f"event line {i + 1} is not valid JSON") from None
        return out

    def torn_tail(self) -> bool:
        if not self.events_path.exists():
            return False
        lines = [line for line in self.events_path.read_text().splitlines() if line.strip()]
        try:
            lines and json.loads(lines[-1])
        except json.JSONDecodeError:
            return True
        return False

    def verify_chain(self) -> list[str]:
        """Detect edited, removed, reordered or half-written events."""
        problems, prev = [], GENESIS
        if self.torn_tail():
            problems.append("torn last line (crash during a write): move it to logs/ by hand, then re-verify")
        for i, event in enumerate(self.events()):
            body = {k: v for k, v in event.items() if k != "hash"}
            if event.get("prev_hash") != prev:
                problems.append(f"event {i} ({event.get('event_id')}): prev_hash does not match")
            if sha256_bytes(dumps(body).encode()) != event.get("hash"):
                problems.append(f"event {i} ({event.get('event_id')}): content hash mismatch")
            prev = event.get("hash")
        return problems

    def tasks(self) -> dict[str, dict]:
        state: dict[str, dict] = {}
        for event in self.events():
            if event["type"] == "TASK_CREATED":
                state[event["task_id"]] = dict(event["data"])
            elif event["type"] == "TASK_UPDATED":
                state[event["task_id"]].update(event["data"])
        return state

    def get(self, task_id: str) -> dict:
        try:
            return self.tasks()[task_id]
        except KeyError:
            raise LedgerError(f"unknown task {task_id}") from None

    # ---------- writing ----------

    def _append(self, kind: str, task_id: str, data: dict, actor: str) -> dict:
        existing = self.events()
        event = {
            "event_id": f"EVT-{len(existing) + 1:06d}",
            "ts": now_iso(),
            "type": kind,
            "task_id": task_id,
            "actor": actor,
            "data": data,
            "prev_hash": existing[-1]["hash"] if existing else GENESIS,
        }
        event["hash"] = sha256_bytes(dumps(event).encode())
        self.events_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.events_path, "a") as handle:
            handle.write(dumps(event) + "\n")
        return event

    def _next_id(self) -> str:
        numbers = [int(t.split("-")[1]) for t in self.tasks() if t.startswith("TASK-")]
        return f"TASK-{max(numbers, default=0) + 1:04d}"

    def create_task(self, spec: dict, actor: str = "orchestrator", today: date | None = None) -> tuple[dict, dict]:
        """Run the pre-flight check, then record the task. Returns (task, preflight)."""
        with write_lock():
            if self.verify_chain():
                raise LedgerError("ledger chain is broken; run `abos ledger verify` before writing")
            task = {
                "status": "NOT_STARTED",
                "depends_on": [],
                "inputs": [],
                "outputs": [],
                "evidence_ids": [],
                "review_status": "NONE",
                "risk_class": "STANDARD",
                "privacy_class": "INTERNAL",
                "scope": "",
                **spec,
            }
            task["task_key"] = task_key(
                task["objective"], task.get("scope", ""), task["product_id"],
                [i["version_or_hash"] for i in task["inputs"]],
            )
            task["task_id"] = self._next_id()
            task["updated_at"] = now_iso()
            pre = preflight(task, self.tasks(), today=today)
            task["preflight"] = pre
            if pre["result"] == "REUSE":
                return self.get(pre["reused_task_id"]), pre
            if pre["result"] == "REJECTED":
                return task, pre
            if pre["result"] == "BLOCKED":
                task["status"] = "BLOCKED"
            elif pre["result"] == "PARKED":
                task["status"] = "NOT_STARTED"
            errors = schema.check(_for_schema(task), "task")
            if errors:
                raise LedgerError("task fails schema: " + "; ".join(errors))
            self._append("TASK_CREATED", task["task_id"], task, actor)
            return task, pre

    def update(self, task_id: str, changes: dict, actor: str = "orchestrator") -> dict:
        with write_lock():
            if self.verify_chain():
                raise LedgerError("ledger chain is broken; run `abos ledger verify` before writing")
            current = self.get(task_id)
            if "status" in changes:
                _check_transition(current, {**current, **changes})
            merged = {**current, **changes, "updated_at": now_iso()}
            errors = schema.check(_for_schema(merged), "task")
            if errors:
                raise LedgerError("update fails schema: " + "; ".join(errors))
            self._append("TASK_UPDATED", task_id, {**changes, "updated_at": merged["updated_at"]}, actor)
            return merged

    # ---------- SQL view for humans ----------

    def export_sqlite(self, path: Path) -> Path:
        path = Path(path)
        path.unlink(missing_ok=True)
        con = sqlite3.connect(path)
        con.execute(
            "CREATE TABLE tasks (task_id TEXT PRIMARY KEY, product_id TEXT, status TEXT, priority TEXT,"
            " owner_agent TEXT, serves_gate TEXT, objective TEXT, updated_at TEXT, json TEXT)"
        )
        con.execute(
            "CREATE TABLE events (event_id TEXT PRIMARY KEY, ts TEXT, type TEXT, task_id TEXT, actor TEXT, json TEXT)"
        )
        for t in self.tasks().values():
            con.execute(
                "INSERT INTO tasks VALUES (?,?,?,?,?,?,?,?,?)",
                (t["task_id"], t["product_id"], t["status"], t["priority"], t["owner_agent"],
                 t["serves_gate"], t["objective"], t["updated_at"], dumps(t)),
            )
        for e in self.events():
            con.execute("INSERT INTO events VALUES (?,?,?,?,?,?)",
                        (e["event_id"], e["ts"], e["type"], e["task_id"], e["actor"], dumps(e["data"])))
        con.commit()
        con.close()
        return path


_TASK_FIELDS = {
    "task_id", "task_key", "project_id", "product_id", "objective", "owner_agent", "reviewers",
    "status", "priority", "priority_reason", "serves_gate", "risk_class", "privacy_class",
    "depends_on", "inputs", "outputs", "evidence_ids", "acceptance_criteria", "freshness_date",
    "review_status", "preflight", "next_action", "updated_at", "scope", "external_ids",
    "previous_task_id", "notes",
}


def _for_schema(task: dict) -> dict:
    unknown = set(task) - _TASK_FIELDS
    if unknown:
        raise LedgerError(f"unknown task field(s): {sorted(unknown)}")
    return task


def _check_transition(old: dict, new: dict) -> None:
    status = new["status"]
    if status not in STATUSES:
        raise LedgerError(f"unknown status {status}")
    if status == "DONE":
        # PROMPT.md 10.4: done = output exists with hash + evidence attached + review passed.
        if not new.get("outputs"):
            raise LedgerError("DONE needs at least one output with a hash")
        if not new.get("evidence_ids"):
            raise LedgerError("DONE needs evidence_ids")
        if new.get("risk_class") == "CRITICAL" and new.get("review_status") != "PASSED":
            raise LedgerError("CRITICAL task needs review_status PASSED before DONE")
    if old["status"] in FINISHED and status not in FINISHED and not new.get("notes"):
        raise LedgerError("re-opening a finished task needs a notes entry explaining why")


def preflight(task: dict, existing: dict[str, dict], today: date | None = None) -> dict:
    """PROMPT.md 10.3, fully deterministic. Order: definition of done, duplicate, deps, priority."""
    today = today or date.today()
    result = {"checked_at": now_iso(), "reasons": []}

    def done(kind: str, reason: str, **extra) -> dict:
        result.update(result=kind, **extra)
        result["reasons"].append(reason)
        return result

    if not task.get("acceptance_criteria"):
        return done("REJECTED", "no acceptance criteria: definition of done missing")

    norm = normalize_text(task["objective"])
    for other in existing.values():
        if other["task_key"] == task["task_key"] and other["status"] in FINISHED:
            fresh = other.get("freshness_date") is None or date.fromisoformat(other["freshness_date"]) >= today
            if fresh:
                return done("REUSE", f"same task_key already {other['status']} and fresh",
                            reused_task_id=other["task_id"])
            task["previous_task_id"] = other["task_id"]
            result["reasons"].append(f"{other['task_id']} is stale; redo as delta")
            result["result"] = "DELTA"
            break
        if other["task_key"] == task["task_key"] and other["status"] not in {"FAILED", "SKIPPED_NOT_APPLICABLE"}:
            return done("REUSE", f"same task_key already open as {other['task_id']} ({other['status']})",
                        reused_task_id=other["task_id"])
        if (normalize_text(other["objective"]) == norm and other["product_id"] == task["product_id"]
                and other["status"] in FINISHED):
            task["previous_task_id"] = other["task_id"]
            result["reasons"].append(f"inputs changed since {other['task_id']}; redo only the delta")
            result["result"] = "DELTA"

    missing = [d for d in task.get("depends_on", []) if existing.get(d, {}).get("status") not in FINISHED]
    if missing:
        return done("BLOCKED", f"dependencies not DONE/VERIFIED: {missing}")

    if task.get("priority") not in {"MUST", "SHOULD"}:
        return done("PARKED", f"priority {task.get('priority')} is not MUST/SHOULD for the current gate")

    result.setdefault("result", "RUN")
    if result["result"] == "RUN":
        result["reasons"].append("new task, dependencies met, priority ok")
    return result
