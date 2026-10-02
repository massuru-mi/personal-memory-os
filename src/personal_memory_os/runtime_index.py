from __future__ import annotations

import sqlite3
from pathlib import Path

from .paths import VaultPaths

SKIP_PARTS = {"_system", ".obsidian"}


def _documents(vault_root: Path):
    for path in vault_root.rglob("*.md"):
        rel = path.relative_to(vault_root)
        if any(part in SKIP_PARTS for part in rel.parts):
            continue
        yield rel.as_posix(), path.read_text(encoding="utf-8", errors="replace")


def rebuild_index(vault_root: Path) -> Path:
    runtime = VaultPaths(vault_root).runtime_root()
    runtime.mkdir(parents=True, exist_ok=True)
    db = runtime / "index.sqlite3"
    conn = sqlite3.connect(db)
    try:
        conn.execute("DROP TABLE IF EXISTS docs")
        conn.execute("CREATE VIRTUAL TABLE docs USING fts5(path UNINDEXED, content, tokenize='unicode61')")
        conn.executemany("INSERT INTO docs(path, content) VALUES (?, ?)", _documents(vault_root))
        conn.commit()
    finally:
        conn.close()
    return db


def search(vault_root: Path, query: str, limit: int = 20) -> list[dict[str, str]]:
    db = VaultPaths(vault_root).runtime_root() / "index.sqlite3"
    if not db.exists():
        rebuild_index(vault_root)
    conn = sqlite3.connect(db)
    try:
        try:
            rows = conn.execute(
                "SELECT path, snippet(docs, 1, '[', ']', ' … ', 20) FROM docs WHERE docs MATCH ? ORDER BY rank LIMIT ?",
                (query, limit),
            ).fetchall()
        except sqlite3.OperationalError:
            quoted = '"' + query.replace('"', '""') + '"'
            rows = conn.execute(
                "SELECT path, snippet(docs, 1, '[', ']', ' … ', 20) FROM docs WHERE docs MATCH ? ORDER BY rank LIMIT ?",
                (quoted, limit),
            ).fetchall()
    finally:
        conn.close()
    return [{"path": path, "snippet": snippet} for path, snippet in rows]
