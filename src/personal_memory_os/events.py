from __future__ import annotations

import re
import uuid
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .config import load_settings
from .errors import ValidationError
from .frontmatter import dumps, load_file
from .io import atomic_write_text, file_lock
from .models import CorrectionEvent, MemoryEvent
from .paths import VaultPaths
from .validation import MEMORY_SCHEMA, validate_document

_SAFE = re.compile(r"[^a-zA-Z0-9._-]+")


def safe_slug(value: str, fallback: str = "item") -> str:
    slug = _SAFE.sub("-", value.strip().lower()).strip("-.")
    return slug[:80] or fallback


def now_for_vault(vault_root: Path) -> datetime:
    settings = load_settings(vault_root)
    tz_name = settings.get("language", {}).get("timezone", "UTC")
    try:
        tz = ZoneInfo(tz_name)
    except ZoneInfoNotFoundError:
        tz = ZoneInfo("UTC")
    return datetime.now(tz)


def new_event_id(prefix: str, at: datetime | None = None) -> str:
    at = at or datetime.now().astimezone()
    return f"{prefix}-{at:%Y%m%dT%H%M%S}-{uuid.uuid4().hex[:8]}"


def write_memory_event(vault_root: Path, event: MemoryEvent) -> Path:
    event.validate()
    paths = VaultPaths(vault_root)
    target = paths.events / f"{safe_slug(event.id)}.md"
    front = {
        "schema": "pmo.memory-event/v1",
        "id": event.id,
        "type": event.type,
        "created_at": event.created_at.isoformat(),
        "source": event.source,
        "importance": float(event.importance),
        "confidence": float(event.confidence),
        "explicitness": event.explicitness,
        "status": event.status,
        "topic": event.topic,
        "supersedes": event.supersedes,
    }
    if front.keys() & event.metadata.keys():
        raise ValidationError("metadata must not override canonical fields")
    front.update(event.metadata)
    runtime = paths.runtime_root()
    with file_lock(runtime / "locks" / "events.lock"):
        if target.exists():
            raise FileExistsError(f"Event already exists: {event.id}")
        atomic_write_text(target, dumps(front, event.content))
    return target


def write_correction(vault_root: Path, correction: CorrectionEvent) -> Path:
    correction.validate()
    paths = VaultPaths(vault_root)
    target = paths.corrections / f"{safe_slug(correction.id)}.md"
    front = {
        "schema": "pmo.correction/v1",
        "id": correction.id,
        "type": "correction",
        "created_at": correction.created_at.isoformat(),
        "source": correction.source,
        "priority": correction.priority,
        "status": correction.status,
        "topic": correction.topic,
        "repeat_error_count": correction.repeat_error_count,
        "supersedes": correction.supersedes,
    }
    body = f"## Wrong assumption\n{correction.wrong.strip()}\n\n## Correct understanding\n{correction.correct.strip()}"
    if correction.trigger:
        body += f"\n\n## Trigger\n{correction.trigger.strip()}"
    runtime = paths.runtime_root()
    with file_lock(runtime / "locks" / "corrections.lock"):
        if target.exists():
            raise FileExistsError(f"Correction already exists: {correction.id}")
        atomic_write_text(target, dumps(front, body))
    return target


def read_events(
    directory: Path, expected_schema: str = MEMORY_SCHEMA,
) -> list[tuple[dict, str, Path]]:
    rows: list[tuple[dict, str, Path]] = []
    if not directory.exists():
        return rows
    ids: set[str] = set()
    for path in sorted(directory.glob("*.md")):
        try:
            meta, body = load_file(path)
            validate_document(meta, body, expected_schema)
            if meta["id"] in ids:
                raise ValidationError(f"duplicate event ID: {meta['id']}")
            ids.add(meta["id"])
        except Exception as exc:
            raise ValidationError(f"{path}: {exc}") from exc
        rows.append((meta, body.strip(), path))
    return rows
