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


def test_correction_trigger_is_written_validated_and_shown(tmp_path):
    from personal_memory_os.deploy import install
    from personal_memory_os.doctor import run_doctor
    from personal_memory_os.events import now_for_vault, write_correction
    from personal_memory_os.models import CorrectionEvent
    from personal_memory_os.views import rebuild_views

    vault = tmp_path / "vault"
    install(vault)
    correction = CorrectionEvent(
        id="trigger-case", wrong="Remote Control works with API keys",
        correct="Remote Control needs Claude for Enterprise",
        created_at=now_for_vault(vault), source="test",
        trigger="When advising on Claude Code Remote Control",
    )
    path = write_correction(vault, correction)
    rebuild_views(vault)

    assert "## Trigger\nWhen advising on Claude Code Remote Control" in path.read_text(encoding="utf-8")
    assert "When advising on Claude Code Remote Control" in (vault / "GUARDRAILS.md").read_text(encoding="utf-8")
    assert next(c for c in run_doctor(vault) if c.name == "memory_parse").ok


def test_empty_correction_trigger_section_is_rejected(tmp_path):
    from personal_memory_os.deploy import install
    from personal_memory_os.doctor import run_doctor
    from personal_memory_os.events import now_for_vault, write_correction
    from personal_memory_os.models import CorrectionEvent

    vault = tmp_path / "vault"
    install(vault)
    path = write_correction(vault, CorrectionEvent(
        id="empty-trigger", wrong="a", correct="b", created_at=now_for_vault(vault), source="test",
    ))
    path.write_text(path.read_text(encoding="utf-8") + "\n## Trigger\n\n", encoding="utf-8")
    assert not next(c for c in run_doctor(vault) if c.name == "memory_parse").ok


def test_install_does_not_create_unused_memory_folders(tmp_path):
    from personal_memory_os.deploy import install

    vault = tmp_path / "vault"
    install(vault)
    for name in ("Self", "Preferences", "Decisions"):
        assert not (vault / "10_Memory" / name).exists()
    assert (vault / "10_Memory" / "Events").is_dir()
