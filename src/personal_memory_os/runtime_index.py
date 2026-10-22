from __future__ import annotations

import sqlite3
from pathlib import Path

from .constants import TRANSCRIPTS_DIR
from .paths import VaultPaths

SKIP_PARTS = {"_system", ".obsidian"}
# Bump when the table layout changes so stale indexes are rebuilt instead of queried.
INDEX_FILE = "index.v2.sqlite3"


def _documents(vault_root: Path):
    for path in vault_root.rglob("*.md"):
        rel = path.relative_to(vault_root)
        if any(part in SKIP_PARTS for part in rel.parts):
            continue
        kind = "transcript" if rel.parts[0] == TRANSCRIPTS_DIR else "record"
        yield rel.as_posix(), kind, path.read_text(encoding="utf-8", errors="replace")


def rebuild_index(vault_root: Path) -> Path:
    runtime = VaultPaths(vault_root).runtime_root()
    runtime.mkdir(parents=True, exist_ok=True)
    db = runtime / INDEX_FILE
    conn = sqlite3.connect(db)
    try:
        conn.execute("DROP TABLE IF EXISTS docs")
        conn.execute(
            "CREATE VIRTUAL TABLE docs USING fts5(path UNINDEXED, kind UNINDEXED, content, tokenize='unicode61')"
        )
        conn.executemany("INSERT INTO docs(path, kind, content) VALUES (?, ?, ?)", _documents(vault_root))
        conn.commit()
    finally:
        conn.close()
    return db


def search(
    vault_root: Path, query: str, limit: int = 20, *, include_transcripts: bool = False,
) -> list[dict[str, str]]:
    """Search canonical records; raw transcripts are included only when asked for."""
    db = VaultPaths(vault_root).runtime_root() / INDEX_FILE
    if not db.exists():
        rebuild_index(vault_root)
    where = "docs MATCH ?" if include_transcripts else "docs MATCH ? AND kind = 'record'"
    sql = (
        f"SELECT path, snippet(docs, 2, '[', ']', ' … ', 20) FROM docs WHERE {where} "
        "ORDER BY rank LIMIT ?"
    )
    conn = sqlite3.connect(db)
    try:
        try:
            rows = conn.execute(sql, (query, limit)).fetchall()
        except sqlite3.OperationalError:
            quoted = '"' + query.replace('"', '""') + '"'
            rows = conn.execute(sql, (quoted, limit)).fetchall()
    finally:
        conn.close()
    return [{"path": path, "snippet": snippet} for path, snippet in rows]
