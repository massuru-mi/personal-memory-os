---
name: pmo-doctor-repair
description: Diagnose a Personal Memory OS (PMO) vault with pmo doctor and apply only content-preserving repairs to malformed canonical records (encoding, line endings, correction sections in the wrong place), after taking a backup. Use when pmo doctor fails, when PMO records cannot be parsed or are missing from generated views, or when the user asks to check or repair PMO.
---

# PMO Doctor & Repair Skill

Find and fix records that PMO cannot read, without changing what any record means. Typical cause: an assistant wrote a record by hand in a slightly wrong format.

## Non-negotiable rules

1. Read the active PMO `START_HERE.md` first.
2. Back up before changing anything.
3. Only make **content-preserving** repairs (listed below). Never reword, summarize, merge, delete or re-date a record, and never invent a value the file does not already contain.
4. Anything outside the allowed repairs is reported to the user with a proposed fix and waits for explicit approval.
5. Never edit `_system/**`, `START_HERE.md`, `AGENTS.md` or `CLAUDE.md` to make a check pass. Do not run `pmo update --force-system-drift` without the user's explicit approval for that action.
6. Re-run the checks after repairing and report what changed.

## Allowed content-preserving repairs

| Problem | Repair |
|---|---|
| UTF-8 BOM, CRLF or CR line endings | Re-save as UTF-8 without BOM with LF line endings. Text unchanged. |
| Correction has `wrong` / `correct` as frontmatter keys | Remove those keys and put their text, verbatim, under `## Wrong assumption` / `## Correct understanding` in the body. Keep any existing body text after them under its own heading (for example `## Guidance`). |
| Correction body uses `wrong:` / `correct:` lines instead of headings | Move the text after each label, verbatim, under the matching heading. |
| Correction file lacks the constant fields `schema: pmo.correction/v1` or `type: correction` | Add the constant value. |
| Memory event file lacks `schema: pmo.memory-event/v1` | Add the constant value. |

Not allowed without approval: filling `status`, `created_at`, `id`, `importance`, `confidence`, `explicitness`, `priority` or any other value that requires judgment; renaming files; resolving duplicates; changing `supersedes`.

## Preferred path: the pmo CLI

```bash
pmo backup /path/to/PMO
pmo --json doctor /path/to/PMO
```

1. Read every failing check. `memory_parse` lists the unreadable records; `system_drift` lists modified or missing System files.
2. `pmo doctor` may stop at the first error per file. After fixing, run it again until it passes or only non-allowed problems remain.
3. Repair each listed record using the table above. Read the whole file first; preserve every character of the user's content.
4. Run `pmo --json doctor /path/to/PMO` again, then `pmo rebuild /path/to/PMO`.

For `system_drift`: report which System files changed. If the user had customized them, suggest moving the customization to `_config/custom_rules.md`; restoring with `pmo update --force-system-drift` needs explicit approval.

## Connector path

Use this when the CLI is unavailable.

1. Make sure a prior version can be recovered: rely on the storage provider's version history if it exists, otherwise copy each file you will change into `80_Archive/repair-backups/YYYY-MM-DD/` before editing it.
2. List `10_Memory/Events/` and `10_Memory/Corrections/` completely and read each record.
3. Check each record against `_system/schemas/` and the templates in `_system/templates/`, and apply only the allowed repairs.
4. Read each repaired file back.
5. Refresh the views with `_system/skills/pmo-refresh-views/SKILL.md`.

## Report

Tell the user, in their language:

- where the backup is;
- each repaired file and what was changed (for example "moved wrong/correct into body headings");
- each problem left for the user, with a proposed fix;
- the final doctor result and whether the views were refreshed.
