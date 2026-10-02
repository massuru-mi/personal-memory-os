from datetime import date
from pathlib import Path

from personal_memory_os.daily import render_day_summary, write_session
from personal_memory_os.deploy import install
from personal_memory_os.events import new_event_id, now_for_vault, write_memory_event
from personal_memory_os.models import MemoryEvent
from personal_memory_os.views import rebuild_views


def test_memory_event_renders_memory_and_now(tmp_path: Path):
    vault = tmp_path / "vault"
    install(vault)
    at = now_for_vault(vault)
    event = MemoryEvent(
        id=new_event_id("mem", at),
        type="decision",
        content="Use Markdown as canonical memory.",
        created_at=at,
        source="test",
        importance=0.9,
        topic="architecture",
    )
    write_memory_event(vault, event)
    rebuild_views(vault)
    assert "Use Markdown as canonical memory." in (vault / "MEMORY.md").read_text(encoding="utf-8")
    assert "Use Markdown as canonical memory." in (vault / "NOW.md").read_text(encoding="utf-8")


def test_daily_session_merges_incremental_turns(tmp_path: Path):
    vault = tmp_path / "vault"
    install(vault)
    day = date(2026, 10, 2)
    path = write_session(vault, source="chatgpt", session_id="s1", topic="design", day=day, done=["A"])
    write_session(vault, source="chatgpt", session_id="s1", topic="design", day=day, decisions=["B"])
    text = path.read_text(encoding="utf-8")
    assert "- A" in text
    assert "- B" in text
    summary = render_day_summary(vault, day)
    assert summary and "design (chatgpt)" in summary.read_text(encoding="utf-8")
