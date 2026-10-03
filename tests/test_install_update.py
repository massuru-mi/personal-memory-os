import json
from pathlib import Path

import pytest

from personal_memory_os.deploy import detect_drift, install, update
from personal_memory_os.errors import DriftError


def test_install_creates_owned_and_private_layers(tmp_path: Path):
    vault = tmp_path / "vault"
    version = install(vault)
    assert version["system_version"] == "1.1.0"
    assert (vault / "START_HERE.md").exists()
    assert (vault / "_system" / "protocols" / "MEMORY_PROTOCOL.md").exists()
    assert (vault / "_system" / "skills" / "pmo-refresh-views" / "SKILL.md").exists()
    assert (vault / "_config" / "settings.yaml").exists()
    assert (vault / "10_Memory" / "Events").is_dir()
    assert detect_drift(vault) == []


def test_install_does_not_create_unused_note_folders(tmp_path: Path):
    vault = tmp_path / "vault"
    install(vault)
    for name in ("00_Inbox", "20_Projects", "30_Knowledge", "40_Decisions"):
        assert not (vault / name).exists()
        assert f"[[{name}]]" not in (vault / "INDEX.md").read_text(encoding="utf-8")
    for name in ("50_Daily", "80_Archive"):
        assert (vault / name).is_dir()


def test_update_preserves_data_and_config(tmp_path: Path):
    vault = tmp_path / "vault"
    install(vault)
    private = vault / "20_Projects" / "private.md"
    private.parent.mkdir()
    private.write_text("secret\n", encoding="utf-8")
    settings = vault / "_config" / "settings.yaml"
    text = settings.read_text(encoding="utf-8").replace("importance_threshold: 0.6", "importance_threshold: 0.42")
    settings.write_text(text, encoding="utf-8")
    update(vault, backup=False)
    assert private.read_text(encoding="utf-8") == "secret\n"
    assert "importance_threshold: 0.42" in settings.read_text(encoding="utf-8")


def test_update_fails_closed_on_system_drift(tmp_path: Path):
    vault = tmp_path / "vault"
    install(vault)
    target = vault / "_system" / "protocols" / "MEMORY_PROTOCOL.md"
    target.write_text(target.read_text(encoding="utf-8") + "\nmanual edit\n", encoding="utf-8")
    assert detect_drift(vault)
    with pytest.raises(DriftError):
        update(vault, backup=False)


def test_install_deploys_remember_and_repair_skills(tmp_path: Path):
    vault = tmp_path / "vault"
    install(vault)
    for name in ("pmo-remember", "pmo-doctor-repair"):
        assert (vault / "_system" / "skills" / name / "SKILL.md").exists()


def test_install_deploys_agent_entrypoints_and_custom_rules(tmp_path: Path):
    vault = tmp_path / "vault"
    result = install(vault)
    assert result["skipped_existing"] == []
    assert "START_HERE.md" in (vault / "AGENTS.md").read_text(encoding="utf-8")
    assert (vault / "CLAUDE.md").read_text(encoding="utf-8").strip() == "@AGENTS.md"
    assert (vault / "_config" / "custom_rules.md").exists()
    assert not (vault / "_system" / "entrypoints").exists()


def test_existing_user_agent_files_are_never_overwritten(tmp_path: Path):
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "CLAUDE.md").write_text("my own rules\n", encoding="utf-8")
    result = install(vault)
    assert result["skipped_existing"] == ["CLAUDE.md"]
    assert (vault / "CLAUDE.md").read_text(encoding="utf-8") == "my own rules\n"
    assert (vault / "AGENTS.md").exists()
    assert detect_drift(vault) == []
    result = update(vault, backup=False)
    assert result["skipped_existing"] == ["CLAUDE.md"]
    assert (vault / "CLAUDE.md").read_text(encoding="utf-8") == "my own rules\n"


def test_update_adds_entrypoints_and_keeps_custom_rules(tmp_path: Path):
    vault = tmp_path / "vault"
    install(vault)
    for name in ("AGENTS.md", "CLAUDE.md"):
        (vault / name).unlink()
    manifest = vault / "_system" / "SYSTEM_MANIFEST.json"
    data = json.loads(manifest.read_text(encoding="utf-8"))
    for name in ("AGENTS.md", "CLAUDE.md"):
        data["owned_files"].pop(name)
    manifest.write_text(json.dumps(data), encoding="utf-8")
    rules = vault / "_config" / "custom_rules.md"
    rules.write_text("- answer in Japanese\n", encoding="utf-8")

    update(vault, backup=False)

    assert (vault / "AGENTS.md").exists()
    assert rules.read_text(encoding="utf-8") == "- answer in Japanese\n"


def test_edited_agent_entrypoint_is_system_drift(tmp_path: Path):
    vault = tmp_path / "vault"
    install(vault)
    (vault / "AGENTS.md").write_text("edited\n", encoding="utf-8")
    assert "modified:AGENTS.md" in detect_drift(vault)
