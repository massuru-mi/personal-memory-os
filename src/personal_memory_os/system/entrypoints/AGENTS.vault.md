# Personal Memory OS — agent instructions

This folder is a Personal Memory OS (PMO) vault: the user's AI-independent memory. These instructions apply to any agent working here (Codex, Claude Code, Claudian and others).

1. At the start of each session, read `START_HERE.md` and follow it. It and `_system/protocols/` are the canonical rules; this file only points to them.
2. Write memory and corrections with the `pmo` CLI when it is available, using this folder as the vault path: `pmo record`, `pmo correct`, then `pmo rebuild`. Do not hand-write records the CLI can create. Without the CLI, follow "Writing canonical files" in `START_HERE.md`.
3. Never edit `_system/**`, `START_HERE.md`, `AGENTS.md`, `CLAUDE.md` or generated views (`MEMORY.md`, `NOW.md`, `GUARDRAILS.md`, `INDEX.md`, `SYSTEM_VERSION.md`). Do not rewrite existing canonical records; append a superseding record instead.
4. This file is replaced on PMO updates. User-specific agent rules belong in `_config/custom_rules.md`.
