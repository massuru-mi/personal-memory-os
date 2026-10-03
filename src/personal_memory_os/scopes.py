"""Scopes: where a memory event or correction applies.

A scope is either ``global`` (applies to every conversation) or a category path such as
``digital/video-editing``. Categories are not predefined: the set of categories is whatever
the user's records use, so new ones appear simply by recording with a new path. A record in a
parent category also applies to its child categories. Records without a scope are global.
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta

from .errors import ValidationError

GLOBAL = "global"


def validate_scope(value: object) -> None:
    if not isinstance(value, list) or not value:
        raise ValidationError("scope must be a non-empty list of strings")
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, str) or not item.strip() or item != item.strip():
            raise ValidationError(f"invalid scope: {item!r}")
        if item != GLOBAL:
            parts = item.split("/")
            if any(not p.strip() or p != p.strip() or p in {".", ".."} for p in parts):
                raise ValidationError(f"invalid scope path: {item!r}")
            if GLOBAL in parts:
                raise ValidationError(f"'{GLOBAL}' cannot be part of a category path: {item!r}")
        if item in seen:
            raise ValidationError(f"duplicate scope: {item!r}")
        seen.add(item)
    if GLOBAL in seen and len(seen) > 1:
        raise ValidationError("a global record cannot also have categories")


def record_scopes(meta: dict) -> list[str]:
    return list(meta.get("scope") or [GLOBAL])


def is_global(meta: dict) -> bool:
    return GLOBAL in record_scopes(meta)


def ancestors(category: str) -> list[str]:
    """``a/b/c`` -> ``["a", "a/b", "a/b/c"]``."""
    parts = category.split("/")
    return ["/".join(parts[: i + 1]) for i in range(len(parts))]


def applies_to(meta: dict, categories: list[str]) -> bool:
    """True when the record is in one of the requested categories or in one of their parents."""
    wanted = {a for c in categories for a in ancestors(c.strip()) if c.strip()}
    return any(scope in wanted for scope in record_scopes(meta) if scope != GLOBAL)


def category_summary(rows, recent_days: int = 30) -> list[dict]:
    """Categories in use with record counts, recent counts and frequent topics, most used first.

    ``rows`` are ``(meta, body, path, kind)`` with kind ``"memory"`` or ``"correction"``.
    Counts roll up to parent categories so a growing sub-area is visible from its parent too.
    """
    cutoff = datetime.now().astimezone() - timedelta(days=recent_days)
    stats: dict[str, dict] = {}
    for meta, _, _, kind in rows:
        for scope in record_scopes(meta):
            if scope == GLOBAL:
                continue
            for name in ancestors(scope):
                entry = stats.setdefault(name, {
                    "category": name, "memories": 0, "corrections": 0, "recent": 0, "_topics": Counter(),
                })
                entry["memories" if kind == "memory" else "corrections"] += 1
                created = meta.get("created_at")
                created = created if isinstance(created, datetime) else datetime.fromisoformat(str(created))
                if created >= cutoff:
                    entry["recent"] += 1
                if meta.get("topic"):
                    entry["_topics"][str(meta["topic"])] += 1
    result = []
    for entry in stats.values():
        topics = entry.pop("_topics")
        entry["topics"] = [t for t, _ in topics.most_common(5)]
        result.append(entry)
    result.sort(key=lambda e: (-(e["memories"] + e["corrections"]), e["category"]))
    return result
