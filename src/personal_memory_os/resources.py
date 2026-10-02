from __future__ import annotations

from importlib.resources import files


def system_root():
    return files("personal_memory_os").joinpath("system")


def read_system_text(relative: str) -> str:
    return system_root().joinpath(relative).read_text(encoding="utf-8")


def _walk(node, prefix: str = ""):
    for item in node.iterdir():
        rel = f"{prefix}/{item.name}" if prefix else item.name
        if item.is_dir():
            yield from _walk(item, rel)
        elif item.is_file():
            yield item, rel


def iter_system_files():
    yield from _walk(system_root())
