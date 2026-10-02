from pathlib import Path

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
