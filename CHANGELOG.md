# Changelog

## Unreleased

- add canonical file-format rules to `START_HERE.md`: start from `_system/templates/`, UTF-8 without BOM, LF line endings, read back before reporting saved
- clarify in the Correction Protocol that `Wrong assumption` / `Correct understanding` are required body sections, not frontmatter fields
- point the Memory and Daily protocols at their templates

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
