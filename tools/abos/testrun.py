"""Deterministic test runner (PROMPT.md section 5): exact command, versions, exit status,
raw output and hashes, stored once and never edited. A rerun gets a new record."""

from __future__ import annotations

import platform
import subprocess
import sys

from . import REPO_ROOT, __version__, schema
from .util import dumps, now_iso, sha256_bytes

RESULTS = REPO_ROOT / "test-results" / "unit"


def _git_head() -> str:
    out = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, capture_output=True, text=True)
    dirty = subprocess.run(["git", "status", "--porcelain"], cwd=REPO_ROOT, capture_output=True, text=True)
    return (out.stdout.strip() or "no-git") + ("+dirty" if dirty.stdout.strip() else "")


def run() -> dict:
    command = [sys.executable, "-m", "unittest", "discover", "-s", "tests/unit", "-v"]
    proc = subprocess.run(command, cwd=REPO_ROOT, capture_output=True, text=True)
    raw = (proc.stdout + proc.stderr).encode()
    stamp = now_iso().replace(":", "").replace("-", "")
    RESULTS.mkdir(parents=True, exist_ok=True)
    raw_path = RESULTS / f"{stamp}.log"
    raw_path.write_bytes(raw)

    tail = raw.decode(errors="ignore").strip().splitlines()[-3:]
    record = {
        "test_id": "TEST-" + stamp.replace("T", "").replace("Z", "")[:14],
        "run_at": now_iso(),
        "tester_role": "SUITE",  # one run covers tester A/B/C files; split per role in the testers loop
        "command": " ".join(command[1:]),
        "software_versions": {"python": platform.python_version(), "abos": __version__,
                              "os": platform.platform()},
        "exit_status": proc.returncode,
        "result": "PASS" if proc.returncode == 0 else "FAIL",
        "raw_output_path": str(raw_path.relative_to(REPO_ROOT)),
        "raw_output_hash": sha256_bytes(raw),
        "subject_hash": _git_head(),
        "linked_defect": None,
        "supersedes": None,
    }
    errors = schema.check(record, "test-result")
    if errors:
        raise ValueError(f"test record fails schema: {errors}")
    (RESULTS / f"{stamp}.json").write_text(dumps(record) + "\n")
    print("\n".join(tail))
    return record
