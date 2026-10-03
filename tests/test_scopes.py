from pathlib import Path

import pytest

from personal_memory_os.cli import main
from personal_memory_os.deploy import install
from personal_memory_os.doctor import run_doctor
from personal_memory_os.errors import ValidationError
from personal_memory_os.events import now_for_vault, write_memory_event
from personal_memory_os.frontmatter import load_file
from personal_memory_os.ingest import ingest_turn
from personal_memory_os.mcp_server import PMOTools
from personal_memory_os.models import MemoryEvent
from personal_memory_os.scopes import applies_to, validate_scope


@pytest.fixture
def vault(tmp_path: Path) -> Path:
    root = tmp_path / "vault"
    install(root)
    return root


@pytest.mark.parametrize("scope", [
    [], "digital", [""], [" digital"], ["a//b"], ["a/"], ["global/x"], ["global", "work"], ["work", "work"], [1],
])
def test_invalid_scopes_are_rejected(scope):
    with pytest.raises(ValidationError):
        validate_scope(scope)


def test_valid_scopes():
    validate_scope(["global"])
    validate_scope(["digital/video-editing", "仕事"])


def test_parent_category_applies_to_child_but_not_the_reverse():
    parent = {"scope": ["digital"]}
    child = {"scope": ["digital/video-editing"]}
    assert applies_to(parent, ["digital/video-editing"])
    assert applies_to(child, ["digital/video-editing"])
    assert not applies_to(child, ["digital"])
    assert applies_to(child, ["daily-life", "digital/video-editing"])
    assert not applies_to({"scope": ["global"]}, ["digital"])
    assert not applies_to({}, ["digital"])


def test_scope_is_written_only_when_given_and_invalid_scope_fails_doctor(vault: Path):
    at = now_for_vault(vault)
    plain = write_memory_event(vault, MemoryEvent(id="plain", type="fact", content="x", created_at=at, source="t"))
    assert "scope" not in load_file(plain)[0]
    scoped = write_memory_event(vault, MemoryEvent(
        id="scoped", type="fact", content="y", created_at=at, source="t", scope=["digital"],
    ))
    assert load_file(scoped)[0]["scope"] == ["digital"]
    scoped.write_text(scoped.read_text(encoding="utf-8").replace("- digital", "- global/x"), encoding="utf-8")
    assert not next(c for c in run_doctor(vault) if c.name == "memory_parse").ok


def test_views_group_guardrails_and_list_categories(vault: Path):
    tools = PMOTools(vault)
    tools.record_correction("Answer in English", "Answer in Japanese", topic="language")
    tools.record_correction("Blue box is granules", "Blue box is tablets", topic="kampo", scope=["daily-life/health"])
    tools.record_memory("preference", "Edits videos in DaVinci", scope=["digital/video-editing"])

    guardrails = (vault / "GUARDRAILS.md").read_text(encoding="utf-8")
    assert guardrails.index("## Global") < guardrails.index("## daily-life/health")
    assert "#### Wrong assumption" in guardrails
    assert "{digital/video-editing}" in (vault / "MEMORY.md").read_text(encoding="utf-8")
    index = (vault / "INDEX.md").read_text(encoding="utf-8")
    assert "- digital: 1 memories, 0 corrections (1 recent)" in index
    assert "- daily-life/health: 0 memories, 1 corrections (1 recent)" in index


def test_bootstrap_loads_only_global_and_lists_categories(vault: Path):
    tools = PMOTools(vault)
    tools.record_correction("Answer in English", "Answer in Japanese")
    tools.record_correction("Blue box is granules", "Blue box is tablets", scope=["daily-life/health"])
    tools.record_memory("preference", "Likes concise tables")
    tools.record_memory("preference", "Edits videos in DaVinci", scope=["digital/video-editing"])

    result = tools.bootstrap()
    assert "Answer in Japanese" in result["guardrails"]
    assert "Blue box" not in result["guardrails"]
    assert "Likes concise tables" in result["memory"]
    assert "DaVinci" not in result["memory"]
    names = {c["category"] for c in result["categories"]}
    assert {"daily-life", "daily-life/health", "digital", "digital/video-editing"} <= names


def test_category_context_includes_parents_and_multiple_categories(vault: Path):
    tools = PMOTools(vault)
    tools.record_correction("Any app works", "Check the OS first", scope=["digital"])
    tools.record_correction("Blue box is granules", "Blue box is tablets", scope=["daily-life/health"])
    tools.record_memory("preference", "Edits videos in DaVinci", scope=["digital/video-editing"])
    tools.record_memory("fact", "Child goes to nursery", scope=["family"])

    video = tools.category_context(["digital/video-editing"])
    assert "Check the OS first" in video["guardrails"]
    assert "DaVinci" in video["memory"]
    assert "Blue box" not in video["guardrails"]

    both = tools.category_context(["digital/video-editing", "family"])
    assert "DaVinci" in both["memory"] and "nursery" in both["memory"]
    assert tools.category_context(["cooking"])["unknown_categories"] == ["cooking"]
    with pytest.raises(ValueError):
        tools.category_context([])


def test_cli_and_ingest_accept_scope(vault: Path, capsys):
    assert main(["record", str(vault), "--type", "fact", "--content", "cli fact", "--scope", "work"]) == 0
    assert main(["correct", str(vault), "--wrong", "a", "--correct", "b", "--scope", "work", "--scope", "family"]) == 0
    ingest_turn(vault, {"memory_events": [{"type": "fact", "content": "ingested", "scope": ["digital"]}]})
    scopes = sorted(
        tuple(load_file(p)[0].get("scope", []))
        for p in (vault / "10_Memory").rglob("*.md")
    )
    assert scopes == [("digital",), ("work",), ("work", "family")]


def test_set_scope_changes_only_the_scope_line(vault: Path):
    tools = PMOTools(vault)
    saved = tools.record_memory("fact", "Body stays exactly the same", topic="t")
    path = vault / saved["path"]
    before = path.read_text(encoding="utf-8")

    from personal_memory_os.events import set_scope
    set_scope(vault, [saved["id"]], ["子ども"])
    after = path.read_text(encoding="utf-8")
    assert load_file(path)[0]["scope"] == ["子ども"]
    assert [line for line in after.splitlines() if not line.startswith("scope:")] == before.splitlines()

    set_scope(vault, [saved["id"]], ["global"])
    assert after.count("scope:") == 1
    assert load_file(path)[0]["scope"] == ["global"]


def test_set_scope_replaces_block_list_and_handles_crlf_bom(vault: Path):
    tools = PMOTools(vault)
    saved = tools.record_correction("w", "c", scope=["a", "b"])
    path = vault / saved["path"]
    text = path.read_text(encoding="utf-8").replace('scope:\n- a\n- b\n', 'scope:\n  - a\n  - b\n')
    path.write_bytes(b"\xef\xbb\xbf" + text.replace("\n", "\r\n").encode("utf-8"))

    from personal_memory_os.events import set_scope
    set_scope(vault, [saved["id"]], ["日常生活/健康"])
    meta, body = load_file(path)
    assert meta["scope"] == ["日常生活/健康"]
    assert "## Wrong assumption\nw" in body
    assert next(c for c in run_doctor(vault) if c.name == "memory_parse").ok


def test_set_scope_is_all_or_nothing(vault: Path):
    tools = PMOTools(vault)
    saved = tools.record_memory("fact", "x")
    from personal_memory_os.events import set_scope
    with pytest.raises(ValidationError):
        set_scope(vault, [saved["id"], "no-such-id"], ["work"])
    with pytest.raises(ValidationError):
        set_scope(vault, [saved["id"]], ["global/x"])
    assert "scope" not in load_file(vault / saved["path"])[0]


def test_set_scope_via_cli_and_mcp_updates_views(vault: Path):
    tools = PMOTools(vault)
    a = tools.record_correction("Blue box is granules", "Blue box is tablets")
    b = tools.record_memory("fact", "Child sleeps at 23:00")
    assert main(["set-scope", str(vault), a["id"], "--scope", "日常生活/健康"]) == 0
    tools.set_scope([b["id"]], ["子ども"])
    guardrails = (vault / "GUARDRAILS.md").read_text(encoding="utf-8")
    assert "## 日常生活/健康" in guardrails and "## Global" not in guardrails
    assert "Blue box" not in tools.bootstrap()["guardrails"]
    assert "Child sleeps" in tools.category_context(["子ども"])["memory"]
