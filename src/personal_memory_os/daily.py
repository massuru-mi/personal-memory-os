from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Iterable

from .events import safe_slug
from .frontmatter import dumps, load_file
from .io import atomic_write_text, file_lock
from .paths import VaultPaths

SECTION_ORDER = ("done", "learned", "decisions", "corrections", "open_loops")
SECTION_TITLES = {
    "done": "What we did",
    "learned": "What we learned",
    "decisions": "Decisions",
    "corrections": "Corrections",
    "open_loops": "Open loops",
}


def _clean(values: Iterable[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        item = value.strip() if value else ""
        if not item or item == "None" or item in seen:
            continue
        seen.add(item)
        result.append(item)
    return result


def _bullets(values: Iterable[str]) -> str:
    clean = _clean(values)
    return "\n".join(f"- {v}" for v in clean) if clean else "- None"


def _existing_sections(path: Path) -> dict[str, list[str]]:
    result = {key: [] for key in SECTION_ORDER}
    if not path.exists():
        return result
    try:
        _, body = load_file(path)
    except Exception:
        return result
    current: str | None = None
    title_to_key = {title: key for key, title in SECTION_TITLES.items()}
    for line in body.splitlines():
        if line.startswith("## "):
            current = title_to_key.get(line[3:].strip())
        elif current and line.startswith("- "):
            value = line[2:].strip()
            if value and value != "None":
                result[current].append(value)
    return result


def write_session(
    vault_root: Path,
    *,
    source: str,
    session_id: str,
    topic: str,
    day: date,
    done: list[str] | None = None,
    learned: list[str] | None = None,
    decisions: list[str] | None = None,
    corrections: list[str] | None = None,
    open_loops: list[str] | None = None,
    updated_at: datetime | None = None,
) -> Path:
    paths = VaultPaths(vault_root)
    folder = paths.daily / day.isoformat()
    target = folder / f"{safe_slug(source)}_{safe_slug(session_id)}_{safe_slug(topic, 'session')}.md"
    previous = _existing_sections(target)
    sections = {
        "done": _clean(previous["done"] + (done or [])),
        "learned": _clean(previous["learned"] + (learned or [])),
        "decisions": _clean(previous["decisions"] + (decisions or [])),
        "corrections": _clean(previous["corrections"] + (corrections or [])),
        "open_loops": _clean(previous["open_loops"] + (open_loops or [])),
    }
    body_parts = [f"# {topic.strip() or 'Session'}"]
    for key in SECTION_ORDER:
        body_parts.append(f"## {SECTION_TITLES[key]}\n{_bullets(sections[key])}")
    front = {
        "schema": "pmo.daily-session/v1",
        "source": source,
        "session_id": session_id,
        "topic": topic,
        "date": day.isoformat(),
        "updated_at": (updated_at or datetime.now().astimezone()).isoformat(),
    }
    with file_lock(paths.runtime_root() / "locks" / "daily.lock"):
        atomic_write_text(target, dumps(front, "\n\n".join(body_parts)))
    return target


def render_day_summary(vault_root: Path, day: date) -> Path | None:
    paths = VaultPaths(vault_root)
    folder = paths.daily / day.isoformat()
    sessions = [p for p in sorted(folder.glob("*.md")) if p.name != "SUMMARY.md"] if folder.exists() else []
    if not sessions:
        return None
    chunks = [f"# {day.isoformat()} Summary", "_Generated from PMO session logs._"]
    for path in sessions:
        try:
            meta, body = load_file(path)
        except Exception:
            continue
        source = meta.get("source", "unknown")
        topic = meta.get("topic", path.stem)
        chunks.append(f"## {topic} ({source})\n\n{body}")
    target = folder / "SUMMARY.md"
    atomic_write_text(target, "\n\n".join(chunks).rstrip() + "\n")
    return target
