from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path


def create_backup(vault_root: Path, output_dir: Path | None = None) -> Path:
    output_dir = output_dir or (vault_root.parent / "PMO-Backups")
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().astimezone().strftime("%Y%m%dT%H%M%S%z")
    base = output_dir / f"{vault_root.name}-{stamp}"
    archive = shutil.make_archive(str(base), "zip", root_dir=vault_root)
    return Path(archive)
