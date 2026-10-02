from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

from .events import read_events
from .paths import VaultPaths

_WS = re.compile(r"\s+")


@dataclass(slots=True)
class DuplicateGroup:
    fingerprint: str
    paths: list[Path]


def _fingerprint(text: str) -> str:
    normalized = _WS.sub(" ", text.strip().casefold())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def find_exact_duplicates(vault_root: Path) -> list[DuplicateGroup]:
    paths = VaultPaths(vault_root)
    groups: dict[str, list[Path]] = {}
    for _, body, path in read_events(paths.events):
        fp = _fingerprint(body)
        groups.setdefault(fp, []).append(path)
    return [DuplicateGroup(fp, items) for fp, items in groups.items() if len(items) > 1]
