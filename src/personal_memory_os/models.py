from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .errors import ValidationError

ALLOWED_EVENT_TYPES = {
    "fact",
    "preference",
    "decision",
    "project_progress",
    "open_loop",
    "current_focus",
    "interest",
    "relationship",
    "knowledge",
}
ALLOWED_STATUS = {"active", "superseded", "archived"}
ALLOWED_PRIORITY = {"low", "normal", "high", "critical"}


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
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.id.strip():
            raise ValidationError("event id is required")
        if self.type not in ALLOWED_EVENT_TYPES:
            raise ValidationError(f"unsupported event type: {self.type}")
        if not self.content.strip():
            raise ValidationError("event content is required")
        if not 0 <= self.importance <= 1:
            raise ValidationError("importance must be between 0 and 1")
        if not 0 <= self.confidence <= 1:
            raise ValidationError("confidence must be between 0 and 1")
        if self.status not in ALLOWED_STATUS:
            raise ValidationError(f"unsupported status: {self.status}")


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

    def validate(self) -> None:
        if not self.id.strip():
            raise ValidationError("correction id is required")
        if not self.wrong.strip() or not self.correct.strip():
            raise ValidationError("wrong and correct are required")
        if self.priority not in ALLOWED_PRIORITY:
            raise ValidationError(f"unsupported priority: {self.priority}")
        if self.status not in ALLOWED_STATUS:
            raise ValidationError(f"unsupported status: {self.status}")
        if self.repeat_error_count < 1:
            raise ValidationError("repeat_error_count must be >= 1")
