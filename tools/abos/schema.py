"""Minimal JSON Schema validator for the subset our schemas use.

Supported keywords: type, required, properties, additionalProperties (bool or schema),
enum, const, pattern, items, minimum, maximum, maxLength, format (recorded, not enforced).
Anything else in a schema raises UnsupportedKeyword, so a schema can never silently
ask for a check this validator does not perform (fail closed).
"""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

from . import REPO_ROOT

SCHEMA_DIR = REPO_ROOT / "schemas"

_SUPPORTED = {
    "$schema", "$id", "title", "description", "type", "required", "properties",
    "additionalProperties", "enum", "const", "pattern", "items", "minimum", "maximum",
    "maxLength", "format",
}

_TYPES = {
    "object": dict,
    "array": list,
    "string": str,
    "boolean": bool,
    "null": type(None),
}


class UnsupportedKeyword(ValueError):
    pass


def _type_ok(value, name: str) -> bool:
    if name == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if name == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    return isinstance(value, _TYPES[name])


def validate(instance, schema: dict, path: str = "$") -> list[str]:
    """Return a list of error strings; empty means valid."""
    unknown = set(schema) - _SUPPORTED
    if unknown:
        raise UnsupportedKeyword(f"{path}: unsupported schema keyword(s) {sorted(unknown)}")

    errors: list[str] = []

    if "type" in schema:
        types = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(_type_ok(instance, t) for t in types):
            return [f"{path}: expected type {types}, got {type(instance).__name__}"]

    if "const" in schema and instance != schema["const"]:
        errors.append(f"{path}: must equal {schema['const']!r}")
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: {instance!r} not in {schema['enum']}")

    if isinstance(instance, str):
        if "pattern" in schema and not re.search(schema["pattern"], instance):
            errors.append(f"{path}: {instance!r} does not match {schema['pattern']}")
        if "maxLength" in schema and len(instance) > schema["maxLength"]:
            errors.append(f"{path}: longer than {schema['maxLength']} characters")

    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{path}: below minimum {schema['minimum']}")
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append(f"{path}: above maximum {schema['maximum']}")

    if isinstance(instance, dict):
        props = schema.get("properties", {})
        for key in schema.get("required", []):
            if key not in instance:
                errors.append(f"{path}: missing required property '{key}'")
        extra = schema.get("additionalProperties", True)
        for key, value in instance.items():
            if key in props:
                errors.extend(validate(value, props[key], f"{path}.{key}"))
            elif extra is False:
                errors.append(f"{path}: unexpected property '{key}'")
            elif isinstance(extra, dict):
                errors.extend(validate(value, extra, f"{path}.{key}"))

    if isinstance(instance, list) and "items" in schema:
        for i, item in enumerate(instance):
            errors.extend(validate(item, schema["items"], f"{path}[{i}]"))

    return errors


@lru_cache(maxsize=None)
def load_schema(name: str) -> dict:
    """Load schemas/<name>.schema.json."""
    return json.loads((SCHEMA_DIR / f"{name}.schema.json").read_text())


def check(instance, name: str) -> list[str]:
    return validate(instance, load_schema(name))


def check_all_schemas(schema_dir: Path = SCHEMA_DIR) -> dict[str, str]:
    """Walk every schema once to prove it only uses supported keywords."""
    problems = {}
    for path in sorted(schema_dir.glob("*.schema.json")):
        try:
            _walk(json.loads(path.read_text()), path.name)
        except (UnsupportedKeyword, json.JSONDecodeError) as exc:
            problems[path.name] = str(exc)
    return problems


def _walk(schema: dict, where: str) -> None:
    unknown = set(schema) - _SUPPORTED
    if unknown:
        raise UnsupportedKeyword(f"{where}: {sorted(unknown)}")
    for key, sub in schema.get("properties", {}).items():
        _walk(sub, f"{where}.{key}")
    if isinstance(schema.get("additionalProperties"), dict):
        _walk(schema["additionalProperties"], f"{where}.*")
    if isinstance(schema.get("items"), dict):
        _walk(schema["items"], f"{where}[]")
