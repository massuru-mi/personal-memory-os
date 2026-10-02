from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from .constants import DATA_DIRECTORIES

Migration = Callable[[Path], None]


def _data_0_to_1(root: Path) -> None:
    for rel in DATA_DIRECTORIES:
        (root / rel).mkdir(parents=True, exist_ok=True)


def _config_0_to_1(root: Path) -> None:
    (root / "_config").mkdir(parents=True, exist_ok=True)


DATA_MIGRATIONS: dict[int, Migration] = {0: _data_0_to_1}
CONFIG_MIGRATIONS: dict[int, Migration] = {0: _config_0_to_1}


def migrate(root: Path, current: int, target: int, registry: dict[int, Migration]) -> list[str]:
    if current > target:
        raise ValueError(f"Cannot downgrade schema from {current} to {target}")
    applied: list[str] = []
    version = current
    while version < target:
        fn = registry.get(version)
        if fn is None:
            raise RuntimeError(f"Missing migration {version} -> {version + 1}")
        fn(root)
        applied.append(f"{version}->{version + 1}")
        version += 1
    return applied
