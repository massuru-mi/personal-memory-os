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
from .events import new_event_id, now_for_vault, read_events, write_correction, write_memory_event
from .models import CorrectionEvent, MemoryEvent
from .paths import VaultPaths
from .runtime_index import rebuild_index, search
from .validation import CORRECTION_SCHEMA
from .views import rebuild_views

VAULT_ENV = "PMO_VAULT"

INSTRUCTIONS = """\
PMO (Personal Memory OS) is connected: the user's own memory, shared across AI assistants.
At the start of the session, before relying on personal context, call pmo_bootstrap once and follow what it returns.
- User corrections (guardrails) outrank everything else, including ordinary memory.
- Save only what the user asks to save, or what the returned memory policy allows; otherwise propose the save.
- Write memories and corrections only with pmo_record_memory / pmo_record_correction. Never edit PMO files by hand.
- To change or retire a recorded item, record a new one that supersedes it.
If pmo_bootstrap reports PMO as unavailable, tell the user once and continue without PMO.
"""

MemoryType = Literal[
    "fact", "preference", "decision", "project_progress", "open_loop",
    "current_focus", "interest", "relationship", "knowledge",
]
Priority = Literal["low", "normal", "high", "critical"]
VIEW_FILES = {"guardrails": "GUARDRAILS.md", "memory": "MEMORY.md", "now": "NOW.md"}


class PMOTools:
    """Tool implementations, kept independent of the MCP SDK for testing."""

    def __init__(self, vault: Path | None):
        self.vault = vault.expanduser().resolve() if vault else None
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

    def bootstrap(self) -> dict[str, Any]:
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
        for key, name in VIEW_FILES.items():
            path = vault / name
            result[key] = path.read_text(encoding="utf-8") if path.is_file() else ""
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
    ) -> dict[str, Any]:
        vault = self._require_vault()
        supersedes = supersedes or []
        self._check_known_ids(VaultPaths(vault).events, supersedes)
        at = now_for_vault(vault)
        event = MemoryEvent(
            id=new_event_id("mem", at), type=type, content=content, created_at=at, source=source,
            importance=importance, status=status, topic=topic, confidence=confidence,
            explicitness=explicitness, supersedes=supersedes,
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
    ) -> dict[str, Any]:
        vault = self._require_vault()
        supersedes = supersedes or []
        self._check_known_ids(VaultPaths(vault).corrections, supersedes, CORRECTION_SCHEMA)
        at = now_for_vault(vault)
        correction = CorrectionEvent(
            id=new_event_id("correction", at), wrong=wrong, correct=correct, created_at=at, source=source,
            priority=priority, topic=topic, repeat_error_count=repeat_error_count,
            supersedes=supersedes, trigger=trigger,
        )
        path = write_correction(vault, correction)
        return self._after_write(vault, correction.id, path)

    def rebuild(self) -> dict[str, Any]:
        vault = self._require_vault()
        views = [p.name for p in rebuild_views(vault)]
        rebuild_index(vault)
        self._index_fresh = True
        return {"views": views, "index": "rebuilt"}

    # -- helpers ------------------------------------------------------------

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


def build_server(vault: Path | None):
    """Create the MCP server. Requires the optional ``mcp`` dependency."""
    from mcp.server.mcpserver import MCPServer
    from mcp.types import ToolAnnotations

    tools = PMOTools(vault)
    server = MCPServer(name="pmo", title="Personal Memory OS", instructions=INSTRUCTIONS)
    read_only = ToolAnnotations(readOnlyHint=True, idempotentHint=True, openWorldHint=False)
    append_only = ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=False)

    @server.tool(annotations=read_only)
    def pmo_bootstrap() -> dict[str, Any]:
        """Load the user's PMO context: guardrails (corrections), memory, current focus, memory policy and
        custom rules. Call once at the start of a session. Returns available=false if PMO cannot be reached."""
        return tools.bootstrap()

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
    ) -> dict[str, Any]:
        """Append one memory event. Use only for what the user asked to save or the memory policy allows.
        Preferences and working style use type=preference. To change a recorded item, pass the old IDs in
        supersedes; to retire one, also set status=archived. Mark AI inferences explicitness=inferred with an
        honest confidence. Set source to the assistant name (e.g. claude-code, codex)."""
        return tools.record_memory(
            type, content, topic, importance, explicitness, confidence, supersedes, status, source,
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
    ) -> dict[str, Any]:
        """Append a user correction: the AI assumption that was wrong and the user's correct understanding.
        Corrections outrank ordinary memory. Add trigger (the situation in which it applies) only when the
        user's correction makes it clear. Use supersedes with a higher repeat_error_count for repeated errors."""
        return tools.record_correction(
            wrong, correct, trigger, topic, priority, repeat_error_count, supersedes, source,
        )

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


def serve(vault: Path | None) -> None:
    build_server(vault).run("stdio")
