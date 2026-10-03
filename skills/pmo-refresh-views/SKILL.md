---
name: pmo-refresh-views
description: Rebuild Personal Memory OS (PMO) generated views from canonical memory and correction records without modifying canonical data. Use when MEMORY.md, NOW.md, GUARDRAILS.md, or INDEX.md may be stale after external or cloud writes, or when the user asks to refresh, rebuild, regenerate, or verify PMO views.
---

# PMO Refresh Views Skill

Refresh PMO generated views from canonical records. Canonical Data is the source of truth; generated views are disposable projections.

## Scope

This skill refreshes only:

- `MEMORY.md`
- `NOW.md`
- `GUARDRAILS.md`
- `INDEX.md`

It must not create, edit, archive, delete, or reinterpret canonical records merely to make a view look cleaner.

## Non-negotiable rules

1. Read the active PMO `START_HERE.md` first and follow its current Config, protocols, and write boundary.
2. Treat `10_Memory/Events/` and `10_Memory/Corrections/` as canonical for memory and corrections.
3. Generated views are never canonical and must not be used to repair canonical records.
4. Validate all canonical records needed for the refresh before replacing any existing view. If a required record is malformed or unreadable, fail closed and leave the current views unchanged.
5. Resolve `supersedes` historically: a superseded predecessor does not become active again just because its replacement is later archived.
6. Apply `memory.inferred_memory_min_confidence` from `_config/settings.yaml`. Explicit memory is not filtered by this threshold.
7. Apply `views.now_window_days` from Config when generating `NOW.md`.
8. Read the Correction and Generated View protocols before connector-driven regeneration.
9. Never modify `_system/**` or `_config/**` while refreshing views.
10. After writing views, read them back and verify that the rendered references/counts are consistent with the validated active canonical set.
11. Report view-refresh success separately from canonical-data status and local search-index status.
12. Do not claim the local FTS/search index was refreshed unless a local `pmo rebuild` actually ran.

## Preferred execution path

If a local PMO vault and the installed PMO CLI are available, prefer the deterministic implementation:

```bash
pmo rebuild /path/to/PMO
```

This rebuilds the generated views and local search index using the repository implementation.

After it completes, verify the four generated view files exist and report the result.

## Connector-driven path

Use this path when the assistant can access the PMO through Google Drive or another file connector but cannot run the local CLI.

### 1. Establish the exact PMO root

Use the PMO root that contains the `START_HERE.md` already supplied or resolved for the session. Do not search unrelated user storage for another PMO when the active root is known.

Read:

1. `START_HERE.md`
2. `_config/settings.yaml`
3. `_system/protocols/VIEW_PROTOCOL.md`
4. `_system/protocols/CORRECTION_PROTOCOL.md`

Read additional protocols or schemas when validation requires them.

### 2. Enumerate canonical records completely

List all files in:

- `10_Memory/Events/`
- `10_Memory/Corrections/`

Follow pagination until complete. Do not infer completeness from a partial page.

Read every canonical record needed for the refresh.

Validate memory records against `pmo.memory-event/v1` requirements and correction records against `pmo.correction/v1`. At minimum, ensure required frontmatter fields exist, status values are usable, and referenced `supersedes` values can be processed.

If validation fails, stop before replacing any generated view and report the malformed or unreadable records.

### 3. Resolve the active sets

For memory records, apply the confidence filter **before** resolving supersession:

1. keep explicit records, and inferred records only when confidence is at least `memory.inferred_memory_min_confidence`;
2. from that eligible set, collect all IDs referenced by `supersedes`;
3. exclude any eligible record whose ID is superseded;
4. from the remaining records, include only `status: active`.

An inferred record below the threshold must not hide the record it claims to supersede. Label included inferred memory with its confidence.

For corrections, apply steps 2–4 to all correction records (no confidence filter).

Corrections outrank ordinary memory and are rendered into `GUARDRAILS.md`.

### 4. Render the four views

Match the semantics of the current PMO implementation:

- `GUARDRAILS.md`: active corrections, strongest priority first, including correction body, priority, repeat count, and source reference.
- `MEMORY.md`: eligible active memory grouped by memory `type`, with topic/inference labels and source references.
- `NOW.md`: eligible active records of type `project_progress`, `open_loop`, `current_focus`, or `decision` whose `created_at` falls within `views.now_window_days`; newest first.
- `INDEX.md`: core navigation plus counts from canonical memory records and corrections.

Do not summarize away a canonical record so aggressively that the view can no longer identify its source. Preserve a stable source reference or canonical ID/link for each rendered memory item when the connector representation permits it.

### 5. Replace views safely

Prepare all four outputs before replacing any of them when possible.

Replace only the four generated root views. Preserve canonical Data, Config, System, and version metadata.

If the connector cannot update a raw Markdown file in place but can safely recreate generated views, deletion/recreation is allowed because these files are explicitly disposable. Confirm the replacement exists before considering that view refreshed.

### 6. Read back and verify

After writing, read back all four views.

Verify at minimum:

- every eligible active memory record is represented exactly once in `MEMORY.md`;
- every active correction is represented in `GUARDRAILS.md`;
- `NOW.md` respects the configured window and allowed types;
- `INDEX.md` counts match the canonical records used for this refresh;
- no canonical file was changed by the refresh.

When exact source-reference counting is impossible with a connector, state the weaker verification that was actually performed rather than claiming exact coverage.

## Completion report

Return a compact report containing:

- canonical memory records scanned;
- eligible active memory records rendered;
- correction records scanned;
- active corrections rendered;
- malformed/unreadable records;
- refreshed view names;
- readback verification result;
- local search-index status (`refreshed`, `not refreshed`, or `not applicable`).

Only say the refresh is complete when the four generated views were written and read back successfully.
