from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

from .config import load_settings
from .events import read_events
from .io import atomic_write_text
from .paths import VaultPaths
from .scopes import GLOBAL, category_summary, record_scopes
from .validation import CORRECTION_SCHEMA, aware_datetime, probability

PRIORITY_ORDER = {"critical": 0, "high": 1, "normal": 2, "low": 3}


def _active(rows):
    # Supersession is historical: archiving a replacement must not revive its predecessor.
    superseded = {event_id for meta, _, _ in rows for event_id in meta.get("supersedes", [])}
    return [
        (m, b, p) for m, b, p in rows
        if m["status"] == "active" and m["id"] not in superseded
    ]


def _memory_rows(vault_root: Path):
    settings = load_settings(vault_root)
    threshold = probability(
        settings.get("memory", {}).get("inferred_memory_min_confidence", 0.8),
        "inferred_memory_min_confidence",
    )
    eligible = [
        row for row in read_events(VaultPaths(vault_root).events)
        if row[0]["explicitness"] == "explicit" or row[0]["confidence"] >= threshold
    ]
    return _active(eligible)


def _inference_label(meta):
    if meta["explicitness"] == "inferred":
        return f" [inferred; confidence={meta['confidence']:g}]"
    return ""


def scope_label(meta) -> str:
    scopes = [s for s in record_scopes(meta) if s != GLOBAL]
    return f" {{{', '.join(scopes)}}}" if scopes else ""


def active_corrections(vault_root: Path):
    """Active corrections, strongest first: critical before others, then by repeat count."""
    rows = _active(read_events(VaultPaths(vault_root).corrections, CORRECTION_SCHEMA))
    rows.sort(key=lambda x: (PRIORITY_ORDER.get(str(x[0].get("priority", "normal")), 9), -int(x[0].get("repeat_error_count", 1))))
    return rows


def correction_block(meta, body, path: Path, root: Path, level: int = 3) -> str:
    """Render one correction; body sections are demoted below the given heading level."""
    topic = meta.get("topic") or "General"
    count = int(meta.get("repeat_error_count", 1))
    inner = "#" * (level + 1)
    body = "\n".join(f"{inner} {line[3:]}" if line.startswith("## ") else line for line in body.splitlines())
    return (
        f"{'#' * level} {topic}\n\n{body}\n\n- Priority: `{meta.get('priority', 'critical')}`\n"
        f"- Repeat count: `{count}`\n- Source: {_fmt_link(path, root)}"
    )


def _fmt_link(path: Path, root: Path) -> str:
    rel = path.relative_to(root).with_suffix("").as_posix()
    return f"[[{rel}]]"


def render_memory(vault_root: Path) -> Path:
    rows = _memory_rows(vault_root)
    grouped = defaultdict(list)
    for meta, body, path in rows:
        grouped[str(meta.get("type", "other"))].append((meta, body, path))
    chunks = ["# Memory", "_Generated view. Canonical data lives under `10_Memory/`._"]
    for kind in sorted(grouped):
        chunks.append(f"## {kind.replace('_', ' ').title()}")
        items = sorted(grouped[kind], key=lambda x: float(x[0].get("importance", 0)), reverse=True)
        for meta, body, path in items:
            topic = f" **[{meta.get('topic')}]**" if meta.get("topic") else ""
            chunks.append(
                f"- {body.strip()}{topic}{scope_label(meta)}{_inference_label(meta)} · {_fmt_link(path, vault_root)}"
            )
    target = vault_root / "MEMORY.md"
    atomic_write_text(target, "\n\n".join(chunks).rstrip() + "\n")
    return target


def render_guardrails(vault_root: Path) -> Path:
    rows = active_corrections(vault_root)
    chunks = [
        "# Guardrails",
        (
            "_Generated from active user corrections. Treat these as higher priority than ordinary memory. "
            "Always apply Global; apply a category section when the conversation is in that category "
            "or a sub-category._"
        ),
    ]
    sections: dict[str, list] = defaultdict(list)
    for row in rows:
        for scope in record_scopes(row[0]):
            sections[scope].append(row)
    for scope in [GLOBAL] + sorted(s for s in sections if s != GLOBAL):
        if not sections.get(scope):
            continue
        chunks.append(f"## {'Global' if scope == GLOBAL else scope}")
        for meta, body, path in sections[scope]:
            chunks.append(correction_block(meta, body, path, vault_root))
    target = vault_root / "GUARDRAILS.md"
    atomic_write_text(target, "\n\n".join(chunks).rstrip() + "\n")
    return target


NOW_TYPES = {"project_progress", "open_loop", "current_focus", "decision"}
NOW_LIMIT = 80


def active_memory_rows(vault_root: Path):
    """Active memory events eligible for views (confidence filter and supersession applied)."""
    return _memory_rows(vault_root)


def now_rows(vault_root: Path):
    """Records shown in NOW.md, newest first: (created_at, meta, body, path)."""
    days = now_window_days(vault_root)
    cutoff = datetime.now().astimezone() - timedelta(days=days)
    rows = []
    for meta, body, path in _memory_rows(vault_root):
        if meta.get("type") not in NOW_TYPES:
            continue
        created = aware_datetime(meta["created_at"])
        if created >= cutoff:
            rows.append((created, meta, body, path))
    rows.sort(key=lambda x: x[0], reverse=True)
    return rows[:NOW_LIMIT]


def now_window_days(vault_root: Path) -> int:
    return int(load_settings(vault_root).get("views", {}).get("now_window_days", 30))


def inference_label(meta) -> str:
    return _inference_label(meta)


def render_now(vault_root: Path) -> Path:
    days = now_window_days(vault_root)
    rows = now_rows(vault_root)
    chunks = ["# Now", f"_Generated from active memory in the last {days} days._"]
    for _, meta, body, path in rows:
        chunks.append(f"- **{meta.get('type')}**: {body}{_inference_label(meta)} · {_fmt_link(path, vault_root)}")
    target = vault_root / "NOW.md"
    atomic_write_text(target, "\n".join(chunks).rstrip() + "\n")
    return target


def categories(vault_root: Path) -> list[dict]:
    """Categories used by active memory and corrections (see scopes.category_summary)."""
    rows = [(m, b, p, "memory") for m, b, p in _memory_rows(vault_root)]
    rows += [(m, b, p, "correction") for m, b, p in active_corrections(vault_root)]
    return category_summary(rows, now_window_days(vault_root))


def render_index(vault_root: Path) -> Path:
    paths = VaultPaths(vault_root)
    event_rows = read_events(paths.events)
    corrections = read_events(paths.corrections, CORRECTION_SCHEMA)
    counts = Counter(str(m.get("type", "unknown")) for m, _, _ in event_rows)
    chunks = [
        "# Index",
        "_Generated navigation view._",
        "## Core",
        "- [[GUARDRAILS]]",
        "- [[MEMORY]]",
        "- [[NOW]]",
        "## Memory counts",
    ]
    for key, count in sorted(counts.items()):
        chunks.append(f"- {key}: {count}")
    chunks.append(f"- corrections: {len(corrections)}")
    summary = categories(vault_root)
    if summary:
        chunks.append("## Categories")
        for entry in summary:
            chunks.append(
                f"- {entry['category']}: {entry['memories']} memories, {entry['corrections']} corrections"
                f" ({entry['recent']} recent)"
            )
    target = vault_root / "INDEX.md"
    atomic_write_text(target, "\n".join(chunks).rstrip() + "\n")
    return target


def rebuild_views(vault_root: Path) -> list[Path]:
    # Reject malformed canonical records before replacing any existing view.
    _memory_rows(vault_root)
    read_events(VaultPaths(vault_root).corrections, CORRECTION_SCHEMA)
    return [
        render_guardrails(vault_root),
        render_memory(vault_root),
        render_now(vault_root),
        render_index(vault_root),
    ]
