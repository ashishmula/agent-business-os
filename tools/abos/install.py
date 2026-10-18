"""Install the reviewed Claude Code setup into .claude/ (settings + subagents).

Claude Code only reads .claude/, but remote agents may not write there, so the reviewed
copies live in config/ and agents/claude/ and Ashish runs `./abos install-claude` on his Mac.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from . import REPO_ROOT


def install(repo: Path = REPO_ROOT) -> list[str]:
    target = repo / ".claude"
    (target / "agents").mkdir(parents=True, exist_ok=True)
    changes = []
    pairs = [(repo / "config" / "claude-code-settings.json", target / "settings.json")]
    pairs += [(src, target / "agents" / src.name) for src in sorted((repo / "agents" / "claude").glob("*.md"))]
    for src, dst in pairs:
        if dst.exists() and dst.read_bytes() == src.read_bytes():
            continue
        changes.append(f"{'updated' if dst.exists() else 'added'} {dst.relative_to(repo)}")
        shutil.copyfile(src, dst)
    wanted = {src.name for src in (repo / "agents" / "claude").glob("*.md")}
    for old in (target / "agents").glob("*.md"):
        if old.name not in wanted:
            changes.append(f"left in place (not ours, check it): {old.relative_to(repo)}")
    return changes
