from pathlib import Path

import yaml

from personal_memory_os.resources import read_system_text


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_safe_initial_memory_policy():
    settings = yaml.safe_load(read_system_text("defaults/settings.yaml"))
    assert settings["memory"]["auto_save"] is False
    assert settings["memory"]["auto_promote_explicit_decisions"] is False
    assert settings["daily"]["enabled"] is False
    assert settings["daily"]["update_on_every_meaningful_turn"] is False


def test_runtime_policy_is_in_start_here():
    start = read_system_text("START_HERE.md")
    assert "beginning of each new chat/session" in start
    assert "memory.auto_save" in start
    assert "daily.enabled" in start
    assert "Generated views" in start


def test_setup_skill_requires_destination_approval():
    skill = (REPO_ROOT / "skills" / "pmo-setup" / "SKILL.md").read_text(encoding="utf-8")
    assert "Before the first Google Drive write" in skill
    assert "My Drive/PMO" in skill
    assert "explicit approval" in skill


def test_repository_has_no_legacy_root_naming():
    forbidden = (
        "Second" + "Brain",
        "Second" + " Brain",
        "second" + " brain",
        "second" + "-brain",
    )
    text_suffixes = {".md", ".py", ".toml", ".yaml", ".yml", ".json"}
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or path.suffix not in text_suffixes:
            continue
        source = path.read_text(encoding="utf-8")
        for term in forbidden:
            assert term not in source, "%r remains in %s" % (term, path.relative_to(REPO_ROOT))
