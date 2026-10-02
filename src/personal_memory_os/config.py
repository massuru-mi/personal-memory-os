from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

from .constants import SETTINGS_FILE


def deep_merge(defaults: dict[str, Any], overrides: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(defaults)
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping in {path}")
    return data


def dump_yaml(data: dict[str, Any]) -> str:
    return yaml.safe_dump(data, allow_unicode=True, sort_keys=False)


def load_settings(vault_root: Path, defaults: dict[str, Any] | None = None) -> dict[str, Any]:
    user = load_yaml(vault_root / SETTINGS_FILE)
    return deep_merge(defaults or {}, user)
