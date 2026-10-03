from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from . import CONFIG_SCHEMA_VERSION, DATA_SCHEMA_VERSION, SYSTEM_SCHEMA_VERSION, __version__
from .backup import create_backup
from .config import deep_merge, dump_yaml, load_yaml
from .constants import (
    CUSTOM_RULES_FILE,
    DATA_DIRECTORIES,
    MANIFEST_FILE,
    ROOT_SYSTEM_FILES,
    SETTINGS_FILE,
    SYSTEM_DIR,
    VERSION_FILE,
)
from .errors import DriftError
from .io import atomic_write_json, atomic_write_text, sha256_file
from .migrations import CONFIG_MIGRATIONS, DATA_MIGRATIONS, migrate
from .resources import iter_system_files, read_system_text
from .views import rebuild_views


def read_version(root: Path) -> dict[str, Any]:
    path = root / VERSION_FILE
    if not path.exists():
        return {"system_version": "0.0.0", "config_schema_version": 0, "data_schema_version": 0}
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {"system_version": "0.0.0", "config_schema_version": 0, "data_schema_version": 0}
    end = text.find("\n---\n", 4)
    data = yaml.safe_load(text[4:end]) or {}
    return data


def _version_doc(*, installed_at: str | None, deployed_commit: str | None = None) -> str:
    now = datetime.now().astimezone().isoformat()
    meta = {
        "system": "personal-memory-os",
        "system_version": __version__,
        "system_schema_version": SYSTEM_SCHEMA_VERSION,
        "config_schema_version": CONFIG_SCHEMA_VERSION,
        "data_schema_version": DATA_SCHEMA_VERSION,
        "deployed_commit": deployed_commit,
        "installed_at": installed_at or now,
        "updated_at": now,
    }
    front = yaml.safe_dump(meta, allow_unicode=True, sort_keys=False).rstrip()
    return f"---\n{front}\n---\n\n# Personal Memory OS\n\nInstalled system version: `{__version__}`.\n"


def _load_manifest(root: Path) -> dict[str, Any]:
    path = root / MANIFEST_FILE
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def detect_drift(root: Path) -> list[str]:
    manifest = _load_manifest(root)
    drift: list[str] = []
    for rel, expected in manifest.get("owned_files", {}).items():
        path = root / rel
        if not path.exists():
            drift.append(f"missing:{rel}")
        elif sha256_file(path) != expected:
            drift.append(f"modified:{rel}")
    return drift


def _deploy_root_files(root: Path, previously_owned: dict[str, str]) -> tuple[dict[str, str], list[str]]:
    """Deploy vault-root System files without taking over files the user already had."""
    owned: dict[str, str] = {}
    skipped: list[str] = []
    for name, resource in ROOT_SYSTEM_FILES.items():
        target = root / name
        if target.exists() and name not in previously_owned:
            skipped.append(name)
            continue
        atomic_write_text(target, read_system_text(resource))
        owned[name] = sha256_file(target)
    return owned, skipped


def _deploy_system(root: Path) -> list[str]:
    previously_owned = _load_manifest(root).get("owned_files", {})
    owned, skipped = _deploy_root_files(root, previously_owned)
    skip_resources = set(ROOT_SYSTEM_FILES.values()) | {"defaults/settings.yaml", "defaults/custom_rules.md"}
    for resource, rel in iter_system_files():
        if rel in skip_resources:
            continue
        destination = root / SYSTEM_DIR / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        atomic_write_text(destination, resource.read_text(encoding="utf-8"))
        owned[destination.relative_to(root).as_posix()] = sha256_file(destination)
    manifest = {
        "system": "personal-memory-os",
        "version": __version__,
        "owned_files": owned,
        "protected_paths": [
            "_config/**",
            "00_Inbox/**",
            "10_Memory/**",
            "20_Projects/**",
            "30_Knowledge/**",
            "40_Decisions/**",
            "50_Daily/**",
            "80_Archive/**",
        ],
        "generated_views": ["MEMORY.md", "NOW.md", "GUARDRAILS.md", "INDEX.md", VERSION_FILE],
    }
    atomic_write_json(root / MANIFEST_FILE, manifest)
    return skipped


def _merge_settings(root: Path) -> None:
    defaults = yaml.safe_load(read_system_text("defaults/settings.yaml")) or {}
    path = root / SETTINGS_FILE
    existing = load_yaml(path)
    merged = deep_merge(defaults, existing)
    atomic_write_text(path, dump_yaml(merged))


def _ensure_custom_rules(root: Path) -> None:
    path = root / CUSTOM_RULES_FILE
    if not path.exists():
        atomic_write_text(path, read_system_text("defaults/custom_rules.md"))


def install(root: Path, *, deployed_commit: str | None = None) -> dict[str, Any]:
    root.mkdir(parents=True, exist_ok=True)
    for rel in DATA_DIRECTORIES:
        (root / rel).mkdir(parents=True, exist_ok=True)
    (root / "_config").mkdir(parents=True, exist_ok=True)
    _merge_settings(root)
    _ensure_custom_rules(root)
    skipped = _deploy_system(root)
    atomic_write_text(root / VERSION_FILE, _version_doc(installed_at=None, deployed_commit=deployed_commit))
    rebuild_views(root)
    result = read_version(root)
    result["skipped_existing"] = skipped
    return result


def update(
    root: Path,
    *,
    force_system_drift: bool = False,
    backup: bool = True,
    deployed_commit: str | None = None,
) -> dict[str, Any]:
    if not root.exists():
        raise FileNotFoundError(root)
    drift = detect_drift(root)
    if drift and not force_system_drift:
        raise DriftError("System drift detected: " + ", ".join(drift))
    previous = read_version(root)
    backup_path = create_backup(root) if backup else None
    migrate(root, int(previous.get("config_schema_version", 0)), CONFIG_SCHEMA_VERSION, CONFIG_MIGRATIONS)
    migrate(root, int(previous.get("data_schema_version", 0)), DATA_SCHEMA_VERSION, DATA_MIGRATIONS)
    _merge_settings(root)
    _ensure_custom_rules(root)
    skipped = _deploy_system(root)
    atomic_write_text(
        root / VERSION_FILE,
        _version_doc(installed_at=previous.get("installed_at"), deployed_commit=deployed_commit),
    )
    rebuild_views(root)
    result = read_version(root)
    result["backup"] = str(backup_path) if backup_path else None
    result["skipped_existing"] = skipped
    return result
