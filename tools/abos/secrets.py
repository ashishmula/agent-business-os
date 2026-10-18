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
    "generic_assignment": r"(?i)\b(api[_-]?key|secret|password|passwd|token)\b\s*[:=]\s*"
                          r"(['\"][^'\"\s]{12,}['\"]|(?=[A-Za-z_\-]*\d)[A-Za-z0-9_\-]{16,}\b)",  # unquoted needs a digit (P3-MUSE-04)
}

# Widened after P3-MUSE-04, which listed wordings that slipped past each rule. Still a tripwire,
# not a wall: a reworded line can pass, so findings are flagged for a human, never trusted as clean.
INSTRUCTION_PATTERNS = {
    "ignore_instructions": r"(?i)(?<!never )(?<!not )(?<!n't )\b(ignore|disregard|forget|set aside|override|discard|abandon|drop)\b.{0,40}"
                           r"\b(previous|prior|above|earlier|all|system|standing)\b.{0,20}"
                           r"\b(instructions?|rules?|prompts?|guidance|directions?|constraints?|polic(y|ies))\b",
    "role_override": r"(?i)\byou are now\b|\bnew system prompt\b|\bact as (an? )?(admin|root|developer mode)\b",
    "pipe_to_shell": r"(?i)\b(curl|wget)\b[^\n|]{0,200}\|\s*(sudo\s+)?((ba|z)?sh|python[0-9.]*|perl|ruby|node)\b"
                     r"|\b(ba|z)?sh\s+<\(\s*(curl|wget)\b",
    "exfiltrate": r"(?i)\b(send|post|upload|email|forward|share|transmit|paste|leak)\b.{0,40}"
                  r"\b(api keys?|credentials?|passwords?|\.env|ssh keys?|secrets?|tokens?)\b",
    "approval_bypass": r"(?i)\b(skip|bypass|disable|turn off|ignore)\b.{0,25}\b(approvals?|guard|sandbox|permission rules?|deny rules?)\b"
                       r"|\b(no|not) (approval|permission)s? (is |are )?(needed|required)\b"
                       r"|\bapproval (is |was )?(not needed|not required|already given)\b"
                       r"|\bpre-?authori[sz]ed\b|\balready (been )?approved\b|\b(i|ashish) (have|has|had)\b.{0,15}\bapproved\b",
    "approval_lure": r"(?i)\b(approve|allow|accept|grant)\b.{0,40}\b(network|domain|host|upload|egress|outbound|pypi\.org|npmjs|access to)\b"
                     r".{0,40}\b(to|so|for)\b.{0,20}\b(verify|fix|check|finish|continue|install|update)\b",
    "private_access": r"(?i)(?<!never )(?<!not )(?<!n't )\b(read|open|cat|copy|send|upload|print|display|show|summari[sz]e|include|"
                      r"list|dump|forward|share|paste|quote)\b.{0,80}\bprivate/",
    "hidden_markup": r"(?i)<!--(?!\s*-->)|[\u200b-\u200f\u202a-\u202e\u2066-\u2069]",  # any HTML comment in a context file
}

# Files that agents load as standing context. Instruction-like text here is memory poisoning
# (ASI06): it is flagged for a human to review, never followed.
CONTEXT_FILES = ("memory/", "decisions/", "agents/", "evidence/", "CLAUDE.md", "PROMPT.md")  # evidence/ added after P3-MUSE-04

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
