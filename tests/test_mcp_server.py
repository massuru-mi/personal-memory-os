import os
import time
from pathlib import Path

import pytest

from personal_memory_os.deploy import install
from personal_memory_os.errors import ValidationError
from personal_memory_os.mcp_server import INSTRUCTIONS, PMOTools


@pytest.fixture
def vault(tmp_path: Path) -> Path:
    root = tmp_path / "vault"
    install(root)
    return root


def test_unavailable_vault_is_reported_not_raised(tmp_path: Path):
    assert PMOTools(None).bootstrap()["available"] is False
    missing = PMOTools(tmp_path / "not-mounted").bootstrap()
    assert missing["available"] is False
    assert "not-mounted" in missing["reason"]
    with pytest.raises(RuntimeError):
        PMOTools(tmp_path / "not-mounted").record_memory("fact", "x")


def test_bootstrap_returns_views_policy_and_custom_rules(vault: Path):
    tools = PMOTools(vault)
    tools.record_correction("wrong idea", "right idea", trigger="when it matters")
    result = tools.bootstrap()
    assert result["available"] is True
    assert "right idea" in result["guardrails"]
    assert "when it matters" in result["guardrails"]
    assert result["policy"]["memory"]["auto_save"] is False
    assert "Custom rules" in result["custom_rules"]
    assert result["warnings"] == []


def test_bootstrap_refreshes_views_after_external_write(vault: Path):
    tools = PMOTools(vault)
    tools.record_memory("fact", "first fact")
    # Simulate a cloud assistant writing a record without refreshing views.
    other = PMOTools(vault)
    path = vault / other.record_memory("fact", "cloud fact")["path"]
    (vault / "MEMORY.md").write_text("# Memory\n", encoding="utf-8")
    old = time.time() - 60
    os.utime(vault / "GUARDRAILS.md", (old, old))
    os.utime(path, None)
    assert "cloud fact" in tools.bootstrap()["memory"]


def test_record_memory_supersedes_and_retires(vault: Path):
    tools = PMOTools(vault)
    first = tools.record_memory("preference", "Prefers short answers", topic="communication")
    assert (vault / first["path"]).is_file()
    second = tools.record_memory("preference", "Prefers detailed answers", supersedes=[first["id"]])
    memory = (vault / "MEMORY.md").read_text(encoding="utf-8")
    assert "Prefers detailed answers" in memory
    assert "Prefers short answers" not in memory
    tools.record_memory("preference", "Retired", status="archived", supersedes=[second["id"]])
    assert "Prefers detailed answers" not in (vault / "MEMORY.md").read_text(encoding="utf-8")
    with pytest.raises(ValueError, match="Unknown IDs"):
        tools.record_memory("fact", "x", supersedes=["no-such-id"])


def test_invalid_memory_is_rejected_before_writing(vault: Path):
    tools = PMOTools(vault)
    with pytest.raises(ValidationError):
        tools.record_memory("not-a-type", "x")
    assert not any((vault / "10_Memory" / "Events").glob("*.md"))


def test_search_sees_new_records(vault: Path):
    tools = PMOTools(vault)
    assert tools.search("zebrafish")["results"] == []
    tools.record_memory("fact", "Zebrafish note for search")
    assert any("10_Memory" in row["path"] for row in tools.search("zebrafish")["results"])


def test_read_file_stays_inside_vault(vault: Path, tmp_path: Path):
    tools = PMOTools(vault)
    assert "Start Here" in tools.read_file("START_HERE.md")["content"]
    (tmp_path / "outside.md").write_text("secret", encoding="utf-8")
    with pytest.raises(ValueError):
        tools.read_file("../outside.md")
    with pytest.raises(ValueError):
        tools.read_file("_system/SYSTEM_MANIFEST.json")


def test_doctor_reports_ok(vault: Path):
    assert PMOTools(vault).doctor()["ok"] is True


def test_mcp_server_exposes_tools_and_instructions(vault: Path):
    anyio = pytest.importorskip("anyio")
    pytest.importorskip("mcp")
    from mcp import Client

    from personal_memory_os.mcp_server import build_server

    async def scenario():
        async with Client(build_server(vault)) as client:
            names = {tool.name for tool in (await client.list_tools()).tools}
            assert names == {
                "pmo_bootstrap", "pmo_category_context", "pmo_search", "pmo_read_file", "pmo_record_memory",
                "pmo_record_correction", "pmo_set_scope", "pmo_rebuild", "pmo_doctor",
            }
            assert client.instructions == INSTRUCTIONS
            saved = await client.call_tool("pmo_record_memory", {
                "type": "preference", "content": "Answers in Japanese", "source": "test",
            })
            assert not saved.is_error
            boot = await client.call_tool("pmo_bootstrap", {})
            assert boot.structured_content["available"] is True
            assert "Answers in Japanese" in boot.structured_content["memory"]
            bad = await client.call_tool("pmo_record_memory", {"type": "nope", "content": "x"})
            assert bad.is_error

        async with Client(build_server(None)) as client:
            boot = await client.call_tool("pmo_bootstrap", {})
            assert boot.structured_content["available"] is False

    anyio.run(scenario)


def test_bootstrap_keeps_guardrails_and_prioritizes_memory_within_budget(vault: Path):
    tools = PMOTools(vault, max_context_chars=1500)
    tools.record_correction("long wrong " * 40, "long correct " * 40)
    for i in range(30):
        tools.record_memory("fact", f"filler fact number {i} " + "x" * 60, importance=0.3)
    tools.record_memory("preference", "Most important preference", importance=0.95)
    result = tools.bootstrap()

    assert "long correct" in result["guardrails"]
    assert result["memory"].splitlines()[0].startswith("- (preference) Most important preference")
    assert result["omitted"]["memory"] > 0
    assert "pmo_search" in result["more"]
    assert len(result["guardrails"]) + len(result["now"]) + len(result["memory"]) <= 1500 + 2


def test_bootstrap_guardrails_survive_tiny_budget(vault: Path):
    tools = PMOTools(vault)
    tools.record_correction("w " * 500, "c " * 500)
    tools.record_memory("fact", "some fact")
    result = tools.bootstrap(max_chars=10)
    assert result["guardrails"].count("c c c") > 0
    assert result["memory"] == ""
    assert result["omitted"]["memory"] == 1


def test_bootstrap_does_not_repeat_now_items_in_memory(vault: Path):
    tools = PMOTools(vault)
    tools.record_memory("open_loop", "Finish the MCP budget work")
    tools.record_memory("preference", "Likes tables")
    result = tools.bootstrap()
    assert "Finish the MCP budget work" in result["now"]
    assert "Finish the MCP budget work" not in result["memory"]
    assert "Likes tables" in result["memory"]
    assert result["omitted"] == {"now": 0, "memory": 0}
    assert "more" not in result


def test_bootstrap_truncates_long_items_and_points_to_the_record(vault: Path):
    tools = PMOTools(vault)
    saved = tools.record_memory("knowledge", "y" * 2000)
    line = PMOTools(vault).bootstrap()["memory"]
    assert "…" in line
    assert saved["path"] in line
    assert len(line) < 600


def test_recent_activity_does_not_crowd_out_durable_memory(vault: Path):
    tools = PMOTools(vault, max_context_chars=2000)
    for i in range(40):
        tools.record_memory("project_progress", f"progress step {i} " + "z" * 80)
    tools.record_memory("preference", "Answers in Japanese", importance=0.9)
    result = tools.bootstrap()
    assert "Answers in Japanese" in result["memory"]
    assert result["now"]
    assert result["omitted"]["now"] > 0


def test_now_items_are_cut_shorter_than_memory_items(vault: Path):
    tools = PMOTools(vault)
    loop = tools.record_memory("open_loop", "n" * 1000)
    tools.record_memory("knowledge", "k" * 1000)
    result = tools.bootstrap()
    now_line = result["now"].splitlines()[0]
    memory_line = result["memory"].splitlines()[0]
    assert "n" * 149 + "…" in now_line and "n" * 150 not in now_line
    assert loop["path"] in now_line
    assert "k" * 399 + "…" in memory_line
