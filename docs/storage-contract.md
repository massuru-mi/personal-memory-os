# Storage contract

## System-owned

`START_HERE.md`, `AGENTS.md`, `CLAUDE.md` and `_system/**` are deployment-owned. Manual edits are detected as drift. A pre-existing user `AGENTS.md` or `CLAUDE.md` is never overwritten; install/update leaves it in place and reports it under `skipped_existing`. User customizations belong in `_config/custom_rules.md`, which install creates once and updates never overwrite.

## User-owned

`_config/**` and all Data directories are user-owned. The updater may migrate schema with backup, but must not blanket-replace them.

Canonical memory lives in `10_Memory/Events/` (one file per memory event; preferences, facts, decisions and other kinds are distinguished by `type`) and `10_Memory/Corrections/`. Install no longer creates `10_Memory/Self`, `10_Memory/Preferences` or `10_Memory/Decisions`: nothing reads or writes them. Existing vaults may still contain these folders; they are user Data and are left in place, never deleted by PMO.

Install also no longer creates `00_Inbox`, `20_Projects`, `30_Knowledge` or `40_Decisions`. Projects, knowledge and decisions are recorded as memory events (`type: project_progress`, `knowledge`, `decision`) and grouped by `scope`. Memory save proposals are made in the conversation and saved as events only when approved; there is no candidate queue. If these folders already exist, they remain user Data: still protected from updates and never deleted by PMO.

## Generated

`SYSTEM_VERSION.md`, `MEMORY.md`, `NOW.md`, `GUARDRAILS.md`, `INDEX.md` and daily `SUMMARY.md` are machine-generated artifacts.

## Runtime

The local FTS database and lock files live under `~/.personal-memory-os/<vault-id>/`. They can be removed without data loss.
