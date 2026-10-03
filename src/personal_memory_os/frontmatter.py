from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .errors import ValidationError


def dumps(frontmatter: dict[str, Any], body: str) -> str:
    meta = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False).rstrip()
    return f"---\n{meta}\n---\n\n{body.rstrip()}\n"


def loads(text: str) -> tuple[dict[str, Any], str]:
    # Cloud writers (e.g. ChatGPT via Drive) may emit a UTF-8 BOM and CRLF line endings.
    text = text.removeprefix("﻿").replace("\r\n", "\n").replace("\r", "\n")
    if not text.startswith("---\n"):
        raise ValidationError("missing YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValidationError("unterminated YAML frontmatter")
    raw = text[4:end]
    data = yaml.safe_load(raw) or {}
    if not isinstance(data, dict):
        raise ValidationError("frontmatter must be a mapping")
    return data, text[end + 5 :].lstrip("\n")


def load_file(path: Path) -> tuple[dict[str, Any], str]:
    return loads(path.read_text(encoding="utf-8"))
