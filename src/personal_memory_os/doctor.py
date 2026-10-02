from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

from .constants import DATA_DIRECTORIES, SETTINGS_FILE, VERSION_FILE
from .deploy import detect_drift, read_version
from .frontmatter import load_file
from .paths import VaultPaths


@dataclass(slots=True)
class Check:
    name: str
    ok: bool
    detail: str


def run_doctor(root: Path) -> list[Check]:
    checks: list[Check] = []
    checks.append(Check("vault_exists", root.exists(), str(root)))
    checks.append(Check("version_file", (root / VERSION_FILE).exists(), VERSION_FILE))
    checks.append(Check("settings", (root / SETTINGS_FILE).exists(), SETTINGS_FILE.as_posix()))
    for rel in DATA_DIRECTORIES:
        checks.append(Check(f"dir:{rel}", (root / rel).is_dir(), rel))
    drift = detect_drift(root) if (root / "_system").exists() else ["system-not-installed"]
    checks.append(Check("system_drift", not drift, ", ".join(drift) if drift else "clean"))
    paths = VaultPaths(root)
    invalid: list[str] = []
    for directory in (paths.events, paths.corrections):
        if not directory.exists():
            continue
        for path in directory.glob("*.md"):
            try:
                load_file(path)
            except Exception as exc:
                invalid.append(f"{path.name}:{type(exc).__name__}")
    checks.append(Check("memory_parse", not invalid, ", ".join(invalid) if invalid else "clean"))
    version = read_version(root)
    checks.append(Check("version_readable", bool(version.get("system_version")), str(version.get("system_version"))))
    runtime = paths.runtime_root().resolve()
    root_resolved = root.resolve()
    runtime_outside = runtime != root_resolved and root_resolved not in runtime.parents
    checks.append(Check("runtime_outside_vault", runtime_outside, str(runtime)))
    return checks


def doctor_dict(root: Path) -> list[dict]:
    return [asdict(c) for c in run_doctor(root)]
