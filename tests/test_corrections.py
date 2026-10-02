from pathlib import Path

from personal_memory_os.deploy import install
from personal_memory_os.events import new_event_id, now_for_vault, write_correction
from personal_memory_os.models import CorrectionEvent
from personal_memory_os.views import rebuild_views


def test_correction_renders_guardrail(tmp_path: Path):
    vault = tmp_path / "vault"
    install(vault)
    at = now_for_vault(vault)
    correction = CorrectionEvent(
        id=new_event_id("correction", at),
        wrong="Store AI files in the original folder.",
        correct="Keep AI-specific files in a separate mirror.",
        created_at=at,
        source="test",
        topic="storage",
    )
    write_correction(vault, correction)
    rebuild_views(vault)
    text = (vault / "GUARDRAILS.md").read_text(encoding="utf-8")
    assert "Store AI files" in text
    assert "separate mirror" in text
