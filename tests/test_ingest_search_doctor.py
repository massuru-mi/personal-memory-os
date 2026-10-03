from pathlib import Path

import yaml

from personal_memory_os.deploy import install
from personal_memory_os.doctor import run_doctor
from personal_memory_os.ingest import ingest_turn
from personal_memory_os.runtime_index import rebuild_index, search


def test_turn_ingest_search_and_doctor(tmp_path: Path):
    vault = tmp_path / "vault"
    install(vault)
    ingest_turn(
        vault,
        {
            "source": "chatgpt",
            "session_id": "abc",
            "topic": "memory",
            "memory_events": [{"type": "fact", "content": "Portable memory is user-owned.", "importance": 0.8}],
            "corrections": [{"wrong": "Provider owns memory", "correct": "User owns memory"}],
            "session": {"done": ["Discussed ownership"]},
        },
    )
    rebuild_index(vault)
    results = search(vault, "portable")
    assert any("10_Memory" in row["path"] for row in results)
    checks = run_doctor(vault)
    assert all(check.ok for check in checks), [check for check in checks if not check.ok]


def _turn() -> dict:
    return {
        "source": "chatgpt",
        "session_id": "abc",
        "topic": "memory",
        "memory_events": [{"type": "fact", "content": "Portable memory is user-owned."}],
        "session": {"done": ["Discussed ownership"]},
    }


def test_ingest_skips_daily_when_disabled(tmp_path: Path):
    vault = tmp_path / "vault"
    install(vault)

    result = ingest_turn(vault, _turn())

    assert result["session"] is None
    assert len(result["events"]) == 1
    assert not any((vault / "50_Daily").rglob("*.md"))


def test_ingest_writes_daily_when_enabled(tmp_path: Path):
    vault = tmp_path / "vault"
    install(vault)
    settings_path = vault / "_config" / "settings.yaml"
    settings = yaml.safe_load(settings_path.read_text(encoding="utf-8"))
    settings["daily"]["enabled"] = True
    settings_path.write_text(yaml.safe_dump(settings), encoding="utf-8")

    result = ingest_turn(vault, _turn())

    assert result["session"] is not None
    assert Path(result["session"]).exists()
