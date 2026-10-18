"""Model Router (PROMPT.md 9.3). T0, no LLM: picks the tier and subagent for a task from
config/routing-rules.toml, the live budget level and the task's privacy class.

Invariants (tested over every rule and input combination):
- the chosen tier is never below the rule's floor;
- CRITICAL work is never shifted down for budget, and keeps running at budget HARD (reserve);
- PRIVATE content only goes to T0/T1, otherwise BLOCKED (unless an APR-* approval allows cloud);
- T1 is used only for tasks in t1_tasks while t1_enabled.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

from . import REPO_ROOT

TIERS = ["T0", "T1", "T2", "T3", "T4"]
RISK = {"any": 0, "LOW": 1, "STANDARD": 2, "CRITICAL": 3}
LEVELS = ("OK", "SOFT", "HARD")


def load(config_dir: Path | None = None) -> tuple[dict, dict]:
    config_dir = config_dir or REPO_ROOT / "config"
    with open(config_dir / "routing-rules.toml", "rb") as handle:
        rules = tomllib.load(handle)
    with open(config_dir / "budgets.toml", "rb") as handle:
        budgets = tomllib.load(handle)
    return rules, budgets


def budget_level(five_pct: float | None, seven_pct: float | None, budgets: dict) -> str:
    """Worst level across the 5-hour and 7-day windows (same thresholds the prompt nudge uses)."""
    level = "OK"
    for value, key in ((five_pct, "five_hour"), (seven_pct, "seven_day")):
        window = budgets["windows"][key]
        if value is None:
            continue
        if value >= window["hard_pct"]:
            return "HARD"
        if value >= window["soft_pct"]:
            level = "SOFT"
    return level


def _idx(tier: str) -> int:
    return TIERS.index(tier)


def _t1_ok(task: str, cfg: dict) -> bool:
    return bool(cfg.get("t1_enabled")) and task in cfg.get("t1_tasks", [])


def route(task: str, cfg: dict, budgets: dict, *, risk: str | None = None, privacy: str = "INTERNAL",
          budget: str = "OK", failures: int = 0, cloud_approval: str | None = None) -> dict:
    rule = next((r for r in cfg["rule"] if r["task"] == task), None)
    if rule is None:
        return {"task": task, "action": "BLOCKED", "reasons": ["no routing rule for this task type"]}
    if budget not in LEVELS:
        raise ValueError(f"budget must be one of {LEVELS}")
    risk = max(rule["risk"], risk or "any", key=RISK.__getitem__)
    floor, tier = _idx(rule["floor"]), _idx(rule["start_tier"])
    reasons = [f"start {rule['start_tier']}, floor {rule['floor']}, risk {risk}"]
    action = "RUN"
    max_retries = budgets.get("retries", {}).get("max_per_task", 2)

    if TIERS[tier] == "T1" and not _t1_ok(task, cfg):
        tier = _idx("T2")
        reasons.append("T1 not enabled for this task: T2")
    if failures:
        tier = min(tier + failures * cfg["escalation"]["step"], _idx("T4"))
        if TIERS[tier] == "T1" and not _t1_ok(task, cfg):
            tier = _idx("T2")
        reasons.append(f"{failures} failure(s): escalated to {TIERS[tier]}")
        if failures > max_retries:
            action = "ESCALATE_TO_ASHISH"
            reasons.append(f"more than {max_retries} retries: stop and mark FAILED or ask Ashish")
    if budget == "SOFT" and risk != "CRITICAL" and not failures:
        lower = tier - 1
        if lower == _idx("T1") and not _t1_ok(task, cfg):
            lower -= 1
        if lower >= floor:
            tier = lower
            reasons.append(f"budget SOFT: shifted down to {TIERS[tier]}")
        else:
            reasons.append("budget SOFT: already at floor, not shifted")
    if budget == "HARD":
        if risk == "CRITICAL":
            reasons.append("budget HARD: CRITICAL work runs on the reserve")
        elif action == "RUN":
            action = "PAUSE"
            reasons.append("budget HARD: non-critical work paused; tell Ashish what is paused")
    if privacy == "PRIVATE" and tier > _idx("T1") and not cloud_approval:
        if floor <= _idx("T1") and _t1_ok(task, cfg):
            tier = _idx("T1")
            reasons.append("PRIVATE: kept local at T1")
        elif floor == _idx("T0"):
            tier = _idx("T0")
            reasons.append("PRIVATE: kept at T0 (script)")
        else:
            action = "BLOCKED"
            reasons.append("PRIVATE: needs a cloud model; requires an APR-* approval")

    assert tier >= floor, (task, tier, floor)
    agent, env = rule.get("agent", "none"), rule.get("environment", "CLAUDE_CODE")
    if TIERS[tier] == "T1":  # local model; output must pass abos.grounding before use
        agent, env = "none", "OLLAMA_LOCAL"
    return {"task": task, "tier": TIERS[tier], "agent": agent, "environment": env, "risk": risk,
            "action": action, "reasons": reasons}
