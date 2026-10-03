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


def test_remember_and_repair_skills_are_deployed_and_referenced():
    start = read_system_text("START_HERE.md")
    for name in ("pmo-remember", "pmo-doctor-repair"):
        repo_skill = (REPO_ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
        assert repo_skill == read_system_text(f"skills/{name}/SKILL.md")
        assert f"_system/skills/{name}/SKILL.md" in start
    remember = read_system_text("skills/pmo-remember/SKILL.md")
    assert "pmo correct" in remember and "--trigger" in remember
    assert "UTF-8 without a BOM" in remember
    assert "Never put these in frontmatter" in remember
    repair = read_system_text("skills/pmo-doctor-repair/SKILL.md")
    assert "pmo backup" in repair
    assert "content-preserving" in repair
    assert "--force-system-drift" in repair and "explicit approval" in repair


def test_update_and_organize_skills_are_deployed_and_referenced():
    start = read_system_text("START_HERE.md")
    for name in ("pmo-update", "pmo-organize"):
        repo_skill = (REPO_ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
        assert repo_skill == read_system_text(f"skills/{name}/SKILL.md")
        assert f"_system/skills/{name}/SKILL.md" in start
    update = read_system_text("skills/pmo-update/SKILL.md")
    assert "Never downgrade" in update
    assert "--no-backup" in update and "--force-system-drift" in update
    organize = read_system_text("skills/pmo-organize/SKILL.md")
    assert "Propose first" in organize
    assert "Never edit, delete or rename an existing canonical record" in organize


def test_agent_entrypoints_point_to_start_here():
    agents = read_system_text("entrypoints/AGENTS.vault.md")
    assert "START_HERE.md" in agents
    assert "pmo record" in agents and "pmo correct" in agents
    assert "_config/custom_rules.md" in agents
    assert read_system_text("entrypoints/CLAUDE.vault.md").strip() == "@AGENTS.md"
    assert "_config/custom_rules.md" in read_system_text("START_HERE.md")


def test_scope_rules_are_documented_for_every_writer():
    start = read_system_text("START_HERE.md")
    assert "Global" in start and "category" in start
    memory_protocol = read_system_text("protocols/MEMORY_PROTOCOL.md")
    assert "## Scope (global or category)" in memory_protocol
    assert "Categories are not predefined" in memory_protocol
    assert "scope" in read_system_text("protocols/CORRECTION_PROTOCOL.md")
    for name in ("memory-event.md", "correction.md"):
        assert "scope: [global]" in read_system_text(f"templates/{name}")
    for name in ("pmo-remember", "pmo-organize", "pmo-refresh-views"):
        repo_skill = (REPO_ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
        assert repo_skill == read_system_text(f"skills/{name}/SKILL.md")
        assert "scope" in repo_skill


def test_scope_changes_are_in_place_in_rules_and_skills():
    assert "pmo set-scope" in read_system_text("protocols/MEMORY_PROTOCOL.md")
    organize = read_system_text("skills/pmo-organize/SKILL.md")
    assert "pmo set-scope" in organize and "pmo_set_scope" in organize
    assert "a new record with the same content and fields and the new `scope`" not in organize


def test_organize_skill_intro_matches_in_place_scope_rule():
    organize = read_system_text("skills/pmo-organize/SKILL.md")
    head = organize.split("## Non-negotiable rules")[0]
    assert "every accepted change is a new record" not in head
    assert "apply only the accepted ones as new append-only records" not in head
    assert "pmo set-scope" in head and "never by superseding" in head


def test_setup_skill_warns_about_duration_resumes_and_stays_inside_destination():
    skill = (REPO_ROOT / "skills" / "pmo-setup" / "SKILL.md").read_text(encoding="utf-8")
    intro = skill.split("## Non-negotiable rules")[0]
    assert "5 分以上" in intro and "続けて" in intro
    assert "## Resuming after an interruption" in skill
    assert "Never create anything outside the approved destination" in skill
    assert ".pmo-setup-check.md" in skill
    assert "nothing was created outside the approved destination" in skill
    for readme, phrase in (("README.ja.md", "続けて"), ("README.md", "continue")):
        assert phrase in (REPO_ROOT / readme).read_text(encoding="utf-8")
