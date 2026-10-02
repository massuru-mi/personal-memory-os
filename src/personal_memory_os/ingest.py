from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Any

from .daily import write_session
from .events import new_event_id, now_for_vault, write_correction, write_memory_event
from .models import CorrectionEvent, MemoryEvent
from .views import rebuild_views


def ingest_turn(vault_root: Path, payload: dict[str, Any]) -> dict[str, list[str] | str]:
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
            id=str(item.get("id") or new_event_id("mem", created_at)),
            type=str(item["type"]),
            content=str(item["content"]),
            created_at=created_at,
            source=str(item.get("source") or source),
            importance=float(item.get("importance", 0.5)),
            status=str(item.get("status", "active")),
            topic=item.get("topic") or topic,
            confidence=float(item.get("confidence", 1.0)),
            explicitness=str(item.get("explicitness", "explicit")),
            supersedes=list(item.get("supersedes", []) or []),
        )
        created.append(str(write_memory_event(vault_root, event)))

    for item in payload.get("corrections", []) or []:
        created_at = _parse_dt(item.get("created_at"), at)
        correction = CorrectionEvent(
            id=str(item.get("id") or new_event_id("correction", created_at)),
            wrong=str(item["wrong"]),
            correct=str(item["correct"]),
            created_at=created_at,
            source=str(item.get("source") or source),
            priority=str(item.get("priority", "critical")),
            topic=item.get("topic") or topic,
            status=str(item.get("status", "active")),
            repeat_error_count=int(item.get("repeat_error_count", 1)),
            supersedes=list(item.get("supersedes", []) or []),
        )
        corrections_created.append(str(write_correction(vault_root, correction)))

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
    return {"events": created, "corrections": corrections_created, "session": str(session_path)}


def _parse_dt(value: Any, fallback: datetime) -> datetime:
    if not value:
        return fallback
    return datetime.fromisoformat(str(value))


def _parse_date(value: Any, fallback: date) -> date:
    if not value:
        return fallback
    return date.fromisoformat(str(value))
