---
name: pmo-remember
description: Save a Personal Memory OS (PMO) memory event or user correction correctly — choose memory vs correction vs superseding record, write it through the pmo CLI when available or in the exact template format otherwise, and read it back. Use when the user asks to remember, save, note, correct, or update something in PMO, or when a save the user accepted must be written.
---

# PMO Remember Skill

Write one canonical PMO record per thing to remember. Records are append-only Markdown files; this skill makes sure they are valid on the first write.

## Non-negotiable rules

1. Read the active PMO `START_HERE.md` first and follow its Config, protocols and write boundary.
2. Save only what the user asked for, or what `memory.auto_save` and the Memory Protocol allow. Silence is not consent. If saving is not allowed, propose the save instead.
3. Do not record AI inference as a user fact. Use `explicitness: inferred` with an honest `confidence` only when an inferred record is intentionally created.
4. Never edit or delete an existing canonical record to change what it says. Append a new record that `supersedes` it.
5. Never write `_system/**`, `START_HERE.md`, `AGENTS.md`, `CLAUDE.md` or generated views (`MEMORY.md`, `NOW.md`, `GUARDRAILS.md`, `INDEX.md`).
6. Do not report a record as saved until it has been written and read back.

## 1. Decide what to write

| The user… | Write |
|---|---|
| says an earlier AI assumption, fact or direction was wrong | a **correction** (`10_Memory/Corrections/`) |
| changes a fact, preference or decision that is already recorded | a **memory event** with `supersedes: [<old id>]` |
| shares something new to keep | a **memory event** (`10_Memory/Events/`) |

Memory `type` is one of: `fact`, `preference`, `decision`, `project_progress`, `open_loop`, `current_focus`, `interest`, `relationship`, `knowledge`. Preferences and working style are `preference` events; there is no separate preferences folder.

Choose a `scope` for every record:

- `["global"]` only for how to behave in every conversation (language, tone, honesty) and core facts about the user;
- otherwise the best matching category path, reusing an existing one (Categories in `INDEX.md`, or `categories` from the MCP bootstrap); create a new path such as `digital/video-editing` when none fits; use the broader parent when unsure; several categories are allowed.

Narrow one-off corrections (one product, one appointment) belong in a category, not in global.

For a correction, write `wrong` and `correct` in the user's terms. Add a `trigger` (the situation in which the correction applies) only when the user's correction makes it clear; do not invent a broader one. Use `priority: critical` for direct user corrections. Follow `_system/protocols/CORRECTION_PROTOCOL.md` for repeated errors.

## 2. Preferred path: PMO MCP tools or the pmo CLI

If the PMO MCP tools are available, use `pmo_record_memory` / `pmo_record_correction` (they take the same fields, including `scope`, `supersedes` and `status`).

Otherwise, with the CLI:

Use this when a shell with the installed `pmo` CLI and the PMO folder is available.

```bash
pmo record /path/to/PMO --type preference --content "Prefers concise answers in Japanese" --topic communication --scope global
pmo correct /path/to/PMO --wrong "..." --correct "..." --topic claude-code --trigger "When advising on Claude Code features" --scope digital/claude-code
```

Other `pmo record` options: `--importance` (0–1), `--explicitness inferred --confidence <0–1>`, `--source <assistant name>`.

`pmo record` cannot set `supersedes`. To supersede, submit the turn contract instead:

```bash
pmo ingest-turn /path/to/PMO - <<'JSON'
{"source": "claude-code", "memory_events": [
  {"type": "preference", "content": "...", "supersedes": ["<old id>"]}
]}
JSON
```

The CLI validates the record, writes it atomically and refreshes the generated views. Run `pmo rebuild /path/to/PMO` before searching for the new record.

## 3. Connector path: write the file yourself

Use this only when the CLI is unavailable (for example a cloud assistant writing through Google Drive).

1. Read the template: `_system/templates/memory-event.md` or `_system/templates/correction.md`.
2. Build the ID: `mem-YYYYMMDDTHHMMSS-<8 lowercase hex>` or `correction-YYYYMMDDTHHMMSS-<8 lowercase hex>`, using the vault timezone from `_config/settings.yaml`. The file name is the ID in lowercase plus `.md` (the CLI does the same).
3. Fill every frontmatter field the template shows, including `scope`. `created_at` must include a timezone offset. Do not add fields the template and protocol do not define.
4. Body:
   - memory event: the memory content after the closing `---`;
   - correction: `## Wrong assumption`, `## Correct understanding`, and optionally `## Trigger`, each with non-empty text. Never put these in frontmatter.
5. Save as UTF-8 without a BOM, with LF line endings, as an ordinary file (not a converted Google Doc). The first line must be exactly `---`.
6. Read the file back and check the format above. If it is wrong, fix the file you just created before reporting.
7. Refresh the generated views with `_system/skills/pmo-refresh-views/SKILL.md` when possible; otherwise say the views are stale.

## 4. Report

Tell the user, in their language:

- what was saved and as which kind (memory type or correction);
- the record ID and path;
- whether the views were refreshed;
- anything that could not be completed.
