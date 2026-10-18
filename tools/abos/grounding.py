"""T0 grounding check for model extractions (Muse-approved fix for invented values).

Every non-null value a model extracts must be traceable to the source text; anything that
is not is replaced with null and reported. Deterministic, no LLM.
"""

from __future__ import annotations

import re

CURRENCY_SYMBOLS = {"€": "EUR", "£": "GBP", "¥": "JPY", "CA$": "CAD", "C$": "CAD", "US$": "USD", "A$": "AUD"}   # "$" is ambiguous (CAD/USD/AUD...), never enough alone
WORD = re.compile(r"[a-z]+|[0-9]+")


def _numbers(text: str) -> set[float]:
    found = set()
    for m in re.finditer(r"\d+(?:[.,]\d+)?", text):
        try:
            found.add(round(float(m.group(0).replace(",", ".")), 2))
        except ValueError:
            pass
    return found


def grounded(value, source: str, field: str = "") -> bool:
    if value is None:
        return True
    low = source.lower()
    if isinstance(value, bool):
        return False
    if isinstance(value, (int, float)):
        return round(float(value), 2) in _numbers(source)
    text = str(value).strip()
    if not text:
        return True
    if field == "currency" or re.fullmatch(r"[A-Z]{3}", text):
        code = text.upper()
        return code.lower() in WORD.findall(low) or any(sym in source and c == code for sym, c in CURRENCY_SYMBOLS.items())
    try:
        return round(float(text.replace(",", ".")), 2) in _numbers(source)
    except ValueError:
        pass
    words = WORD.findall(text.lower())
    source_words = set(WORD.findall(low))
    return bool(words) and all(w in source_words for w in words)


def check(extracted: dict, source: str) -> tuple[dict, list[str]]:
    """Return (cleaned copy with ungrounded values set to None, list of ungrounded field names)."""
    cleaned, dropped = {}, []
    for field, value in extracted.items():
        if grounded(value, source, field):
            cleaned[field] = value
        else:
            cleaned[field] = None
            dropped.append(field)
    return cleaned, dropped
