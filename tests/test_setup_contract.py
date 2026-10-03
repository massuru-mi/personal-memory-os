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
            assert term not in source, f"{term!r} remains in {path.relative_to(REPO_ROOT)}"


def test_refresh_views_skill_is_deployed_and_referenced():
    repo_skill = (REPO_ROOT / "skills" / "pmo-refresh-views" / "SKILL.md").read_text(encoding="utf-8")
    deployed_skill = read_system_text("skills/pmo-refresh-views/SKILL.md")
    start = read_system_text("START_HERE.md")
    assert repo_skill == deployed_skill
    assert "pmo-refresh-views/SKILL.md" in start
    assert "pmo rebuild" in repo_skill
    assert "fail closed" in repo_skill


def test_canonical_file_format_rules_are_in_system_docs():
    start = read_system_text("START_HERE.md")
    assert "_system/templates/" in start
    assert "UTF-8 without a BOM" in start
    assert "LF line endings" in start
    correction = read_system_text("protocols/CORRECTION_PROTOCOL.md")
    assert "## Wrong assumption" in correction
    assert "## Correct understanding" in correction
    assert "never put these in frontmatter" in correction
    assert "_system/templates/memory-event.md" in read_system_text("protocols/MEMORY_PROTOCOL.md")
    assert "_system/templates/daily-session.md" in read_system_text("protocols/DAILY_PROTOCOL.md")
