from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from .backup import create_backup
from .curator import find_exact_duplicates
from .daily import render_day_summary
from .deploy import detect_drift, install, read_version, update
from .doctor import doctor_dict
from .events import new_event_id, now_for_vault, set_scope, write_correction, write_memory_event
from .ingest import ingest_turn
from .models import CorrectionEvent, MemoryEvent
from .runtime_index import rebuild_index, search
from .views import rebuild_views


def _root(value: str) -> Path:
    return Path(value).expanduser().resolve()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pmo", description="Personal Memory OS")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("install", help="Install PMO into a private vault directory")
    p.add_argument("vault")
    p.add_argument("--commit")

    p = sub.add_parser("update", help="Deploy the installed PMO version into an existing vault")
    p.add_argument("vault")
    p.add_argument("--commit")
    p.add_argument("--force-system-drift", action="store_true")
    p.add_argument("--no-backup", action="store_true")

    p = sub.add_parser("status", help="Show PMO version and system drift")
    p.add_argument("vault")

    p = sub.add_parser("doctor", help="Validate vault integrity and ownership boundaries")
    p.add_argument("vault")

    p = sub.add_parser("rebuild", help="Rebuild generated views and local search index")
    p.add_argument("vault")

    p = sub.add_parser("record", help="Append one canonical memory event")
    p.add_argument("vault")
    p.add_argument("--type", required=True)
    p.add_argument("--content", required=True)
    p.add_argument("--source", default="cli")
    p.add_argument("--topic")
    p.add_argument("--importance", type=float, default=0.7)
    p.add_argument("--confidence", type=float, default=1.0)
    p.add_argument("--explicitness", choices=["explicit", "inferred"], default="explicit")
    p.add_argument("--scope", action="append", default=[], help="\"global\" or a category path such as digital/video-editing; repeatable (default: global)")

    p = sub.add_parser("correct", help="Append a high-priority user correction")
    p.add_argument("vault")
    p.add_argument("--wrong", required=True)
    p.add_argument("--correct", required=True)
    p.add_argument("--source", default="cli")
    p.add_argument("--topic")
    p.add_argument("--priority", choices=["low", "normal", "high", "critical"], default="critical")
    p.add_argument("--trigger", help="Situation in which this correction applies")
    p.add_argument("--scope", action="append", default=[], help="\"global\" or a category path such as digital/video-editing; repeatable (default: global)")

    p = sub.add_parser("set-scope", help="Set the scope of existing records in place (classification only)")
    p.add_argument("vault")
    p.add_argument("ids", nargs="+", help="Record IDs (memory events or corrections)")
    p.add_argument("--scope", action="append", required=True, help="\"global\" or a category path; repeatable")

    p = sub.add_parser("ingest-turn", help="Ingest a provider-neutral AI turn JSON payload")
    p.add_argument("vault")
    p.add_argument("input", help="JSON file or '-' for stdin")

    p = sub.add_parser("daily", help="Regenerate one daily summary")
    p.add_argument("vault")
    p.add_argument("day", help="YYYY-MM-DD")

    p = sub.add_parser("search", help="Search the local runtime FTS index")
    p.add_argument("vault")
    p.add_argument("query")
    p.add_argument("--limit", type=int, default=20)

    p = sub.add_parser("backup", help="Create a zip backup of the private vault")
    p.add_argument("vault")
    p.add_argument("--output")

    p = sub.add_parser("mcp", help="Serve PMO tools over MCP (stdio). Requires personal-memory-os[mcp]")
    p.add_argument("--vault", help="PMO vault path (default: $PMO_VAULT)")
    p.add_argument(
        "--max-context-chars", type=int, default=8000,
        help="Character budget for pmo_bootstrap memory context; guardrails are always included (default: 8000)",
    )

    p = sub.add_parser("duplicates", help="Report exact duplicate memory events")
    p.add_argument("vault")
    return parser


def _emit(data, as_json: bool) -> None:
    if as_json or isinstance(data, (dict, list)):
        print(json.dumps(data, ensure_ascii=False, indent=2, default=str))
    else:
        print(data)


def run(args: argparse.Namespace) -> object:
    cmd = args.command
    if cmd == "install":
        return install(_root(args.vault), deployed_commit=args.commit)
    if cmd == "update":
        return update(
            _root(args.vault),
            force_system_drift=args.force_system_drift,
            backup=not args.no_backup,
            deployed_commit=args.commit,
        )
    if cmd == "status":
        root = _root(args.vault)
        return {"version": read_version(root), "system_drift": detect_drift(root)}
    if cmd == "doctor":
        return doctor_dict(_root(args.vault))
    if cmd == "rebuild":
        root = _root(args.vault)
        views = [str(p) for p in rebuild_views(root)]
        db = rebuild_index(root)
        return {"views": views, "index": str(db)}
    if cmd == "record":
        root = _root(args.vault)
        at = now_for_vault(root)
        event = MemoryEvent(
            id=new_event_id("mem", at),
            type=args.type,
            content=args.content,
            created_at=at,
            source=args.source,
            importance=args.importance,
            topic=args.topic,
            confidence=args.confidence,
            explicitness=args.explicitness,
            scope=args.scope,
        )
        path = write_memory_event(root, event)
        rebuild_views(root)
        return {"path": str(path), "id": event.id}
    if cmd == "correct":
        root = _root(args.vault)
        at = now_for_vault(root)
        event = CorrectionEvent(
            id=new_event_id("correction", at),
            wrong=args.wrong,
            correct=args.correct,
            created_at=at,
            source=args.source,
            topic=args.topic,
            priority=args.priority,
            trigger=args.trigger,
            scope=args.scope,
        )
        path = write_correction(root, event)
        rebuild_views(root)
        return {"path": str(path), "id": event.id}
    if cmd == "ingest-turn":
        raw = sys.stdin.read() if args.input == "-" else Path(args.input).read_text(encoding="utf-8")
        return ingest_turn(_root(args.vault), json.loads(raw))
    if cmd == "daily":
        path = render_day_summary(_root(args.vault), date.fromisoformat(args.day))
        return {"path": str(path) if path else None}
    if cmd == "search":
        return search(_root(args.vault), args.query, args.limit)
    if cmd == "backup":
        out = Path(args.output).expanduser().resolve() if args.output else None
        return {"path": str(create_backup(_root(args.vault), out))}
    if cmd == "set-scope":
        root = _root(args.vault)
        changed = set_scope(root, args.ids, args.scope)
        rebuild_views(root)
        return {"updated": [str(p) for p in changed], "scope": args.scope}
    if cmd == "duplicates":
        return [
            {"fingerprint": group.fingerprint, "paths": [str(p) for p in group.paths]}
            for group in find_exact_duplicates(_root(args.vault))
        ]
    raise RuntimeError(f"Unknown command: {cmd}")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "mcp":
        return _serve_mcp(args.vault, args.max_context_chars)
    try:
        result = run(args)
        _emit(result, args.json)
        return 0
    except Exception as exc:  # noqa: BLE001 - CLI boundary reports unexpected failures cleanly
        if args.json:
            _emit({"error": type(exc).__name__, "message": str(exc)}, True)
        else:
            print(f"error: {exc}", file=sys.stderr)
        return 1


def _serve_mcp(vault: str | None, max_context_chars: int) -> int:
    # stdout carries the MCP protocol, so nothing else may be printed there.
    try:
        from .mcp_server import resolve_vault, serve
        serve(resolve_vault(vault), max_context_chars)
    except ModuleNotFoundError as exc:
        if exc.name and exc.name.split(".")[0] == "mcp":
            print("error: MCP support is not installed. Install personal-memory-os[mcp].", file=sys.stderr)
            return 1
        raise
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
