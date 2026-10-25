import json
from pathlib import Path

import yaml

from personal_memory_os.cli import main
from personal_memory_os.deploy import install
from personal_memory_os.frontmatter import load_file
from personal_memory_os.transcripts import handle_claude_code_hook, import_codex, sync_codex

THREAD = "019fb3a2-fc8f-71c0-a808-5663e49e7896"


def _vault(tmp_path: Path) -> Path:
    vault = tmp_path / "vault"
    install(vault)
    settings_path = vault / "_config" / "settings.yaml"
    settings = yaml.safe_load(settings_path.read_text(encoding="utf-8"))
    settings["privacy"]["raw_chat_archiving"] = True
    settings_path.write_text(yaml.safe_dump(settings, allow_unicode=True), encoding="utf-8")
    return vault


def _line(kind, payload, ts="2026-07-30T15:29:23.061Z"):
    return {"timestamp": ts, "type": kind, "payload": payload}


def _message(role, *blocks, ts="2026-07-30T15:29:23.061Z", msg_id=None):
    kind = "output_text" if role == "assistant" else "input_text"
    content = [b if isinstance(b, dict) else {"type": kind, "text": b} for b in blocks]
    payload = {"type": "message", "role": role, "content": content}
    if msg_id:
        payload["id"] = msg_id
    return _line("response_item", payload, ts)


def _meta(thread=THREAD, **extra):
    return _line("session_meta", {"id": thread, "session_id": thread, "cwd": "/work/demo",
                                  "originator": "Codex Desktop", "cli_version": "0.162.0", **extra})


def _context(model="gpt-6.1-sol", effort="low"):
    return _line("turn_context", {"model": model, "effort": effort, "cwd": "/work/demo"})


def _entries() -> list[dict]:
    return [
        _meta(),
        _message("developer", "<permissions instructions>sandbox</permissions instructions>"),
        _message("user", "# AGENTS.md instructions\n\n<INSTRUCTIONS>rules</INSTRUCTIONS>",
                 "<environment_context>\n  <cwd>/work/demo</cwd>\n</environment_context>"),
        _context(effort="xhigh"),
        _message("user", "\n# Files mentioned by the user:\n\n## spec excerpt…: /tmp/attachments/pasted-text.txt\n\n"
                 "## My request for Codex:\n添付に従って実装して", ts="2026-07-30T15:29:24.000Z"),
        _line("response_item", {"type": "reasoning", "summary": [{"text": "private reasoning"}]}),
        _message("assistant", "まず仕様を読みます。", ts="2026-07-30T15:29:30.000Z", msg_id="msg_1"),
        _message("assistant", "まず仕様を読みます。", ts="2026-07-30T15:29:30.000Z", msg_id="msg_1"),
        _line("response_item", {"type": "custom_tool_call", "name": "exec", "call_id": "c1",
                                "input": 'const r = await tools.exec_command({\n  cmd: "sed -n 1,20p spec.txt",\n})'}),
        _line("response_item", {"type": "custom_tool_call_output", "call_id": "c1", "output": "TOOL OUTPUT"}),
        _line("response_item", {"type": "custom_tool_call", "name": "exec", "call_id": "c2",
                                "input": 'const patch = "*** Begin Patch\\n*** Add File: app/main.py\\n+print()";'
                                         "\nawait tools.apply_patch(patch);"}),
        _line("response_item", {"type": "function_call", "name": "js", "namespace": "mcp__cua_repl",
                                "arguments": json.dumps({"code": "x", "title": "アプリの状態を確認"})}),
        _context(model="gpt-6.1-sol", effort="low"),
        _message("user", '\n<in-app-browser-context source="ambient-ui-state">\nURL\n</in-app-browser-context>\n\n'
                 "## My request for Codex:\n画面を見て", {"type": "input_image", "image_url": "data:"},
                 ts="2026-07-30T16:00:00.000Z"),
        _message("user", '<send_user_message_question_reply>\n[{"question": "認証しましたか？", '
                 '"answer": "認証を完了した"}]\n</send_user_message_question_reply>',
                 ts="2026-07-30T16:00:05.000Z"),
        _message("user", '<codex_internal_context source="goal">\nContinue.\n</codex_internal_context>',
                 ts="2026-07-30T16:00:06.000Z"),
        _message("assistant", "# 結果\n\n確認しました。key: sk-proj-abcdefghijklmnopqrstuvwx",
                 ts="2026-07-30T16:00:10.000Z"),
        _line("event_msg", {"type": "token_count", "info": {"total_token_usage": {
            "input_tokens": 1000, "cached_input_tokens": 800, "output_tokens": 50, "reasoning_output_tokens": 20,
        }}}),
    ]


def _write(home: Path, entries: list[dict], thread=THREAD) -> Path:
    folder = home / "sessions" / "2026" / "07" / "31"
    folder.mkdir(parents=True, exist_ok=True)
    log = folder / f"rollout-2026-07-31T00-29-23-{thread}.jsonl"
    log.write_text("\n".join(json.dumps(e, ensure_ascii=False) for e in entries) + "\n", encoding="utf-8")
    return log


def test_import_codex_keeps_conversation_text_and_metadata(tmp_path: Path):
    vault = _vault(tmp_path)
    home = tmp_path / "codex"
    log = _write(home, _entries())
    (home / "session_index.jsonl").write_text(
        json.dumps({"id": THREAD, "thread_name": "古い名前"}) + "\n"
        + json.dumps({"id": THREAD, "thread_name": "非同期アプリの実装"}) + "\n", encoding="utf-8",
    )

    result = import_codex(vault, log)

    assert result["path"] == f"60_Transcripts/2026-07-31/codex_{THREAD}.md"
    meta, body = load_file(vault / result["path"])
    assert meta["source"] == "codex" and meta["session_id"] == THREAD
    assert meta["title"] == "非同期アプリの実装"
    assert meta["cwd"] == "/work/demo"
    assert meta["app"] == "Codex Desktop" and meta["app_version"] == "0.162.0"
    assert meta["models"] == ["gpt-6.1-sol"] and meta["efforts"] == ["xhigh", "low"]
    assert meta["tokens"] == {"input": 1000, "cached_input": 800, "output": 50, "reasoning": 20}
    assert meta["redactions"] == 1
    assert "## 2026-07-31 00:29 User\n\n[file: pasted-text.txt]\n\n添付に従って実装して" in body
    assert "## 2026-07-31 00:29 Assistant (gpt-6.1-sol, effort: xhigh)\n\nまず仕様を読みます。\n\n- tool" in body
    assert body.count("まず仕様を読みます。") == 1
    assert "- tool `exec_command`: sed -n 1,20p spec.txt" in body
    assert "- tool `apply_patch`: app/main.py" in body
    assert "- tool `mcp__cua_repl.js`: アプリの状態を確認" in body
    assert "画面を見て\n\n[image]" in body
    assert "> 認証しましたか？\n\n認証を完了した" in body
    assert "## 2026-07-31 01:00 Assistant (gpt-6.1-sol, effort: low)\n\n### 結果" in body
    for dropped in ("AGENTS.md", "INSTRUCTIONS", "environment_context", "permissions", "private reasoning",
                    "TOOL OUTPUT", "in-app-browser-context", "My request", "Continue.", "abcdefghijklmnop"):
        assert dropped not in body, dropped


def test_codex_skips_subagents_and_imported_history(tmp_path: Path):
    vault = _vault(tmp_path)
    home = tmp_path / "codex"
    _write(home, _entries())
    _write(home, [_meta("sub-1", parent_thread_id=THREAD), _context(), _message("user", "subagent task")], "sub-1")
    # A conversation imported from another app: its history is in the log, but Codex never ran a turn.
    _write(home, [_meta("imported-1"), _message("user", "imported question"),
                  _message("assistant", "imported answer")], "imported-1")

    result = sync_codex(vault, home)

    assert result["counts"] == {"written": 1, "empty": 2}
    assert sync_codex(vault, home)["counts"] == {"unchanged": 3}


def test_cli_sync_covers_both_apps_and_hook_syncs_codex(tmp_path: Path, monkeypatch, capsys):
    vault = _vault(tmp_path)
    home = tmp_path / "codex"
    _write(home, _entries())

    assert main(["transcripts", "sync", str(vault), "--codex-home", str(home),
                 "--projects", str(tmp_path / "none")]) == 0
    assert json.loads(capsys.readouterr().out)["counts"] == {"claude-code": {}, "codex": {"written": 1}}

    monkeypatch.setenv("CODEX_HOME", str(home))
    target = vault / f"60_Transcripts/2026-07-31/codex_{THREAD}.md"
    target.unlink()
    handle_claude_code_hook(vault, {"hook_event_name": "SessionStart", "session_id": "s"})
    assert not target.exists()  # unchanged logs are skipped
    handle_claude_code_hook(vault, {"hook_event_name": "Stop", "session_id": "s"})
    assert main(["transcripts", "sync", str(vault), "--source", "codex", "--force"]) == 0
    assert target.exists()
