"""Phase report: ./abos phase-report <gate> [--write PATH] [--force]. Read-only summary of a gate's tasks (T0, no LLM).

--write is confined to reports/ inside the repo. Every echoed value is sanitised to one short line.
"""

from __future__ import annotations

import json
import os
import re
import stat
import sys
import tempfile
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from . import REPO_ROOT
from .ledger import Ledger
from .util import now_iso, sha256_bytes

RESULTS = REPO_ROOT / "test-results" / "unit"
REPORTS_DIR = "reports"
FIELD_MAX = 80
GATE_MAX = 60
_MD_BREAK = re.compile(r"[|`<>\[\]\\*_#~]")
_TOKEN = re.compile(r"[A-Z][A-Z0-9_-]{0,39}")  # statuses and task ids: plain tokens kept as-is
RECORD_MAX_BYTES = 1_000_000


class ReportError(Exception):
    """A user-facing problem; message is one line."""


def clean(value, limit: int = FIELD_MAX) -> str:
    """One short line: control chars/newlines removed, whitespace collapsed, capped."""
    text = "".join(" " if unicodedata.category(c) in ("Cc", "Cf", "Zl", "Zp") else c for c in str(value))
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 3] + "..."


def clean_md(value, limit: int = FIELD_MAX) -> str:
    """clean() plus table/markdown-breaking characters replaced, for echoing untrusted names."""
    return _MD_BREAK.sub("?", clean(value, limit))


def clean_token(value, limit: int = 40) -> str:
    """Plain upper-case tokens (NOT_STARTED, TASK-0018) pass unchanged; anything else goes through clean_md."""
    text = clean(value, limit)
    return text if _TOKEN.fullmatch(text) else clean_md(value, limit)


def safe_target(raw: str, root: Path = REPO_ROOT) -> Path:
    """Validate a --write target: under <root>/reports/, no symlinks, no '..', never private/."""
    if not isinstance(raw, str) or not raw.strip():
        raise ReportError("--write needs a non-empty path under reports/")
    if "\x00" in raw:
        raise ReportError("--write path contains a NUL byte")
    root = Path(os.path.realpath(root))
    p = Path(raw)
    if ".." in p.parts:
        raise ReportError("--write path may not contain '..'")
    target = Path(os.path.abspath(p if p.is_absolute() else Path.cwd() / p))
    rel = None
    for anc in (*reversed(target.parents), target):  # shallowest first; match by real identity so aliased prefixes (e.g. /tmp) still work
        if os.path.realpath(anc) == str(root):
            rel = target.relative_to(anc)
            break
    if rel is None:
        raise ReportError(f"--write must be inside the repo under {REPORTS_DIR}/")
    if not rel.parts or rel.parts[0] != REPORTS_DIR or len(rel.parts) < 2:
        raise ReportError(f"--write must be a file under {REPORTS_DIR}/")
    if "private" in rel.parts:
        raise ReportError("--write may not target private/")
    cur = root
    for part in rel.parts:
        cur = cur / part
        if cur.is_symlink():
            raise ReportError("--write path may not include symlinks")
    if not cur.parent.is_dir():
        raise ReportError(f"--write parent directory does not exist: {clean(rel.parent, 120)}")
    if cur.is_dir():
        raise ReportError("--write target is a directory")
    return cur


def write_report(target: Path, text: str, force: bool = False) -> None:
    """Write without following a symlink; refuse to overwrite unless force. Raises ReportError."""
    try:
        if not force:
            fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o644)
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                fh.write(text)
            return
        try:
            mode = stat.S_IMODE(os.lstat(target).st_mode)  # keep the original file's mode
        except OSError:
            mode = 0o644
        fd, tmp = tempfile.mkstemp(dir=target.parent, prefix=".phase-report-")
        try:
            os.fchmod(fd, mode)
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                fh.write(text)
            os.replace(tmp, target)  # replaces the name itself, never writes through a link
        except BaseException:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise
    except FileExistsError:
        raise ReportError(f"refusing to overwrite existing {clean(target.name)} (use --force)") from None
    except OSError as exc:
        raise ReportError(f"cannot write report: {clean(exc.strerror or type(exc).__name__)}") from None


def _log_ok(raw_path, want_hash, base: Path, results_dir: Path) -> bool:
    """True if raw_path resolves inside results_dir (no '..', no symlinks), is a regular file, and hashes to want_hash."""
    if not isinstance(raw_path, str) or not raw_path or "\x00" in raw_path or not isinstance(want_hash, str):
        return False
    rp = Path(raw_path)
    if ".." in rp.parts:
        return False
    rd = Path(os.path.realpath(results_dir))
    cand = Path(os.path.abspath(rp if rp.is_absolute() else Path(os.path.realpath(base)) / rp))
    rel = None
    for anc in (*reversed(cand.parents), cand):  # match by real identity so aliased prefixes (e.g. /tmp) work
        if os.path.realpath(anc) == str(rd):
            rel = cand.relative_to(anc)
            break
    if rel is None:
        return False
    if not rel.parts:
        return False
    cur = rd
    for part in rel.parts:
        cur = cur / part
        if cur.is_symlink():
            return False
    try:
        if not stat.S_ISREG(os.lstat(cur).st_mode):
            return False
        fd = os.open(cur, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
        with os.fdopen(fd, "rb") as fh:
            digest = sha256_bytes(fh.read())
    except OSError:
        return False
    return digest == want_hash


def _valid_record(p: Path, base: Path, results_dir: Path) -> dict | None:
    """The parsed record if every trust check passes, else None."""
    try:
        st = os.lstat(p)
        if not stat.S_ISREG(st.st_mode) or st.st_size >= RECORD_MAX_BYTES:
            return None
        fd = os.open(p, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
        with os.fdopen(fd, "rb") as fh:
            rec = json.loads(fh.read(RECORD_MAX_BYTES).decode("utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(rec, dict) or not isinstance(rec.get("test_id"), str):
        return None
    if rec.get("result") not in ("PASS", "FAIL"):
        return None
    es = rec.get("exit_status")
    if not isinstance(es, int) or isinstance(es, bool):
        return None
    if (es == 0) != (rec["result"] == "PASS"):  # tester C round 3: result must agree with exit_status
        return None
    when = parse_utc(rec.get("run_at"))
    if when is None or when > datetime.now(timezone.utc):
        return None
    if not _log_ok(rec.get("raw_output_path"), rec.get("raw_output_hash"), base, results_dir):
        return None
    rec["_when"] = when
    return rec


def parse_utc(value) -> datetime | None:
    """Aware UTC datetime from an ISO string ending in Z or +00:00, else None."""
    if not isinstance(value, str) or len(value) > 40:
        return None
    try:
        dt = datetime.fromisoformat(value[:-1] + "+00:00" if value.endswith("Z") else value)
    except ValueError:
        return None
    if dt.tzinfo is None or dt.utcoffset() != timezone.utc.utcoffset(None):
        return None
    return dt.astimezone(timezone.utc)


def latest_test(results_dir: Path = RESULTS, root: Path = REPO_ROOT) -> tuple[dict | None, int]:
    """(newest trusted unit test record by run_at or None, number of *.json records skipped as untrusted)."""
    records, skipped = [], 0
    d = Path(results_dir)
    try:
        paths = sorted(d.glob("*.json")) if d.is_dir() else []
    except OSError:
        paths = []
    for p in paths:
        rec = _valid_record(p, root, d)
        if rec is None:
            skipped += 1
        else:
            records.append(rec)
    return max(records, key=lambda r: r["_when"], default=None), skipped


def build(ledger: Ledger, gate: str, results_dir: Path = RESULTS, root: Path = REPO_ROOT) -> str | None:
    """Report text for the gate, or None if no task serves that gate."""
    tasks = [t for t in ledger.tasks().values() if t.get("serves_gate") == gate]
    if not tasks:
        return None
    counts = Counter(clean_token(t.get("status", "?"), 40) for t in tasks)
    lines = [f"# Phase report: {clean_md(gate, GATE_MAX)}", "",
             f"Generated {now_iso()} from the task ledger. Tasks: {len(tasks)}", "", "## Counts by status"]
    lines += [f"- {s}: {n}" for s, n in sorted(counts.items())]
    lines += ["", "## Latest unit test record"]
    rec, skipped = latest_test(results_dir, root)
    if rec:
        lines.append(f"- {clean_token(rec['test_id'], 40)}: {clean_token(rec.get('result'), 20)} "
                     f"(run {clean_md(rec.get('run_at'), 30)}, subject {clean_md(rec.get('subject_hash'), 20)})")
    else:
        lines.append("- NOT_TESTED: no unit test record found")
    lines.append(f"- Untrusted test records skipped: {skipped}")
    lines += ["", "## NOT_TESTED or no evidence"]
    flagged = [t for t in tasks if t.get("status") == "NOT_TESTED" or not t.get("evidence_ids")]
    if flagged:
        for t in flagged:
            why = "status NOT_TESTED" if t.get("status") == "NOT_TESTED" else "no evidence_ids"
            if t.get("status") == "NOT_TESTED" and not t.get("evidence_ids"):
                why += ", no evidence_ids"
            lines.append(f"- {clean_token(t.get('task_id'), 20)} [{clean_token(t.get('status'), 40)}] "
                         f"{clean_md(t.get('objective', ''))} ({why})")
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def run_cli(ledger: Ledger, gate: str, write: str | None = None, force: bool = False,
            root: Path = REPO_ROOT, results_dir: Path = RESULTS) -> int:
    """Exit codes: 0 ok, 1 unknown gate, 2 bad ledger/input/target. Never raises."""
    try:
        if write is not None:
            target = safe_target(write, root)  # validate before doing any work
        if not ledger.events_path.exists() or not ledger.events_path.read_text(encoding="utf-8").strip():
            raise ReportError("ledger is missing or empty; nothing to report")
        problems = ledger.verify_chain()
        if problems:
            raise ReportError(f"ledger verify failed ({len(problems)} problem(s)): {clean(problems[0], 120)}; "
                              "run ./abos ledger verify")
        text = build(ledger, gate, results_dir, root)
        if text is None:
            print(f"unknown gate: {clean_md(gate, GATE_MAX)} (no ledger task has that serves_gate)", file=sys.stderr)
            return 1
        if write is not None:
            write_report(target, text, force)
        print(text, end="")
        return 0
    except ReportError as exc:
        print(f"phase-report error: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # malformed ledger/result data must never produce a traceback
        print(f"phase-report error: could not read ledger or inputs ({type(exc).__name__}: {clean(exc, 100)})",
              file=sys.stderr)
        return 2
