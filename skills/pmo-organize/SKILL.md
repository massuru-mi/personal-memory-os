---
name: pmo-organize
description: Organize a Personal Memory OS (PMO) vault on request — find duplicates, contradictions, stale open loops and weak inferences, propose concrete changes, and apply only the accepted ones as new append-only records that supersede or retire old ones. Use when the user asks to organize, clean up, review, deduplicate or tidy their PMO memory.
---

# PMO Organize Skill

Help the user keep their memory accurate and small. Organizing never edits or deletes existing records: every accepted change is a new record that supersedes the old ones.

## Non-negotiable rules

1. Read the active PMO `START_HERE.md` first, then `GUARDRAILS.md`, `MEMORY.md` and `NOW.md`.
2. Propose first. Apply only the changes the user accepts, item by item or as an explicitly accepted batch.
3. Never edit, delete or rename an existing canonical record to change what it says. Use `supersedes`. The only in-place change is a record's `scope` (classification), made with `pmo set-scope` / `pmo_set_scope`.
4. Never turn an inference into a user fact, and never resolve a contradiction by guessing which record is right. Ask.
5. User corrections outrank ordinary memory. Do not retire or weaken an active correction unless the user explicitly says it no longer applies.
6. Never write `_system/**` or generated views directly.

## 1. Collect candidates

With the CLI:

```bash
pmo rebuild /path/to/PMO
pmo --json duplicates /path/to/PMO
```

Then read the active records (`10_Memory/Events/`, `10_Memory/Corrections/`) and look for:

| Candidate | What to look for |
|---|---|
| Exact duplicates | groups reported by `pmo duplicates` |
| Near duplicates | records that say the same thing in different words |
| Contradictions | active records on the same topic that cannot both be true |
| Stale items | `open_loop` or `current_focus` older than `views.now_window_days` that may be done or no longer relevant |
| Weak inferences | `explicitness: inferred` records, especially low `confidence` |
| Missing triggers | corrections whose situation is clear from the text but that have no `## Trigger` |
| Unscoped or mis-scoped records | records without `scope` (treated as global), and global records that only matter in one subject — propose a category |
| Categories to split | a category with many records, or many recent records in one sub-area (see Categories in `INDEX.md`, "recent" counts) — propose a sub-category, e.g. `digital` → `digital/video-editing` |
| Categories to merge or rename | tiny categories, near-duplicate names (`health` / `daily-life/health`) |

Without the CLI, list and read the same folders through the connector and look for the same candidates.

## 2. Propose

Show a short numbered list in the user's language. For each item give the records involved (IDs), the problem, and the concrete proposed change, for example:

1. Merge `mem-…a` and `mem-…b` into one preference "…".
2. `open_loop` "…" (2026-08-01) — done? If so, retire it.
3. `mem-…c` and `mem-…d` contradict on "…" — which is current?

Wait for the user's answer.

## 3. Apply accepted changes

Write each change with `_system/skills/pmo-remember/SKILL.md`:

| Change | New record |
|---|---|
| Merge duplicates | one memory event with the merged content, `supersedes: [all merged IDs]` |
| Resolve a contradiction | one memory event with the user's answer, `supersedes: [the outdated IDs]` |
| Retire an item (done, no longer true) | one memory event with `status: archived`, the same `type`, content stating what is retired and why, `supersedes: [the retired ID]` — it hides itself and the old record from the views |
| Confirm an inference | one explicit memory event with the user's wording, `supersedes: [the inferred ID]` |
| Add a missing trigger | one new correction with the same wrong/correct text plus `## Trigger`, `supersedes: [the old correction ID]` |
| Set or change a scope (classify, split, merge, rename a category) | no new record: change the scope in place with `pmo set-scope <vault> <id>… --scope <new>` or `pmo_set_scope` (only the `scope` line changes) |

With the CLI, submit records that need `supersedes` or `status` through `pmo ingest-turn` (see the pmo-remember skill). Back up with `pmo backup` before a large reclassification. Then run `pmo rebuild`.

## 4. Report

Tell the user what was changed (new record IDs and what they supersede), what was left as is, and whether the views were refreshed.
