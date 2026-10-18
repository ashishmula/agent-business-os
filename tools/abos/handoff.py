"""Receive a handoff bundle from another environment (PROMPT.md section 4 receiver protocol).

Steps: secret scan -> parse -> normalize allowed gaps -> schema check -> instruction scan
-> input freshness -> evidence mapping -> store as received + ACK record -> ledger task.
Rejected bundles are never stored in the inbox, only reported, so a leaked key or a
poisoned packet does not reach git.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from . import REPO_ROOT, schema
from .ledger import Ledger
from .secrets import scan_text
from .util import dumps, now_iso, sha256_bytes, sha256_file

INBOX = REPO_ROOT / "handoffs" / "inbox"
ACKS = REPO_ROOT / "handoffs" / "acks"

# Section 4 list fields a sender may omit; filled with [] and reported as a warning.
DEFAULTABLE = ("security_or_privacy_notes", "known_failures", "untested_gaps")


def receive(path: Path, ledger: Ledger | None = None, repo: Path = REPO_ROOT,
            product_id: str = "PRD-PLATFORM", create_task: bool = True) -> dict:
    ledger = ledger or Ledger()
    raw = Path(path).read_bytes()
    ack = {
        "ack_schema_version": "1.0",
        "received_at": now_iso(),
        "source_file": Path(path).name,
        "sha256": sha256_bytes(raw),
        "warnings": [],
        "errors": [],
        "checks": {},
    }

    secrets = scan_text(raw.decode(errors="ignore"), "secrets")
    ack["checks"]["secret_scan"] = "FAIL" if secrets else "PASS"
    if secrets:
        ack["errors"].append(f"secret-like content found ({[h['rule'] for h in secrets]}); bundle not stored")
        return _finish(ack, "REJECTED")

    try:
        bundle = json.loads(raw)
    except json.JSONDecodeError as exc:
        ack["checks"]["json_parse"] = "FAIL"
        ack["errors"].append(f"not valid JSON (truncated or edited?): {exc}")
        return _finish(ack, "REJECTED")
    ack["checks"]["json_parse"] = "PASS"
    ack["task_id_external"] = bundle.get("task_id")

    if bundle.get("handoff_schema_version") != "1.0":
        ack["errors"].append(f"unsupported handoff_schema_version {bundle.get('handoff_schema_version')!r}")
        return _finish(ack, "REJECTED")

    for field in DEFAULTABLE:
        if field not in bundle:
            bundle[field] = []
            ack["warnings"].append(f"'{field}' missing; treated as none declared")

    errors = schema.check(bundle, "handoff")
    ack["checks"]["schema"] = "FAIL" if errors else "PASS"
    if errors:
        ack["errors"].extend(errors)
        return _finish(ack, "REJECTED")

    flagged = scan_text(raw.decode(errors="ignore"), "instructions")
    ack["checks"]["instruction_scan"] = "FLAGGED" if flagged else "PASS"
    if flagged:
        ack["warnings"].append(f"instruction-like text flagged, stored as data only: {[h['rule'] for h in flagged]}")

    stale = []
    for rel, claimed in bundle.get("inputs_read_sha256", {}).items():
        target = repo / rel
        actual = sha256_file(target) if target.exists() else None
        if actual != claimed:
            stale.append(rel)
    if "inputs_read_sha256" not in bundle:
        ack["checks"]["input_freshness"] = "NOT_VERIFIED"
        ack["warnings"].append("no inputs_read_sha256; cannot prove which repo version the sender read")
    else:
        ack["checks"]["input_freshness"] = "FAIL" if stale else "PASS"
    if stale:
        ack["errors"].append(f"sender read an outdated version of: {stale}")
        return _finish(ack, "BLOCKED")

    ack["evidence_map"] = {
        eid: (eid if re.fullmatch(r"(SRC|TEST)-\d{4,}", eid) else f"EXT-{_env_tag(bundle)}-{sha256_bytes(eid.encode())[:8]}")
        for eid in bundle["evidence_ids"]
    }

    INBOX.mkdir(parents=True, exist_ok=True)
    stored = INBOX / f"{bundle['task_id']}.{ack['sha256'][:8]}.json"
    stored.write_bytes(raw)  # byte-for-byte as received
    ack["stored_as"] = str(stored.relative_to(repo))

    if create_task:
        task, pre = ledger.create_task({
            "project_id": bundle["project_id"],
            "product_id": bundle.get("product_id", product_id),
            "objective": f"Handoff {bundle['task_id']} from {bundle['from_environment']}: {bundle['objective']}",
            "owner_agent": "orchestrator",
            "priority": "MUST",
            "priority_reason": "incoming handoff must be acknowledged before anyone acts on it",
            "serves_gate": "handoff-intake",
            "inputs": [{"artifact_id": bundle["task_id"], "path_or_uri": ack["stored_as"],
                        "version_or_hash": ack["sha256"]}],
            "acceptance_criteria": ["bundle stored byte-for-byte", "ACK record written", "ledger task created"],
            "external_ids": [bundle["task_id"]],
            "evidence_ids": list(ack["evidence_map"].values()),
            "next_action": bundle.get("next_action", ""),
        })
        ack["ledger_task_id"] = task["task_id"]
        ack["preflight"] = pre["result"]

    return _finish(ack, "ACCEPTED_WITH_WARNINGS" if ack["warnings"] else "ACCEPTED", write=True)


def _env_tag(bundle: dict) -> str:
    return {"DOT_MUSE": "MUSE", "OLLAMA_LOCAL": "OLLAMA", "CLAUDE_CODE": "CC", "HUMAN": "HUMAN"}.get(
        bundle.get("from_environment"), "X")


def _finish(ack: dict, result: str, write: bool = False) -> dict:
    ack["result"] = result
    if write:
        ACKS.mkdir(parents=True, exist_ok=True)
        (ACKS / f"ACK-{ack['task_id_external']}.{ack['sha256'][:8]}.json").write_text(dumps(ack) + "\n")
    return ack
