import io
import json
from pathlib import Path

import pytest
import yaml

from personal_memory_os.cli import main
from personal_memory_os.deploy import install
from personal_memory_os.frontmatter import load_file
from personal_memory_os.runtime_index import rebuild_index, search
from personal_memory_os.transcripts import (
    ArchivingDisabled,
    handle_claude_code_hook,
    import_claude_code,
    redact,
    sync_claude_code,
)

SESSION = "11111111-2222-3333-4444-555555555555"


def _vault(tmp_path: Path, *, archiving: bool = True) -> Path:
    vault = tmp_path / "vault"
    install(vault)
    settings_path = vault / "_config" / "settings.yaml"
    settings = yaml.safe_load(settings_path.read_text(encoding="utf-8"))
    settings["privacy"]["raw_chat_archiving"] = archiving
    settings_path.write_text(yaml.safe_dump(settings, allow_unicode=True), encoding="utf-8")
    return vault


def _user(text, ts, **extra):
    return {"type": "user", "uuid": f"u-{ts}", "sessionId": SESSION, "timestamp": ts,
            "cwd": "/work/demo", "message": {"role": "user", "content": text}, **extra}


def _assistant(blocks, ts):
    return {"type": "assistant", "uuid": f"a-{ts}", "sessionId": SESSION, "timestamp": ts,
            "message": {"role": "assistant", "content": blocks}}


def _write_log(folder: Path, entries: list[dict]) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    log = folder / f"{SESSION}.jsonl"
    log.write_text("\n".join(json.dumps(e, ensure_ascii=False) for e in entries) + "\n", encoding="utf-8")
    return log


def _entries() -> list[dict]:
    return [
        _user("過去のチャットはどこに保存される？<system-reminder>injected</system-reminder>",
              "2026-10-21T13:49:26.000Z", origin={"kind": "human"}),
        _assistant([{"type": "thinking", "thinking": "private reasoning"}], "2026-10-21T13:49:30.000Z"),
        _assistant([{"type": "tool_use", "name": "Bash",
                     "input": {"command": "ls", "description": "List session files"}}],
                   "2026-10-21T13:49:31.000Z"),
        _user([{"type": "tool_result", "content": "SECRET TOOL OUTPUT"}], "2026-10-21T13:49:32.000Z"),
        _assistant([{"type": "text", "text": "# 答え\n\nサーバーです。\n\n```\n# not a heading\n```"}],
                   "2026-10-21T13:49:33.000Z"),
        _user("<command-name>/compact</command-name><command-args></command-args>",
              "2026-10-21T13:50:00.000Z"),
        _user("<local-command-stdout>compacted</local-command-stdout>", "2026-10-21T13:50:01.000Z"),
        _user("Caveat: harness", "2026-10-21T13:50:02.000Z", isMeta=True),
        _user("This session is being continued from a previous conversation...",
              "2026-10-21T13:50:03.000Z", isCompactSummary=True),
        _user("<task-notification>done</task-notification>", "2026-10-21T13:50:04.000Z",
              origin={"kind": "task-notification"}),
        _user("subagent prompt", "2026-10-21T13:50:05.000Z", isSidechain=True),
        _user([{"type": "text", "text": "キーは OPENAI_API_KEY=sk-proj-abcdefghijklmnopqrstuvwx です"},
               {"type": "image", "source": {"type": "base64", "data": "AAAA"}}],
              "2026-10-21T13:51:00.000Z", origin={"kind": "human"}),
        {"type": "ai-title", "aiTitle": "保存場所の質問", "sessionId": SESSION},
    ]


def test_import_keeps_only_conversation_text(tmp_path: Path):
    vault = _vault(tmp_path)
    log = _write_log(tmp_path / "projects" / "-work-demo", _entries())

    result = import_claude_code(vault, log)

    assert result["status"] == "written"
    assert result["path"] == f"60_Transcripts/2026-10-21/claude-code_{SESSION}.md"
    meta, body = load_file(vault / result["path"])
    assert meta["schema"] == "pmo.transcript/v1"
    assert meta["session_id"] == SESSION
    assert meta["title"] == "保存場所の質問"
    assert meta["cwd"] == "/work/demo"
    assert meta["started_at"].startswith("2026-10-21T22:49:26")  # vault timezone (Asia/Tokyo)
    assert meta["redactions"] == 1
    assert "## 2026-10-21 22:49 User\n\n過去のチャットはどこに保存される？" in body
    assert "- tool `Bash`: List session files" in body
    assert "\n### 答え" in body and "# not a heading" in body
    assert "/compact" in body and "[image]" in body
    assert "OPENAI_API_KEY=[REDACTED:" in body
    for dropped in ("injected", "private reasoning", "SECRET TOOL OUTPUT", "compacted", "Caveat",
                    "being continued", "done", "subagent prompt", "abcdefghijklmnop"):
        assert dropped not in body, dropped


def test_import_without_metadata_keeps_the_original_frontmatter(tmp_path: Path):
    vault = _vault(tmp_path)
    log = _write_log(tmp_path / "projects" / "-work-demo", _entries())

    meta, body = load_file(vault / import_claude_code(vault, log)["path"])

    assert list(meta) == [
        "schema", "source", "session_id", "title", "cwd", "started_at", "updated_at", "turns", "redactions",
    ]
    assert "## 2026-10-21 22:49 Assistant\n" in body


def _model_reply(text, ts, model, *, effort=None, message_id=None, usage=None):
    entry = _assistant([{"type": "text", "text": text}], ts)
    entry["message"].update({"model": model, "id": message_id or f"msg-{ts}"})
    if usage:
        entry["message"]["usage"] = usage
    if effort:
        entry["effort"] = effort
    return {**entry, "entrypoint": "claude-desktop", "version": "2.1.308"}


def test_import_records_models_effort_app_and_tokens(tmp_path: Path):
    vault = _vault(tmp_path)
    usage = {"input_tokens": 10, "cache_creation_input_tokens": 5, "cache_read_input_tokens": 100,
             "output_tokens": 7}
    entries = [
        _user("質問", "2026-10-21T13:49:26.000Z", origin={"kind": "human"}),
        # One API response logged as two entries with the same message id and usage.
        _model_reply("前半", "2026-10-21T13:49:30.000Z", "claude-opus-5-5", effort="medium",
                     message_id="msg-1", usage=usage),
        _model_reply("後半", "2026-10-21T13:49:31.000Z", "claude-opus-5-5", effort="medium",
                     message_id="msg-1", usage=usage),
        _model_reply("harness note", "2026-10-21T13:49:32.000Z", "<synthetic>"),
        _user("次", "2026-10-21T13:50:00.000Z", origin={"kind": "human"}),
        _model_reply("同じ設定", "2026-10-21T13:50:01.000Z", "claude-opus-5-5", effort="medium",
                     message_id="msg-2", usage=usage),
        _user("切り替えた", "2026-10-21T13:51:00.000Z", origin={"kind": "human"}),
        _model_reply("別のモデル", "2026-10-21T13:51:01.000Z", "claude-sonnet-5-5", effort="high",
                     message_id="msg-3", usage=usage),
    ]
    log = _write_log(tmp_path / "projects" / "-work-demo", entries)

    meta, body = load_file(vault / import_claude_code(vault, log)["path"])

    assert meta["app"] == "claude-desktop" and meta["app_version"] == "2.1.308"
    assert meta["models"] == ["claude-opus-5-5", "claude-sonnet-5-5"]
    assert meta["efforts"] == ["medium", "high"]
    assert meta["tokens"] == {"input": 345, "cached_input": 300, "output": 21}
    assert "## 2026-10-21 22:49 Assistant (claude-opus-5-5, effort: medium)\n\n前半\n\n後半" in body
    assert "## 2026-10-21 22:50 Assistant\n\n同じ設定" in body  # unchanged settings are not repeated
    assert "## 2026-10-21 22:51 Assistant (claude-sonnet-5-5, effort: high)\n\n別のモデル" in body


def test_import_requires_archiving_enabled(tmp_path: Path):
    vault = _vault(tmp_path, archiving=False)
    log = _write_log(tmp_path / "projects" / "-work-demo", _entries())

    with pytest.raises(ArchivingDisabled):
        import_claude_code(vault, log)
    assert handle_claude_code_hook(vault, {"hook_event_name": "Stop", "transcript_path": str(log)}) is None
    assert not (vault / "60_Transcripts").exists()


def test_reimport_is_idempotent_and_follows_log_growth(tmp_path: Path):
    vault = _vault(tmp_path)
    folder = tmp_path / "projects" / "-work-demo"
    entries = _entries()
    log = _write_log(folder, entries)
    first = import_claude_code(vault, log)

    assert import_claude_code(vault, log)["status"] == "unchanged"

    entries.append(_assistant([{"type": "text", "text": "追記した返答"}], "2026-10-22T01:00:00.000Z"))
    _write_log(folder, entries)
    again = import_claude_code(vault, log)
    assert again["status"] == "written"
    assert again["path"] == first["path"]  # the file stays under the session's start date
    assert "追記した返答" in (vault / again["path"]).read_text(encoding="utf-8")


def test_sync_skips_subagent_logs_and_empty_sessions(tmp_path: Path):
    vault = _vault(tmp_path)
    projects = tmp_path / "projects"
    _write_log(projects / "-work-demo", _entries())
    _write_log(projects / "-work-demo" / SESSION / "subagents", _entries())
    (projects / "-work-other").mkdir(parents=True)
    (projects / "-work-other" / "empty.jsonl").write_text('{"type": "mode"}\n', encoding="utf-8")

    result = sync_claude_code(vault, projects)

    assert result["counts"] == {"written": 1, "empty": 1}
    assert len(list((vault / "60_Transcripts").rglob("*.md"))) == 1


def test_search_excludes_transcripts_unless_requested(tmp_path: Path):
    vault = _vault(tmp_path)
    _write_log(tmp_path / "projects" / "-work-demo", _entries())
    sync_claude_code(vault, tmp_path / "projects")
    (vault / "60_Transcripts" / "2026-10-21" / "extra.md").write_text("zebrafish transcript", encoding="utf-8")
    rebuild_index(vault)

    assert search(vault, "zebrafish") == []
    rows = search(vault, "zebrafish", include_transcripts=True)
    assert [r["path"] for r in rows] == ["60_Transcripts/2026-10-21/extra.md"]


def test_hook_imports_and_reports_session_on_start(tmp_path: Path, monkeypatch):
    vault = _vault(tmp_path)
    projects = tmp_path / "projects"
    log = _write_log(projects / "-work-demo", _entries())
    monkeypatch.setattr("personal_memory_os.transcripts.default_claude_projects", lambda: projects)

    context = handle_claude_code_hook(
        vault, {"hook_event_name": "SessionStart", "session_id": SESSION, "transcript_path": str(log)},
    )

    assert f'source_session="claude-code:{SESSION}"' in context
    assert f"60_Transcripts/2026-10-21/claude-code_{SESSION}.md" in context
    assert handle_claude_code_hook(
        vault, {"hook_event_name": "Stop", "session_id": SESSION, "transcript_path": str(log)},
    ) is None


def test_cli_hook_never_fails(tmp_path: Path, monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", io.StringIO("not json"))
    assert main(["transcripts", "hook", str(tmp_path / "missing")]) == 0
    assert "pmo transcripts hook" in capsys.readouterr().err


def test_cli_record_source_session(tmp_path: Path):
    vault = _vault(tmp_path)
    assert main(["record", str(vault), "--type", "fact", "--content", "x",
                 "--source-session", f"claude-code:{SESSION}"]) == 0
    (path,) = (vault / "10_Memory" / "Events").glob("*.md")
    meta, _ = load_file(path)
    assert meta["source_session"] == f"claude-code:{SESSION}"


@pytest.mark.parametrize(
    "text",
    [
        "sk-ant-api03-" + "a" * 40,
        "OPENAI_KEY sk-proj-" + "d" * 40,
        "(sk-" + "e" * 40 + ")",
        "ghp_" + "b" * 36,
        "AKIAABCDEFGHIJKLMNOP",
        "Authorization: Bearer " + "c" * 30,
        "-----BEGIN OPENSSH PRIVATE KEY-----\nabc\n-----END OPENSSH PRIVATE KEY-----",
        'password: "hunter2hunter2"',
    ],
)
def test_redact_secrets(text: str):
    redacted, count = redact(text)
    assert count == 1 and "[REDACTED:" in redacted


@pytest.mark.parametrize(
    "text",
    [
        "Password:\nFetching escape-0.0.4.gem", "トークン数は 8,000 文字まで", "api_key は環境変数に置く",
        "https://example.com/blog/closing-the-credential-risk-gap-for-ai-agents-2026",
        "task-runner-for-long-jobs-with-retries", "desk-organizer-ideas-for-small-rooms",
    ],
)
def test_redact_leaves_ordinary_text(text: str):
    assert redact(text) == (text, 0)
