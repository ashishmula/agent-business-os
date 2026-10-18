"""Hashing, time, IDs and the file lock shared by every writer."""

from __future__ import annotations

import fcntl
import hashlib
import json
import re
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from . import REPO_ROOT

LOCK_PATH = REPO_ROOT / "state" / ".write.lock"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(Path(path).read_bytes())


def normalize_text(text: str) -> str:
    """Lowercase, collapse whitespace and drop punctuation so trivial rewording matches."""
    text = re.sub(r"[^\w\s]", " ", text.lower())
    return re.sub(r"\s+", " ", text).strip()


def task_key(objective: str, scope: str, product_id: str, input_hashes: list[str]) -> str:
    """Dedup key from PROMPT.md 10.3: same objective + scope + product + inputs => same key."""
    parts = [normalize_text(objective), normalize_text(scope), product_id, *sorted(input_hashes)]
    return sha256_bytes("|".join(parts).encode())


def dumps(obj) -> str:
    """Stable JSON for hashing and append-only logs."""
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


@contextmanager
def write_lock(lock_path: Path | None = None):
    """Exclusive lock around every change to shared state (one writer at a time)."""
    lock_path = lock_path or LOCK_PATH  # resolved at call time so tests and tools can redirect it
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with open(lock_path, "w") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)
