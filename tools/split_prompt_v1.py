"""One-off (2026-10-18): split PROMPT v1 into the detail files PROMPT v2-slim loads on demand.

Copies sections word for word; the full v1 text stays at prompt-source/PROMPT-v1-full.md.
Run once from the repo root: python3 tools/split_prompt_v1.py
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "prompt-source" / "PROMPT-v1-full.md"

# target file -> (title, v1 section ids, in order)
PLAN = {
    "agents/orchestrator.md": ("Orchestrator: coordination rules, environments, handoffs, phases and gates",
                               ["1", "2", "3", "4", "8"]),
    "agents/security.md": ("Security: capability audit, approvals and boundaries", ["2A", "7"]),
    "agents/testing.md": ("Testing: developer + testers loop and its memory", ["5"]),
    "agents/business-rules.md": ("Business rules: strategy workstream, brief traceability, product portfolio",
                                 ["6", "6A", "6B"]),
    "agents/governor.md": ("Governor and Router: token, context-window and model-routing governance", ["9"]),
    "agents/memory.md": ("Memory: records, priorities, pre-flight check, status board", ["10"]),
    "agents/tutor.md": ("Tutor mode: how to explain, flag and push back", ["11"]),
    "agents/sources.md": ("Seed reference links (verify before use)", ["links", "links9"]),
}


def sections(text: str) -> dict[str, str]:
    """Split v1 into its top-level sections, keyed by number ("1", "2A", ...) or by link-list name."""
    out, key, buf = {}, None, []
    for line in text.splitlines(keepends=True):
        m = re.match(r"## (\d+[A-Z]?)\. ", line)
        if m or line.startswith("# Shared reference links") or line.startswith("## Additional seed links"):
            if key:
                out[key] = "".join(buf)
            key = m.group(1) if m else ("links" if line.startswith("# Shared") else "links9")
            buf = []
        if key:
            buf.append(line)
    if key:
        out[key] = "".join(buf)
    return out


def main() -> None:
    parts = sections(SOURCE.read_text())
    used = set()
    for target, (title, ids) in PLAN.items():
        header = (f"# {title}\n\n"
                  f"Moved word for word from PROMPT v1, sections {', '.join(ids)} (2026-10-18). "
                  "Loaded on demand by `PROMPT.md` Section 9. Section numbers inside are v1's.\n\n")
        (ROOT / target).write_text(header + "".join(parts[i] for i in ids).rstrip() + "\n")
        used.update(ids)
    missing = set(parts) - used
    if missing:
        raise SystemExit(f"v1 sections not placed anywhere: {sorted(missing)}")


if __name__ == "__main__":
    main()
