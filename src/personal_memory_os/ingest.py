from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Any

from .config import load_settings
from .daily import write_session
from .events import new_event_id, now_for_vault, write_correction, write_memory_event
from .models import CorrectionEvent, MemoryEvent
from .validation import aware_datetime
from .views import rebuild_views


def ingest_turn(vault_root: Path, payload: dict[str, Any]) -> dict[str, list[str] | str | None]:
    """Ingest one AI turn using the provider-neutral PMO turn contract."""
    source = str(payload.get("source") or "unknown")
    session_id = str(payload.get("session_id") or new_event_id("session"))
    topic = str(payload.get("topic") or "Conversation")
    at = now_for_vault(vault_root)
    created: list[str] = []
    corrections_created: list[str] = []

    for item in payload.get("memory_events", []) or []:
        created_at = _parse_dt(item.get("created_at"), at)
        event = MemoryEvent(
            id=item.get("id", new_event_id("mem", created_at)),
            type=item["type"],
            content=item["content"],
            created_at=created_at,
            source=item.get("source", source),
            importance=item.get("importance", 0.5),
            status=item.get("status", "active"),
            topic=item.get("topic") or topic,
            confidence=item.get("confidence", 1.0),
            explicitness=item.get("explicitness", "explicit"),
            supersedes=item.get("supersedes", []),
        )
        created.append(str(write_memory_event(vault_root, event)))

    for item in payload.get("corrections", []) or []:
        created_at = _parse_dt(item.get("created_at"), at)
        correction = CorrectionEvent(
            id=item.get("id", new_event_id("correction", created_at)),
            wrong=item["wrong"],
            correct=item["correct"],
            created_at=created_at,
            source=item.get("source", source),
            priority=item.get("priority", "critical"),
            topic=item.get("topic") or topic,
            status=item.get("status", "active"),
            repeat_error_count=item.get("repeat_error_count", 1),
            supersedes=item.get("supersedes", []),
        )
        corrections_created.append(str(write_correction(vault_root, correction)))

    session_path = None
    if _daily_enabled(vault_root):
        session = payload.get("session") or {}
        session_path = write_session(
            vault_root,
            source=source,
            session_id=session_id,
            topic=topic,
            day=_parse_date(payload.get("date"), at.date()),
            done=list(session.get("done", []) or []),
            learned=list(session.get("learned", []) or []),
            decisions=list(session.get("decisions", []) or []),
            corrections=list(session.get("corrections", []) or []),
            open_loops=list(session.get("open_loops", []) or []),
            updated_at=at,
        )
    rebuild_views(vault_root)
    return {
        "events": created,
        "corrections": corrections_created,
        "session": str(session_path) if session_path else None,
    }


def _daily_enabled(vault_root: Path) -> bool:
    daily = load_settings(vault_root).get("daily") or {}
    return isinstance(daily, dict) and daily.get("enabled") is True


def _parse_dt(value: Any, fallback: datetime) -> datetime:
    if value is None:
        return fallback
    return aware_datetime(value)


def _parse_date(value: Any, fallback: date) -> date:
    if not value:
        return fallback
    return date.fromisoformat(str(value))
