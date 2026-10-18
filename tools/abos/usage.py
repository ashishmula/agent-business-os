"""Usage report from the status-line snapshots (PROMPT.md 9.2.4). T0, no LLM.

Each snapshot carries cumulative session totals, so the tokens between two snapshots are
charged to the task, agent and model of the later one. Writes usage-ledger rows
(usage.schema v1.0) plus a readable report per day.
"""

from __future__ import annotations

import csv
import json
import tomllib
from collections import defaultdict
from pathlib import Path

from . import REPO_ROOT, schema
from .util import dumps

SESSIONS = REPO_ROOT / "state" / "context-sessions"
USAGE_LEDGER = REPO_ROOT / "state" / "usage-ledger"
REPORTS = REPO_ROOT / "reports" / "usage"


def _tiers(registry: Path) -> dict[str, str]:
    try:
        with open(registry, "rb") as handle:
            models = tomllib.load(handle)["model"]
    except (OSError, KeyError, tomllib.TOMLDecodeError):
        return {}
    return {m["id"]: m["tier"] for m in models}


def _tier(model: str | None, tiers: dict[str, str]) -> str:
    for mid, tier in tiers.items():
        if model and model.startswith(mid):
            return tier
    return "T4"  # unknown cloud model: assume the expensive tier so it is never under-counted


def _delta(now, before) -> int:
    if not isinstance(now, int):
        return 0
    return max(now - (before if isinstance(before, int) else 0), 0)


def rows(sessions_dir: Path = SESSIONS, registry: Path = REPO_ROOT / "config" / "model-registry.toml") -> list[dict]:
    tiers = _tiers(registry)
    out = []
    for path in sorted(sessions_dir.glob("*.jsonl")):
        snaps = sorted((json.loads(line) for line in path.read_text().splitlines() if line.strip()),
                       key=lambda s: s.get("ts") or "")
        prev: dict = {}
        for snap in snaps:
            if prev and (snap.get("total_input_tokens") or 0) < (prev.get("total_input_tokens") or 0):
                prev = {}  # counters went down: treat as a new session segment, never negative
            row = {
                "usage_schema_version": "1.0",
                "timestamp": snap["ts"],
                "environment": "CLAUDE_CODE",
                "session_id": snap.get("session_id") or path.stem,
                "agent": snap.get("agent") or "main",
                "task_id": snap.get("task_id") or "UNATTRIBUTED",
                "model": snap.get("model") or "unknown",
                "tier": _tier(snap.get("model"), tiers),
                "input_tokens": _delta(snap.get("total_input_tokens"), prev.get("total_input_tokens")),
                "output_tokens": _delta(snap.get("total_output_tokens"), prev.get("total_output_tokens")),
                "measurement": "MEASURED",
                "source": "STATUSLINE",
            }
            if isinstance(snap.get("context_fill_pct"), (int, float)):
                row["context_fill_pct"] = snap["context_fill_pct"]
            cost, before = snap.get("cost_usd_list_price"), prev.get("cost_usd_list_price")
            if isinstance(cost, (int, float)):
                row["cost_or_usage_estimate"] = f"USD {max(cost - (before or 0), 0):.4f} list price (not billed on Pro)"
            errors = schema.check(row, "usage")
            if errors:
                raise ValueError(f"usage row from {path.name} invalid: {errors}")
            if row["input_tokens"] or row["output_tokens"]:
                out.append(row)
            prev = snap
    return out


def summarize(day_rows: list[dict]) -> dict:
    total = sum(r["input_tokens"] + r["output_tokens"] for r in day_rows)
    attributed = sum(r["input_tokens"] + r["output_tokens"] for r in day_rows if r["task_id"] != "UNATTRIBUTED")
    by = defaultdict(lambda: defaultdict(int))
    for r in day_rows:
        for key in ("task_id", "agent", "model", "session_id"):
            by[key][r[key]] += r["input_tokens"] + r["output_tokens"]
    return {"total_tokens": total, "attributed_pct": round(100 * attributed / total, 1) if total else None,
            "by": {k: dict(sorted(v.items(), key=lambda kv: -kv[1])) for k, v in by.items()}}


def report(sessions_dir: Path = SESSIONS, ledger_dir: Path = USAGE_LEDGER, reports_dir: Path = REPORTS) -> list[Path]:
    """Rebuild usage-ledger files and per-day reports. Deterministic: re-running gives the same files."""
    days = defaultdict(list)
    for r in rows(sessions_dir):
        days[r["timestamp"][:10]].append(r)
    written = []
    ledger_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)
    for day, day_rows in sorted(days.items()):
        led = ledger_dir / f"usage-{day}.jsonl"
        led.write_text("".join(dumps(r) + "\n" for r in day_rows))
        with open(reports_dir / f"{day}.csv", "w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["timestamp", "session_id", "agent", "task_id", "model", "tier",
                                                        "input_tokens", "output_tokens", "context_fill_pct"],
                                    extrasaction="ignore")
            writer.writeheader()
            writer.writerows(day_rows)
        s = summarize(day_rows)
        lines = [f"# Usage {day}", "",
                 f"Source: Claude Code status line snapshots (MEASURED). Rows: {len(day_rows)}. "
                 f"Tokens: {s['total_tokens']:,}. Attributed to a task: "
                 f"{'n/a' if s['attributed_pct'] is None else str(s['attributed_pct']) + '%'} (target >= 95%).", "",
                 "Muse and Ollama usage are not in this report yet (Muse is ESTIMATED per handoff bundle).", ""]
        for key, title in (("task_id", "By task"), ("agent", "By agent"), ("model", "By model"), ("session_id", "By session")):
            lines += [f"## {title}", "", "| | tokens |", "|---|---:|"]
            lines += [f"| {k} | {v:,} |" for k, v in s["by"][key].items()] + [""]
        md = reports_dir / f"{day}.md"
        md.write_text("\n".join(lines))
        written += [led, md, reports_dir / f"{day}.csv"]
    return written
