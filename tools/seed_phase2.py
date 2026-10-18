"""One-off: record Phase 1 and Phase 2 work in the ledger (2026-10-18). Kept for provenance; safe to
re-run because the pre-flight check reuses tasks that already exist."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from abos import REPO_ROOT, board  # noqa: E402
from abos.ledger import Ledger  # noqa: E402
from abos.util import sha256_file  # noqa: E402

L = Ledger()
BASE = {"project_id": "COFFEE-PROTEIN-OS", "product_id": "PRD-PLATFORM"}


def ref(rel: str) -> dict:
    return {"artifact_id": Path(rel).name, "path_or_uri": rel, "version_or_hash": sha256_file(REPO_ROOT / rel)}


def add(**spec):
    task, pre = L.create_task({**BASE, **spec})
    print(task["task_id"], pre["result"], spec["objective"][:60])
    return task["task_id"]


def finish(task_id, outputs, evidence, **extra):
    t = L.get(task_id)
    if t["status"] != "DONE":
        L.update(task_id, {"status": "DONE", "outputs": outputs, "evidence_ids": evidence, **extra})


# Muse handoffs TASK-0001/0002 were created by `abos handoff receive`; close them.
acks = sorted((REPO_ROOT / "handoffs" / "acks").glob("ACK-*.json"))
for task_id in ("TASK-0001", "TASK-0002"):
    t = L.get(task_id)
    ack = next(a for a in acks if json.loads(a.read_text()).get("ledger_task_id") == task_id)
    finish(task_id, [ref(t["inputs"][0]["path_or_uri"]), ref(str(ack.relative_to(REPO_ROOT)))], t["evidence_ids"],
           next_action="Ask Muse to include security_or_privacy_notes and inputs_read_sha256 in future packets")

test_record = sorted((REPO_ROOT / "test-results" / "unit").glob("*.json"))[-1]
test_id = json.loads(test_record.read_text())["test_id"]

p1 = add(objective="Phase 1 research and architecture report", owner_agent="orchestrator", priority="MUST",
         priority_reason="approval gate for everything after it", serves_gate="G0-phase-1-approval",
         risk_class="CRITICAL", scope="reports/phase-1",
         acceptance_criteria=["Section 8 + 9.6 + 10.7 deliverables present", "Ashish approval", "independent review"])
L.update(p1, {"status": "REVIEW", "review_status": "PENDING",
              "outputs": [ref("reports/phase-1/README.md")],
              "evidence_ids": ["SRC-0001"],
              "notes": "Approved by Ashish 2026-10-18 (APR-0001). Independent challenger review by Muse (P1-MUSE-03) pending.",
              "next_action": "Ashish sends reports/phase-1 to Muse for challenger review P1-MUSE-03"})

p2a = add(objective="Phase 2a backbone: ledger, pre-flight, handoff intake, status board, schemas, config, secret scan",
          owner_agent="builder", reviewers=["tester-a", "tester-b", "tester-c"], priority="MUST",
          priority_reason="every later task depends on records", serves_gate="G1-phase-2", scope="tools/abos",
          depends_on=[p1] if L.get(p1)["status"] in ("DONE", "VERIFIED") else [],
          acceptance_criteria=["42 unit tests pass on the Mac", "Muse packets ingested", "status board generated"])
finish(p2a, [ref("tools/abos/ledger.py"), ref("tools/abos/handoff.py"), ref(str(test_record.relative_to(REPO_ROOT)))],
       [test_id], next_action="Start Phase 2b")

add(objective="Phase 2b Governor: status line script and hooks write the usage ledger and context fill",
    owner_agent="builder", priority="MUST", priority_reason="Pro plan limits are tight; needed before heavy work",
    serves_gate="G1-phase-2", depends_on=[p2a],
    acceptance_criteria=["status line JSON -> usage ledger row", "PreCompact writes checkpoint",
                         "first daily usage report with >=95% attribution"],
    next_action="Write .claude statusline script + Stop/SubagentStop/PreCompact/SessionStart hooks")
add(objective="Phase 2b security hooks: PreToolUse deny-list, block reads of private/, approval check for external actions",
    owner_agent="builder", priority="MUST", priority_reason="closes the convention-only rules in SECURITY.md",
    serves_gate="G1-phase-2", depends_on=[p2a], risk_class="CRITICAL",
    acceptance_criteria=["forbidden command exits 2 and is logged", "Read under private/ denied"],
    next_action="Write .claude/settings.json hooks + scripts, test each")
add(objective="Phase 2c subagent definitions (builder, testers A/B/C, security reviewer) with model and tool allowlists",
    owner_agent="builder", priority="SHOULD", priority_reason="needed for the developer + 3 testers loop",
    serves_gate="G1-phase-2", depends_on=[p2a],
    acceptance_criteria=["agent with Read/Grep only cannot Write", "each agent's model matches routing rules"])
add(objective="Phase 2c Ollama capacity check and golden tasks for qwen2.5:3b",
    owner_agent="builder", priority="SHOULD", priority_reason="decides whether T1 exists on an 8 GB M1",
    serves_gate="G1-phase-2", depends_on=[p2a], privacy_class="PRIVATE",
    acceptance_criteria=["20 golden extraction items scored", "RAM and tokens/sec measured", "T1 on or NOT_NOW recorded"])
add(objective="LangGraph workflow for the developer + 3 testers loop with SQLite checkpoints",
    owner_agent="builder", priority="COULD", priority_reason="add only when a checkpointed multi-step run is needed (DEC-0001)",
    serves_gate="G1-phase-2", acceptance_criteria=["kill mid-run resumes at same step"])
push = add(objective="Push Phase 2 branch to GitHub", owner_agent="orchestrator", priority="SHOULD",
    priority_reason="off-machine backup of the canonical repo", serves_gate="G1-phase-2", depends_on=[p2a],
    acceptance_criteria=["branch visible on github.com/ashishmula/agent-business-os"],
    next_action="Waiting for Ashish to approve the push")
if L.get(push)["status"] == "NOT_STARTED":
    L.update(push, {"status": "WAITING_FOR_APPROVAL"})

board.write(L)
print(L.verify_chain() or "chain OK")
