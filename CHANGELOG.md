# Changelog

## 1.3.0 - 2026-10-24

- the MCP instructions now require, before the first reply of every session and even for questions that look general, reading `START_HERE.md` with `pmo_read_file` and calling `pmo_bootstrap`; they no longer say "before relying on personal context", which let assistants skip PMO for seemingly general questions
- keep the MCP instructions within 2,048 characters, the length Claude Code keeps by default, and test it
- `START_HERE.md`: read it before the first reply; always read settings, `custom_rules.md` and the Global guardrails; read MEMORY, NOW, INDEX and records when personal context may affect the answer, with a concrete rule for when it does (the answer depends on the user's own situation, even if the question looks general; when unsure, read)
- update `docs/mcp.ja.md` and `docs/ai-integration.md` to match

## 1.2.0 - 2026-10-22

- add the raw transcript archive `60_Transcripts/`, written only when `privacy.raw_chat_archiving: true`: `pmo transcripts import|sync` converts Claude Code session logs into one Markdown file per session with only the user's and the assistant's words (tool calls become one-line markers; tool output, thinking, harness-injected text and subagent logs are dropped; API keys and similar secrets are redacted)
- add `pmo transcripts hook` for Claude Code `SessionStart` / `Stop` / `SessionEnd` hooks; it never fails the session, and at session start it tells the assistant the session ID to use as `source_session`
- search leaves transcripts out unless asked (`pmo search --include-transcripts`, `pmo_search(include_transcripts=true)`); the local index file is renamed so old indexes are rebuilt
- add optional `source_session` to memories (`pmo record --source-session`, `pmo_record_memory(source_session=...)`) to point at the conversation a memory came from
- `pmo_bootstrap` reports whether transcripts are archived and where
- note in both READMEs that connecting Google Drive in ChatGPT requires a paid plan (as of 2026-10-22)
- document the transcript archive in the MCP guide (`docs/mcp.ja.md`), the storage contract and the vault layout in `docs/local-optional-design.ja.md`
- add canonical file-format rules to `START_HERE.md`: start from `_system/templates/`, UTF-8 without BOM, LF line endings, read back before reporting saved
- clarify in the Correction Protocol that `Wrong assumption` / `Correct understanding` are required body sections, not frontmatter fields
- point the Memory and Daily protocols at their templates
- `pmo ingest-turn` now writes a Daily session file only when `daily.enabled: true`, and returns `"session": null` otherwise
- deploy `AGENTS.md` and `CLAUDE.md` (imports `AGENTS.md`) into the vault root as thin agent entrypoints; never overwrite pre-existing user files (`skipped_existing`)
- create user-owned `_config/custom_rules.md` on install; `START_HERE.md` reads it
- add optional `## Trigger` section to corrections (`pmo correct --trigger`, `ingest-turn` `trigger`), shown in GUARDRAILS
- stop creating unused `10_Memory/Self`, `10_Memory/Preferences` and `10_Memory/Decisions`; existing folders are left in place
- stop creating unused `00_Inbox/MemoryCandidates`, `20_Projects`, `30_Knowledge` and `40_Decisions`, and drop the note-folder links from `INDEX.md`; existing folders stay protected user Data
- add skills `pmo-remember`, `pmo-doctor-repair`, `pmo-update` and `pmo-organize`, deployed under `_system/skills/` and referenced from `START_HERE.md`
- add design memo `docs/agent-integration-proposals.ja.md`
- add `pmo mcp`: PMO operations as an MCP server with short session instructions; optional extra `personal-memory-os[mcp]`
- rewrite `README.ja.md` in plainer Japanese; add the one-line ChatGPT setup prompt to both READMEs and mark ChatGPT setup as confirmed

## 1.1.0 - 2026-10-03

- add `skills/pmo-setup/SKILL.md` as the canonical AI-driven Google Drive setup procedure
- require a user-specified or explicitly approved Drive destination before setup writes
- standardize the PMO root name and examples on `PMO`
- reduce ChatGPT/Claude persistent instructions to a thin `START_HERE.md` bootstrap
- make `START_HERE.md` the canonical runtime entrypoint for each new chat/session
- switch default memory behavior to explicit-first suggestions (`memory.auto_save: false`)
- disable Daily logging by default until the user enables it
- align adapters and protocols with the new setup/runtime boundary
- add contract tests for setup approval, safe defaults, runtime bootstrap and repository naming

## 1.0.0 - 2026-10-02

Initial complete architecture:
- portable Markdown memory-event and correction schemas
- automatic Memory Check protocol
- per-chat Daily/session protocol
- correction-first generated guardrails
- System / Config / Data / Runtime ownership model
- private-vault installer and manifest-driven updater
- config/data migration framework
- system drift detection
- automatic backups before update
- generated MEMORY / NOW / GUARDRAILS / INDEX views
- provider-neutral turn ingestion
- local SQLite FTS5 search index
- doctor, backup, duplicate detection and rebuild commands
- language / locale / timezone configuration
- ChatGPT, Claude and generic adapter guidance
