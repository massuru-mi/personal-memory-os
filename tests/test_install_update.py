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
    assert (vault / "_config" / "settings.yaml").exists()
    assert (vault / "10_Memory" / "Events").is_dir()
    assert detect_drift(vault) == []


def test_update_preserves_data_and_config(tmp_path: Path):
    vault = tmp_path / "vault"
    install(vault)
    private = vault / "20_Projects" / "private.md"
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
