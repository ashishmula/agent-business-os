"""Secret and instruction-like content scanning (threat model ASI03, ASI01, ASI06, human relay).

Pattern-based, so it catches common key formats, not every secret. A hit blocks; a miss
is not proof of safety. gitleaks or detect-secrets can replace this after review.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

SECRET_PATTERNS = {
    "private_key_block": r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    "aws_access_key": r"\bAKIA[0-9A-Z]{16}\b",
    "github_token": r"\b(gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{50,})\b",
    "anthropic_key": r"\bsk-ant-[A-Za-z0-9_\-]{20,}",
    "openai_key": r"\bsk-(proj-)?[A-Za-z0-9]{32,}",
    "slack_token": r"\bxox[abpors]-[A-Za-z0-9-]{10,}",
    "google_api_key": r"\bAIza[0-9A-Za-z_\-]{35}\b",
    "stripe_key": r"\b[rs]k_live_[0-9A-Za-z]{20,}",
    "generic_assignment": r"(?i)\b(api[_-]?key|secret|password|passwd|token)\b\s*[:=]\s*['\"][^'\"\s]{12,}['\"]",
}

INSTRUCTION_PATTERNS = {
    "ignore_instructions": r"(?i)\b(ignore|disregard|forget)\b.{0,30}\b(previous|prior|above|all|system)\b.{0,20}\b(instructions?|rules?|prompts?)\b",
    "role_override": r"(?i)\byou are now\b|\bnew system prompt\b|\bact as (an? )?(admin|root|developer mode)\b",
    "pipe_to_shell": r"(?i)\b(curl|wget)\b[^\n|]{0,200}\|\s*(ba|z)?sh\b",
    "exfiltrate": r"(?i)\b(send|post|upload|email)\b.{0,40}\b(api key|credentials?|password|\.env|ssh key)\b",
    "approval_bypass": r"(?i)\b(skip|bypass|disable|turn off|ignore)\b.{0,25}\b(approvals?|guard|sandbox|permission rules?|deny rules?)\b"
                       r"|\b(no|not) (approval|permission)s? (is |are )?(needed|required)\b"
                       r"|\bapproval (is |was )?(not needed|not required|already given)\b",
    "private_access": r"(?i)(?<!never )(?<!not )(?<!n't )\b(read|open|cat|copy|send|upload|print)\b.{0,30}\bprivate/",
    "hidden_markup": r"(?i)<!--[^>]*\b(instruction|system|assistant|claude)\b|[\u200b-\u200f\u202a-\u202e\u2066-\u2069]",
}

# Files that agents load as standing context. Instruction-like text here is memory poisoning
# (ASI06): it is flagged for a human to review, never followed.
CONTEXT_FILES = ("memory/", "decisions/", "agents/", "CLAUDE.md", "PROMPT.md")

_COMPILED = {k: re.compile(v) for k, v in {**SECRET_PATTERNS, **INSTRUCTION_PATTERNS}.items()}


def scan_text(text: str, kinds: str = "secrets") -> list[dict]:
    names = SECRET_PATTERNS if kinds == "secrets" else INSTRUCTION_PATTERNS
    hits = []
    for name in names:
        for match in _COMPILED[name].finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            hits.append({"rule": name, "line": line, "preview": _redact(match.group(0))})
    return hits


def _redact(value: str) -> str:
    return value[:6] + "…" if len(value) > 8 else "…"


def staged_files(repo: Path) -> list[Path]:
    out = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        cwd=repo, capture_output=True, text=True, check=True,
    ).stdout
    return [repo / line for line in out.splitlines() if line]


def scan_files(paths: list[Path], kinds: str = "secrets") -> dict[str, list[dict]]:
    found = {}
    for path in paths:
        try:
            text = Path(path).read_text(errors="ignore")
        except (IsADirectoryError, FileNotFoundError):
            continue
        hits = scan_text(text, kinds)
        if hits:
            found[str(path)] = hits
    return found


def is_context_file(path: Path, repo: Path) -> bool:
    try:
        rel = Path(path).resolve().relative_to(Path(repo).resolve()).as_posix()
    except ValueError:
        return False
    return any(rel == c or rel.startswith(c) for c in CONTEXT_FILES)


def context_files(repo: Path) -> list[Path]:
    out = []
    for c in CONTEXT_FILES:
        p = Path(repo) / c
        out += sorted(f for f in p.rglob("*") if f.is_file()) if p.is_dir() else ([p] if p.is_file() else [])
    return out


def scan_context(repo: Path, paths: list[Path] | None = None) -> dict[str, list[dict]]:
    """Instruction scan over standing-context files (all of them, or only those in paths)."""
    files = context_files(repo) if paths is None else [p for p in paths if is_context_file(p, repo)]
    return scan_files(files, "instructions")
