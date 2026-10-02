from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from .constants import CONFIG_DIR, DAILY_DIR, MEMORY_DIR, SYSTEM_DIR


@dataclass(frozen=True)
class VaultPaths:
    root: Path

    @property
    def system(self) -> Path:
        return self.root / SYSTEM_DIR

    @property
    def config(self) -> Path:
        return self.root / CONFIG_DIR

    @property
    def memory(self) -> Path:
        return self.root / MEMORY_DIR

    @property
    def events(self) -> Path:
        return self.memory / "Events"

    @property
    def corrections(self) -> Path:
        return self.memory / "Corrections"

    @property
    def daily(self) -> Path:
        return self.root / DAILY_DIR

    def runtime_root(self) -> Path:
        digest = hashlib.sha256(str(self.root.resolve()).encode("utf-8")).hexdigest()[:16]
        return Path.home() / ".personal-memory-os" / digest
