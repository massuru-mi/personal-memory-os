from __future__ import annotations

import sqlite3
from pathlib import Path

from .constants import TRANSCRIPTS_DIR
from .paths import VaultPaths

SKIP_PARTS = {"_system", ".obsidian"}
# Bump when the table layout changes so stale indexes are rebuilt instead of queried.
INDEX_FILE = "index.v3.sqlite3"
# The trigram tokenizer matches any substring of three characters or more, so words in text without
# spaces (Japanese, Chinese) are found too. Shorter words fall back to a substring scan.
TRIGRAM = 3
SNIPPET_CHARS = 40


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
            "CREATE VIRTUAL TABLE docs USING fts5(path UNINDEXED, kind UNINDEXED, content, tokenize='trigram')"
        )
        conn.executemany("INSERT INTO docs(path, kind, content) VALUES (?, ?, ?)", _documents(vault_root))
        conn.commit()
    finally:
        conn.close()
    return db


def _snippet(content: str, terms: list[str]) -> str:
    lower = content.lower()
    hits = [(lower.find(t.lower()), t) for t in terms]
    hits = [(i, t) for i, t in hits if i >= 0]
    if not hits:
        return ""
    start, term = min(hits)
    left, right = max(0, start - SNIPPET_CHARS), start + len(term) + SNIPPET_CHARS
    text = f"{content[left:start]}[{content[start:start + len(term)]}]{content[start + len(term):right]}"
    text = " ".join(text.split())
    return ("… " if left else "") + text + (" …" if right < len(content) else "")


def search(
    vault_root: Path, query: str, limit: int = 20, *, include_transcripts: bool = False,
) -> list[dict[str, str]]:
    """Search canonical records; raw transcripts are included only when asked for.

    Space-separated words must all appear. Words of any length and in any language match as substrings.
    """
    db = VaultPaths(vault_root).runtime_root() / INDEX_FILE
    if not db.exists():
        rebuild_index(vault_root)
    terms = query.split()
    if not terms:
        return []
    kind = "" if include_transcripts else " AND kind = 'record'"
    conn = sqlite3.connect(db)
    try:
        if all(len(t) >= TRIGRAM for t in terms):
            sql = (
                f"SELECT path, snippet(docs, 2, '[', ']', ' … ', {SNIPPET_CHARS // 2}) FROM docs "
                f"WHERE docs MATCH ?{kind} ORDER BY rank LIMIT ?"
            )
            try:
                rows = conn.execute(sql, (query, limit)).fetchall()
            except sqlite3.OperationalError:
                quoted = " ".join('"' + t.replace('"', '""') + '"' for t in terms)
                rows = conn.execute(sql, (quoted, limit)).fetchall()
        else:
            # A word shorter than a trigram cannot use the index: scan for every word as a substring.
            like = " AND ".join("content LIKE ? ESCAPE '\\'" for _ in terms)
            args = ["%" + t.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%" for t in terms]
            found = conn.execute(
                f"SELECT path, content FROM docs WHERE {like}{kind} ORDER BY path DESC LIMIT ?", (*args, limit),
            ).fetchall()
            rows = [(path, _snippet(content, terms)) for path, content in found]
    finally:
        conn.close()
    return [{"path": path, "snippet": snippet} for path, snippet in rows]
