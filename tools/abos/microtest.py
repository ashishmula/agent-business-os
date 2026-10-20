"""Micro-test scorer (R10 §3.3). T0, no LLM: turns event tallies into PASS / FAIL per gate.

Input is a CSV with one row per tasting sample or ad-test day, never per person's identity:
  kind,event,score,scanned,signed_up,prefers,reinvite,spend_cad
- kind: "taste" (one sampler) or "ads" (one day of the step-0 ad test)
- score: 1-5 or blank; scanned / signed_up / reinvite: 0 or 1; prefers: can, pouch or blank
- ads rows put the day's sign-ups in signed_up and spend in spend_cad

Invariants: refuses columns that look like personal data; a gate with no data is
NOT_TESTED, never PASS; a missing or bad value fails loudly instead of counting as zero.
"""

from __future__ import annotations

import csv
import tomllib
from pathlib import Path

from . import REPO_ROOT

COLUMNS = ["kind", "event", "score", "scanned", "signed_up", "prefers", "reinvite", "spend_cad"]


class MicrotestError(ValueError):
    pass


def load_config(path: Path | None = None) -> dict:
    with open(path or REPO_ROOT / "config" / "microtest.toml", "rb") as handle:
        return tomllib.load(handle)


def _flag(value: str, field: str, line: int) -> int:
    if value.strip() in ("", "0"):
        return 0
    if value.strip() == "1":
        return 1
    raise MicrotestError(f"line {line}: {field} must be 0 or 1, got {value!r}")


def read_rows(path: Path, cfg: dict) -> list[dict]:
    with open(path, newline="") as handle:
        reader = csv.DictReader(handle)
        header = [h.strip().lower() for h in reader.fieldnames or []]
        bad = sorted(set(header) & set(cfg["privacy"]["forbidden_columns"]))
        if bad:
            raise MicrotestError(f"personal-data columns not allowed in the repo: {', '.join(bad)}")
        unknown = sorted(set(header) - set(COLUMNS))
        if unknown:
            raise MicrotestError(f"unknown columns: {', '.join(unknown)}")
        rows = []
        for line, raw in enumerate(reader, start=2):
            raw = {k.strip().lower(): (v or "") for k, v in raw.items()}
            kind = raw.get("kind", "").strip()
            if kind not in ("taste", "ads"):
                raise MicrotestError(f"line {line}: kind must be taste or ads, got {kind!r}")
            score = raw.get("score", "").strip()
            if score and score not in ("1", "2", "3", "4", "5"):
                raise MicrotestError(f"line {line}: score must be 1-5, got {score!r}")
            prefers = raw.get("prefers", "").strip().lower()
            if prefers not in ("", "can", "pouch"):
                raise MicrotestError(f"line {line}: prefers must be can, pouch or blank")
            try:
                spend = float(raw.get("spend_cad", "").strip() or 0)
                signed = int(raw.get("signed_up", "").strip() or 0)
            except ValueError as exc:
                raise MicrotestError(f"line {line}: {exc}") from None
            if spend < 0 or signed < 0:
                raise MicrotestError(f"line {line}: negative values not allowed")
            if kind == "taste" and signed > 1:
                raise MicrotestError(f"line {line}: a taste row is one sampler, signed_up must be 0 or 1")
            rows.append({"kind": kind, "event": raw.get("event", "").strip(), "score": int(score) if score else None,
                         "scanned": _flag(raw.get("scanned", ""), "scanned", line), "signed_up": signed,
                         "prefers": prefers, "reinvite": _flag(raw.get("reinvite", ""), "reinvite", line),
                         "spend_cad": spend})
    return rows


def _gate(name: str, value, target: str, ok: bool | None) -> dict:
    return {"gate": name, "value": value, "target": target,
            "result": "NOT_TESTED" if ok is None else ("PASS" if ok else "FAIL")}


def score(rows: list[dict], cfg: dict) -> dict:
    taste = [r for r in rows if r["kind"] == "taste"]
    ads = [r for r in rows if r["kind"] == "ads"]
    m, s = cfg["micro"], cfg["step0"]
    gates = []

    n = len(taste)
    gates.append(_gate("samplers", n, f">= {m['min_samplers']}", n >= m["min_samplers"] if n else None))
    scan = sum(r["scanned"] for r in taste) / n if n else None
    gates.append(_gate("scan_rate", None if scan is None else round(scan, 3), f">= {m['min_scan_rate']}",
                       None if scan is None else scan >= m["min_scan_rate"]))
    sign = sum(r["signed_up"] for r in taste) / n if n else None
    gates.append(_gate("signup_rate", None if sign is None else round(sign, 3), f">= {m['min_signup_rate']}",
                       None if sign is None else sign >= m["min_signup_rate"]))
    events_reinvited = len({r["event"] for r in taste if r["reinvite"] and r["event"]})
    gates.append(_gate("organizer_reinvites", events_reinvited, f">= {m['min_reinvites']}",
                       events_reinvited >= m["min_reinvites"] if n else None))
    scored = [r["score"] for r in taste if r["score"] is not None]
    if len(scored) < m["min_scored_tasters"]:
        gates.append(_gate("taste_top_box", len(scored), f">= {m['min_scored_tasters']} scored tasters", None))
    else:
        share = sum(1 for x in scored if x >= 4) / len(scored)
        gates.append(_gate("taste_top_box", round(share, 3), f">= {m['min_top_box_share']}",
                           share >= m["min_top_box_share"]))

    spend = sum(r["spend_cad"] for r in ads)
    signups = sum(r["signed_up"] for r in ads)
    if ads:
        gates.append(_gate("ads_spend_cap", round(spend, 2), f"<= {s['max_spend_cad']}", spend <= s["max_spend_cad"]))
        gates.append(_gate("ads_signups", signups, f">= {s['min_signups']}", signups >= s["min_signups"]))
        cps = spend / signups if signups else None
        gates.append(_gate("ads_cost_per_signup", None if cps is None else round(cps, 2),
                           f"<= {s['max_cost_per_signup_cad']}",
                           False if cps is None else cps <= s["max_cost_per_signup_cad"]))

    prefs = {"can": sum(1 for r in taste if r["prefers"] == "can"),
             "pouch": sum(1 for r in taste if r["prefers"] == "pouch")}
    results = [g["result"] for g in gates]
    overall = "FAIL" if "FAIL" in results else ("NOT_TESTED" if "NOT_TESTED" in results else "PASS")
    return {"overall": overall, "gates": gates, "format_preference": prefs}


def run_cli(csv_path: str, config: str | None = None) -> int:
    cfg = load_config(Path(config) if config else None)
    report = score(read_rows(Path(csv_path), cfg), cfg)
    for g in report["gates"]:
        print(f"{g['result']:<11} {g['gate']:<20} {g['value']!s:<8} target {g['target']}")
    print(f"format preference: can {report['format_preference']['can']}, pouch {report['format_preference']['pouch']}")
    print(f"OVERALL: {report['overall']}")
    return {"PASS": 0, "FAIL": 1}.get(report["overall"], 3)
