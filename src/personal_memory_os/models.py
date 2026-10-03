from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any

from .validation import CORRECTION_SCHEMA, MEMORY_SCHEMA, require_text, validate_fields


@dataclass(slots=True)
class MemoryEvent:
    id: str
    type: str
    content: str
    created_at: datetime
    source: str
    importance: float = 0.5
    status: str = "active"
    topic: str | None = None
    confidence: float = 1.0
    explicitness: str = "explicit"
    supersedes: list[str] = field(default_factory=list)
    scope: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        validate_fields({**asdict(self), "schema": MEMORY_SCHEMA, "scope": self.scope or None}, MEMORY_SCHEMA)
        require_text(self.content, "content")


@dataclass(slots=True)
class CorrectionEvent:
    id: str
    wrong: str
    correct: str
    created_at: datetime
    source: str
    priority: str = "critical"
    topic: str | None = None
    status: str = "active"
    repeat_error_count: int = 1
    supersedes: list[str] = field(default_factory=list)
    trigger: str | None = None
    scope: list[str] = field(default_factory=list)

    def validate(self) -> None:
        validate_fields(
            {**asdict(self), "schema": CORRECTION_SCHEMA, "type": "correction", "scope": self.scope or None},
            CORRECTION_SCHEMA,
        )
        require_text(self.wrong, "wrong")
        require_text(self.correct, "correct")
        if self.trigger is not None:
            require_text(self.trigger, "trigger")
