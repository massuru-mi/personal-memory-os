"""MCP wrapper around PMO's deterministic operations.

The tools only call existing PMO functions; Markdown stays canonical. The server
starts even when the vault is unavailable (for example while Google Drive is not
mounted) so that a user-scope registration never breaks unrelated sessions.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Literal

from .config import load_settings
from .constants import VERSION_FILE
from .deploy import read_version
from .doctor import doctor_dict
from .events import (
    new_event_id,
    now_for_vault,
    read_events,
    set_scope,
    write_correction,
    write_memory_event,
)
from .models import CorrectionEvent, MemoryEvent
from .paths import VaultPaths
from .runtime_index import rebuild_index, search
from .scopes import applies_to, is_global
from .validation import CORRECTION_SCHEMA, aware_datetime
from .views import (
    active_corrections,
    active_memory_rows,
    categories,
    correction_block,
    inference_label,
    now_rows,
    rebuild_views,
    scope_label,
)

VAULT_ENV = "PMO_VAULT"

INSTRUCTIONS = """\
PMO (Personal Memory OS) is connected: the user's own memory, shared across AI assistants.
At the start of the session, before relying on personal context, call pmo_bootstrap once and follow what it returns.
- pmo_bootstrap returns global guardrails and memory plus the list of the user's categories. When the conversation
  is about one or more of those categories (or a parent of them), call pmo_category_context with all that apply.
- User corrections (guardrails) outrank everything else, including ordinary memory.
- Save only what the user asks to save, or what the returned memory policy allows; otherwise propose the save.
- Write memories and corrections only with pmo_record_memory / pmo_record_correction. Never edit PMO files by hand.
  Give each a scope: "global" only for how to behave in every conversation, otherwise the best matching category
  (reuse existing ones; create a new path like "digital/video-editing" when none fits; use the broader parent if unsure).
- To change or retire a recorded item, record a new one that supersedes it.
If pmo_bootstrap reports PMO as unavailable, tell the user once and continue without PMO.
"""

MemoryType = Literal[
    "fact", "preference", "decision", "project_progress", "open_loop",
    "current_focus", "interest", "relationship", "knowledge",
]
Priority = Literal["low", "normal", "high", "critical"]
DEFAULT_MAX_CONTEXT_CHARS = 8000
MIN_MAX_CONTEXT_CHARS = 1000
ITEM_MAX_CHARS = 400
# NOW only needs the gist ("in the other project you said …"); details come from the record or category.
NOW_ITEM_MAX_CHARS = 150
NOW_BUDGET_SHARE = 0.4


class PMOTools:
    """Tool implementations, kept independent of the MCP SDK for testing."""

    def __init__(self, vault: Path | None, max_context_chars: int = DEFAULT_MAX_CONTEXT_CHARS):
        self.vault = vault.expanduser().resolve() if vault else None
        self.max_context_chars = max_context_chars
        self._index_fresh = False

    # -- availability -----------------------------------------------------

    def _unavailable(self) -> dict[str, Any] | None:
        if self.vault is None:
            return {"available": False, "reason": f"No vault configured. Pass --vault or set {VAULT_ENV}."}
        if not (self.vault / VERSION_FILE).is_file():
            return {"available": False, "reason": f"PMO vault not found or not mounted: {self.vault}"}
        return None

    def _require_vault(self) -> Path:
        problem = self._unavailable()
        if problem:
            raise RuntimeError(problem["reason"])
        assert self.vault is not None
        return self.vault

    # -- read ---------------------------------------------------------------

    def bootstrap(self, max_chars: int | None = None) -> dict[str, Any]:
        problem = self._unavailable()
        if problem:
            return problem
        vault = self._require_vault()
        warnings: list[str] = []
        if self._views_stale(vault):
            try:
                rebuild_views(vault)
            except Exception as exc:  # noqa: BLE001 - report instead of failing the session
                warnings.append(
                    f"Views could not be refreshed ({exc}). Follow _system/skills/pmo-doctor-repair/SKILL.md."
                )
        settings = load_settings(vault)
        rules_path = vault / "_config" / "custom_rules.md"
        result: dict[str, Any] = {
            "available": True,
            "vault": str(vault),
            "system_version": read_version(vault).get("system_version"),
            "policy": {
                "memory": settings.get("memory", {}),
                "daily": settings.get("daily", {}),
                "language": settings.get("language", {}),
            },
            "custom_rules": rules_path.read_text(encoding="utf-8") if rules_path.is_file() else "",
            "rules": "Full rules: START_HERE.md and _system/protocols/ in the vault (read with pmo_read_file).",
            "warnings": warnings,
        }
        try:
            result["guardrails"] = self._guardrails(vault, [r for r in active_corrections(vault) if is_global(r[0])])
            result["categories"] = categories(vault)
            result.update(self._budgeted_memory(
                vault, max_chars or self.max_context_chars, len(result["guardrails"]), memory_filter=is_global,
            ))
        except Exception as exc:  # noqa: BLE001 - unreadable records must not hide guardrails
            warnings.append(f"Records could not be loaded ({exc}). Follow _system/skills/pmo-doctor-repair/SKILL.md.")
            fallback = vault / "GUARDRAILS.md"
            result["guardrails"] = fallback.read_text(encoding="utf-8") if fallback.is_file() else ""
            result.update({"categories": [], "now": "", "memory": "", "omitted": {"now": 0, "memory": 0}})
        return result

    def category_context(self, categories_: list[str], max_chars: int | None = None) -> dict[str, Any]:
        vault = self._require_vault()
        wanted = [c.strip() for c in categories_ if isinstance(c, str) and c.strip()]
        if not wanted:
            raise ValueError("Pass at least one category from pmo_bootstrap's categories.")
        guardrails = self._guardrails(vault, [r for r in active_corrections(vault) if applies_to(r[0], wanted)])
        memory = [r for r in active_memory_rows(vault) if applies_to(r[0], wanted)]
        memory.sort(key=self._importance_key, reverse=True)
        budget = max(max_chars or self.max_context_chars, MIN_MAX_CONTEXT_CHARS) - len(guardrails)
        lines, _ = self._take(vault, memory, budget)
        known = {entry["category"] for entry in categories(vault)}
        result: dict[str, Any] = {
            "categories": wanted,
            "guardrails": guardrails,
            "memory": "\n".join(lines),
            "omitted": len(memory) - len(lines),
            "unknown_categories": [c for c in wanted if c not in known],
        }
        if result["omitted"]:
            result["more"] = "Some lower-priority items were omitted. Use pmo_search to find them."
        return result

    def search(self, query: str, limit: int = 10) -> dict[str, Any]:
        vault = self._require_vault()
        if not self._index_fresh:
            rebuild_index(vault)
            self._index_fresh = True
        return {"results": search(vault, query, limit=limit)}

    def read_file(self, path: str) -> dict[str, Any]:
        vault = self._require_vault()
        target = (vault / path).resolve()
        if not target.is_relative_to(vault) or target.suffix not in {".md", ".yaml"}:
            raise ValueError("Only .md and .yaml files inside the PMO vault can be read.")
        if not target.is_file():
            raise FileNotFoundError(path)
        return {"path": target.relative_to(vault).as_posix(), "content": target.read_text(encoding="utf-8")}

    def doctor(self) -> dict[str, Any]:
        checks = doctor_dict(self._require_vault())
        return {"ok": all(c["ok"] for c in checks), "checks": checks}

    # -- write --------------------------------------------------------------

    def record_memory(
        self,
        type: str,
        content: str,
        topic: str | None = None,
        importance: float = 0.7,
        explicitness: str = "explicit",
        confidence: float = 1.0,
        supersedes: list[str] | None = None,
        status: str = "active",
        source: str = "mcp",
        scope: list[str] | None = None,
    ) -> dict[str, Any]:
        vault = self._require_vault()
        supersedes = supersedes or []
        self._check_known_ids(VaultPaths(vault).events, supersedes)
        at = now_for_vault(vault)
        event = MemoryEvent(
            id=new_event_id("mem", at), type=type, content=content, created_at=at, source=source,
            importance=importance, status=status, topic=topic, confidence=confidence,
            explicitness=explicitness, supersedes=supersedes, scope=scope or [],
        )
        path = write_memory_event(vault, event)
        return self._after_write(vault, event.id, path)

    def record_correction(
        self,
        wrong: str,
        correct: str,
        trigger: str | None = None,
        topic: str | None = None,
        priority: str = "critical",
        repeat_error_count: int = 1,
        supersedes: list[str] | None = None,
        source: str = "mcp",
        scope: list[str] | None = None,
    ) -> dict[str, Any]:
        vault = self._require_vault()
        supersedes = supersedes or []
        self._check_known_ids(VaultPaths(vault).corrections, supersedes, CORRECTION_SCHEMA)
        at = now_for_vault(vault)
        correction = CorrectionEvent(
            id=new_event_id("correction", at), wrong=wrong, correct=correct, created_at=at, source=source,
            priority=priority, topic=topic, repeat_error_count=repeat_error_count,
            supersedes=supersedes, trigger=trigger, scope=scope or [],
        )
        path = write_correction(vault, correction)
        return self._after_write(vault, correction.id, path)

    def set_scope(self, ids: list[str], scope: list[str]) -> dict[str, Any]:
        vault = self._require_vault()
        changed = set_scope(vault, ids, scope)
        rebuild_views(vault)
        self._index_fresh = False
        return {"updated": [p.relative_to(vault).as_posix() for p in changed], "scope": scope}

    def rebuild(self) -> dict[str, Any]:
        vault = self._require_vault()
        views = [p.name for p in rebuild_views(vault)]
        rebuild_index(vault)
        self._index_fresh = True
        return {"views": views, "index": "rebuilt"}

    # -- helpers ------------------------------------------------------------

    @staticmethod
    def _guardrails(vault: Path, rows) -> str:
        return "\n\n".join(correction_block(meta, body, path, vault, level=2) for meta, body, path in rows)

    @staticmethod
    def _importance_key(row):
        return float(row[0].get("importance", 0)), aware_datetime(row[0]["created_at"])

    def _budgeted_memory(self, vault: Path, max_chars: int, used: int, memory_filter=None) -> dict[str, Any]:
        """Fill the remaining budget with NOW items (newest first) and memory (most important first).

        Guardrails are always returned in full and count against the budget first.
        """
        budget = max(max_chars, MIN_MAX_CONTEXT_CHARS) - used
        now = now_rows(vault)
        now_ids = {meta["id"] for _, meta, _, _ in now}
        memory = [
            row for row in active_memory_rows(vault)
            if row[0]["id"] not in now_ids and (memory_filter is None or memory_filter(row[0]))
        ]
        memory.sort(key=self._importance_key, reverse=True)
        now_items = [(meta, body, path) for _, meta, body, path in now]
        # NOW gets at most a share of the budget first so durable memory (preferences, facts) is never
        # crowded out by recent activity; whatever memory leaves unused flows back to NOW.
        now_lines, rest = self._take(vault, now_items, int(budget * NOW_BUDGET_SHARE), NOW_ITEM_MAX_CHARS)
        budget -= int(budget * NOW_BUDGET_SHARE) - rest
        memory_lines, budget = self._take(vault, memory, budget)
        more_now, budget = self._take(vault, now_items[len(now_lines):], budget, NOW_ITEM_MAX_CHARS)
        now_lines += more_now
        omitted = {"now": len(now) - len(now_lines), "memory": len(memory) - len(memory_lines)}
        result: dict[str, Any] = {
            "now": "\n".join(now_lines),
            "memory": "\n".join(memory_lines),
            "omitted": omitted,
        }
        if omitted["now"] or omitted["memory"]:
            result["more"] = (
                "Some lower-priority items were omitted to save context. Use pmo_search for a topic, "
                "or pmo_read_file('MEMORY.md') / pmo_read_file('NOW.md') for the full views."
            )
        return result

    @staticmethod
    def _take(vault: Path, rows, budget: int, item_max: int = ITEM_MAX_CHARS) -> tuple[list[str], int]:
        lines: list[str] = []
        for meta, body, path in rows:
            text = " ".join(body.split())
            if len(text) > item_max:
                text = text[: item_max - 1] + "…"
            topic = f" [{meta['topic']}]" if meta.get("topic") else ""
            line = (
                f"- ({meta.get('type')}) {text}{topic}{scope_label(meta)}{inference_label(meta)}"
                f" · {path.relative_to(vault).as_posix()}"
            )
            if len(line) + 1 > budget:
                break
            lines.append(line)
            budget -= len(line) + 1
        return lines, budget

    def _after_write(self, vault: Path, record_id: str, path: Path) -> dict[str, Any]:
        rebuild_views(vault)
        self._index_fresh = False
        return {"id": record_id, "path": path.relative_to(vault).as_posix(), "views_refreshed": True}

    @staticmethod
    def _check_known_ids(directory: Path, ids: list[str], schema: str | None = None) -> None:
        if not ids:
            return
        rows = read_events(directory, schema) if schema else read_events(directory)
        known = {meta["id"] for meta, _, _ in rows}
        missing = [i for i in ids if i not in known]
        if missing:
            raise ValueError(f"Unknown IDs in supersedes: {', '.join(missing)}")

    @staticmethod
    def _views_stale(vault: Path) -> bool:
        guardrails = vault / "GUARDRAILS.md"
        if not guardrails.is_file():
            return True
        paths = VaultPaths(vault)
        newest = max(
            (p.stat().st_mtime for d in (paths.events, paths.corrections) for p in d.glob("*.md")),
            default=0.0,
        )
        return newest > guardrails.stat().st_mtime


def build_server(vault: Path | None, max_context_chars: int = DEFAULT_MAX_CONTEXT_CHARS):
    """Create the MCP server. Requires the optional ``mcp`` dependency."""
    from mcp.server.mcpserver import MCPServer
    from mcp.types import ToolAnnotations

    tools = PMOTools(vault, max_context_chars)
    server = MCPServer(name="pmo", title="Personal Memory OS", instructions=INSTRUCTIONS)
    read_only = ToolAnnotations(readOnlyHint=True, idempotentHint=True, openWorldHint=False)
    append_only = ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=False)

    @server.tool(annotations=read_only)
    def pmo_bootstrap(max_chars: int | None = None) -> dict[str, Any]:
        """Load the user's PMO context: all global guardrails (corrections), then current focus and the most
        important global memories within a character budget, plus memory policy, custom rules and the user's
        categories. Call once at the start of a session; call pmo_category_context when the conversation enters
        a listed category. "omitted" counts items left out. Returns available=false if PMO cannot be reached."""
        return tools.bootstrap(max_chars)

    @server.tool(annotations=read_only)
    def pmo_category_context(categories: list[str], max_chars: int | None = None) -> dict[str, Any]:
        """Load the guardrails (in full) and most important memories for one or more categories from
        pmo_bootstrap, including those recorded in their parent categories. Pass every category the
        conversation touches, e.g. ["digital/video-editing", "work"]."""
        return tools.category_context(categories, max_chars)

    @server.tool(annotations=read_only)
    def pmo_search(query: str, limit: int = 10) -> dict[str, Any]:
        """Full-text search over the user's PMO records. Returns vault-relative paths and snippets."""
        return tools.search(query, limit)

    @server.tool(annotations=read_only)
    def pmo_read_file(path: str) -> dict[str, Any]:
        """Read one .md or .yaml file inside the PMO vault by vault-relative path,
        e.g. START_HERE.md or 10_Memory/Events/<id>.md."""
        return tools.read_file(path)

    @server.tool(annotations=append_only)
    def pmo_record_memory(
        type: MemoryType,
        content: str,
        topic: str | None = None,
        importance: float = 0.7,
        explicitness: Literal["explicit", "inferred"] = "explicit",
        confidence: float = 1.0,
        supersedes: list[str] | None = None,
        status: Literal["active", "archived"] = "active",
        source: str = "mcp",
        scope: list[str] | None = None,
    ) -> dict[str, Any]:
        """Append one memory event. Use only for what the user asked to save or the memory policy allows.
        Preferences and working style use type=preference. To change a recorded item, pass the old IDs in
        supersedes; to retire one, also set status=archived. Mark AI inferences explicitness=inferred with an
        honest confidence. Set source to the assistant name (e.g. claude-code, codex). scope: ["global"] only
        for things that matter in every conversation; otherwise the best matching category path from
        pmo_bootstrap (or a new one such as "digital/video-editing"); several are allowed."""
        return tools.record_memory(
            type, content, topic, importance, explicitness, confidence, supersedes, status, source, scope,
        )

    @server.tool(annotations=append_only)
    def pmo_record_correction(
        wrong: str,
        correct: str,
        trigger: str | None = None,
        topic: str | None = None,
        priority: Priority = "critical",
        repeat_error_count: int = 1,
        supersedes: list[str] | None = None,
        source: str = "mcp",
        scope: list[str] | None = None,
    ) -> dict[str, Any]:
        """Append a user correction: the AI assumption that was wrong and the user's correct understanding.
        Corrections outrank ordinary memory. Add trigger (the situation in which it applies) only when the
        user's correction makes it clear. Use supersedes with a higher repeat_error_count for repeated errors.
        scope: ["global"] for how to behave in every conversation (language, tone, honesty); otherwise the
        narrowest category it applies to, so narrow one-off corrections are not loaded in every session."""
        return tools.record_correction(
            wrong, correct, trigger, topic, priority, repeat_error_count, supersedes, source, scope,
        )

    @server.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=True))
    def pmo_set_scope(ids: list[str], scope: list[str]) -> dict[str, Any]:
        """Classify existing memories or corrections: replace their scope in place (content is untouched).
        Use for classifying, splitting, merging or renaming categories after the user approved the change.
        To change what a record says, record a superseding one instead."""
        return tools.set_scope(ids, scope)

    @server.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=True))
    def pmo_rebuild() -> dict[str, Any]:
        """Regenerate MEMORY/NOW/GUARDRAILS/INDEX and the local search index from canonical records."""
        return tools.rebuild()

    @server.tool(annotations=read_only)
    def pmo_doctor() -> dict[str, Any]:
        """Check vault integrity. If records cannot be parsed, follow _system/skills/pmo-doctor-repair/SKILL.md."""
        return tools.doctor()

    return server


def resolve_vault(value: str | None) -> Path | None:
    raw = value or os.environ.get(VAULT_ENV)
    return Path(raw) if raw else None


def serve(vault: Path | None, max_context_chars: int = DEFAULT_MAX_CONTEXT_CHARS) -> None:
    build_server(vault, max_context_chars).run("stdio")
