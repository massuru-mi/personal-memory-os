"""Shared validation for API writes and externally authored Markdown records."""

from __future__ import annotations

import math
import re
from datetime import datetime

from .errors import ValidationError

MEMORY_SCHEMA = "pmo.memory-event/v1"
CORRECTION_SCHEMA = "pmo.correction/v1"
ALLOWED_EVENT_TYPES = {
    "fact", "preference", "decision", "project_progress", "open_loop",
    "current_focus", "interest", "relationship", "knowledge",
}
ALLOWED_STATUS = {"active", "superseded", "archived"}
ALLOWED_PRIORITY = {"low", "normal", "high", "critical"}


def require_text(value: object, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{field} must be a non-empty string")


def probability(value: object, field: str) -> float:
    if type(value) not in (int, float) or not math.isfinite(value) or not 0 <= value <= 1:
        raise ValidationError(f"{field} must be a finite number between 0 and 1")
    return float(value)


def aware_datetime(value: object) -> datetime:
    try:
        parsed = value if isinstance(value, datetime) else datetime.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError("created_at must be an ISO datetime with a timezone") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValidationError("created_at must include a timezone offset")
    return parsed


def _choice(value: object, choices: set[str], field: str) -> None:
    if not isinstance(value, str) or value not in choices:
        raise ValidationError(f"unsupported {field}: {value!r}")


def validate_fields(meta: dict, expected_schema: str) -> None:
    if expected_schema not in (MEMORY_SCHEMA, CORRECTION_SCHEMA):
        raise ValidationError(f"unsupported schema: {expected_schema!r}")
    required = {"schema", "id", "type", "created_at", "source", "status"}
    required |= (
        {"importance", "confidence", "explicitness"}
        if expected_schema == MEMORY_SCHEMA else {"priority", "repeat_error_count"}
    )
    missing = sorted(required - meta.keys())
    if missing:
        raise ValidationError("missing required fields: " + ", ".join(missing))
    if meta["schema"] != expected_schema:
        raise ValidationError(f"expected schema {expected_schema}")
    require_text(meta["id"], "id")
    require_text(meta["source"], "source")
    aware_datetime(meta["created_at"])
    _choice(meta["status"], ALLOWED_STATUS, "status")
    if meta.get("topic") is not None and not isinstance(meta["topic"], str):
        raise ValidationError("topic must be a string or null")
    supersedes = meta.get("supersedes", [])
    if not isinstance(supersedes, list):
        raise ValidationError("supersedes must be a list of event IDs")
    for event_id in supersedes:
        require_text(event_id, "supersedes ID")
    if len(set(supersedes)) != len(supersedes) or meta["id"] in supersedes:
        raise ValidationError("supersedes must contain unique IDs other than the record's own ID")
    if expected_schema == MEMORY_SCHEMA:
        _choice(meta["type"], ALLOWED_EVENT_TYPES, "event type")
        _choice(meta["explicitness"], {"explicit", "inferred"}, "explicitness")
        probability(meta["importance"], "importance")
        probability(meta["confidence"], "confidence")
    else:
        _choice(meta["type"], {"correction"}, "event type")
        _choice(meta["priority"], ALLOWED_PRIORITY, "priority")
        count = meta["repeat_error_count"]
        if type(count) is not int or count < 1:
            raise ValidationError("repeat_error_count must be an integer >= 1")


def validate_document(meta: dict, body: str, expected_schema: str) -> None:
    validate_fields(meta, expected_schema)
    require_text(body, "body")
    if expected_schema == CORRECTION_SCHEMA:
        sections = re.split(r"(?m)^## ", body)
        content = {}
        for section in sections[1:]:
            heading, _, text = section.partition("\n")
            content[heading.strip()] = text.strip()
        for heading in ("Wrong assumption", "Correct understanding"):
            require_text(content.get(heading), heading)
        if "Trigger" in content:
            require_text(content["Trigger"], "Trigger")
