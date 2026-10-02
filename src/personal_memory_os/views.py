from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

from .config import load_settings
from .constants import DECISIONS_DIR, KNOWLEDGE_DIR, PROJECTS_DIR
from .events import read_events
from .io import atomic_write_text
from .paths import VaultPaths

PRIORITY_ORDER = {"critical": 0, "high": 1, "normal": 2, "low": 3}


def _active(rows):
    return [(m, b, p) for m, b, p in rows if m.get("status", "active") == "active"]


def _fmt_link(path: Path, root: Path) -> str:
    rel = path.relative_to(root).with_suffix("").as_posix()
    return f"[[{rel}]]"


def render_memory(vault_root: Path) -> Path:
    paths = VaultPaths(vault_root)
    rows = _active(read_events(paths.events))
    grouped = defaultdict(list)
    for meta, body, path in rows:
        if meta.get("explicitness") == "inferred" and float(meta.get("confidence", 0)) < 0.8:
            continue
        grouped[str(meta.get("type", "other"))].append((meta, body, path))
    chunks = ["# Memory", "_Generated view. Canonical data lives under `10_Memory/`._"]
    for kind in sorted(grouped):
        chunks.append(f"## {kind.replace('_', ' ').title()}")
        items = sorted(grouped[kind], key=lambda x: float(x[0].get("importance", 0)), reverse=True)
        for meta, body, path in items:
            topic = f" **[{meta.get('topic')}]**" if meta.get("topic") else ""
            chunks.append(f"- {body.strip()}{topic} · {_fmt_link(path, vault_root)}")
    target = vault_root / "MEMORY.md"
    atomic_write_text(target, "\n\n".join(chunks).rstrip() + "\n")
    return target


def render_guardrails(vault_root: Path) -> Path:
    paths = VaultPaths(vault_root)
    rows = _active(read_events(paths.corrections))
    rows.sort(key=lambda x: (PRIORITY_ORDER.get(str(x[0].get("priority", "normal")), 9), -int(x[0].get("repeat_error_count", 1))))
    chunks = ["# Guardrails", "_Generated from active user corrections. Treat these as higher priority than ordinary memory._"]
    for meta, body, path in rows:
        topic = meta.get("topic") or "General"
        count = int(meta.get("repeat_error_count", 1))
        chunks.append(f"## {topic}\n\n{body}\n\n- Priority: `{meta.get('priority', 'critical')}`\n- Repeat count: `{count}`\n- Source: {_fmt_link(path, vault_root)}")
    target = vault_root / "GUARDRAILS.md"
    atomic_write_text(target, "\n\n".join(chunks).rstrip() + "\n")
    return target


def render_now(vault_root: Path) -> Path:
    paths = VaultPaths(vault_root)
    settings = load_settings(vault_root)
    days = int(settings.get("views", {}).get("now_window_days", 30))
    cutoff = datetime.now().astimezone() - timedelta(days=days)
    allowed = {"project_progress", "open_loop", "current_focus", "decision"}
    rows = []
    for meta, body, path in _active(read_events(paths.events)):
        if meta.get("type") not in allowed:
            continue
        try:
            created = datetime.fromisoformat(str(meta.get("created_at")))
        except Exception:
            created = datetime.min.astimezone()
        if created >= cutoff:
            rows.append((created, meta, body, path))
    rows.sort(key=lambda x: x[0], reverse=True)
    chunks = ["# Now", f"_Generated from active memory in the last {days} days._"]
    for _, meta, body, path in rows[:80]:
        chunks.append(f"- **{meta.get('type')}**: {body} · {_fmt_link(path, vault_root)}")
    target = vault_root / "NOW.md"
    atomic_write_text(target, "\n".join(chunks).rstrip() + "\n")
    return target


def render_index(vault_root: Path) -> Path:
    paths = VaultPaths(vault_root)
    event_rows = read_events(paths.events)
    corrections = read_events(paths.corrections)
    counts = Counter(str(m.get("type", "unknown")) for m, _, _ in event_rows)
    chunks = [
        "# Index",
        "_Generated navigation view._",
        "## Core",
        "- [[GUARDRAILS]]",
        "- [[MEMORY]]",
        "- [[NOW]]",
        f"- [[{PROJECTS_DIR}]]",
        f"- [[{KNOWLEDGE_DIR}]]",
        f"- [[{DECISIONS_DIR}]]",
        "## Memory counts",
    ]
    for key, count in sorted(counts.items()):
        chunks.append(f"- {key}: {count}")
    chunks.append(f"- corrections: {len(corrections)}")
    target = vault_root / "INDEX.md"
    atomic_write_text(target, "\n".join(chunks).rstrip() + "\n")
    return target


def rebuild_views(vault_root: Path) -> list[Path]:
    return [
        render_guardrails(vault_root),
        render_memory(vault_root),
        render_now(vault_root),
        render_index(vault_root),
    ]
