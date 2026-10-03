# Personal Memory OS — Start Here

This PMO folder is the user's portable, AI-independent memory layer. Canonical Markdown records in PMO are the source of truth; provider-native memory and chat history are supplementary.

## Session bootstrap

At the beginning of each new chat/session, read this file before relying on PMO context. You do not need to re-read it on every turn unless the PMO rules may have changed.

Then read, in this order when personal context may affect the answer:

1. `_config/settings.yaml` — current user-controlled PMO behavior.
   Also read `_config/custom_rules.md` when present — additional user-owned rules.
2. `GUARDRAILS.md` — active user corrections and hard constraints. Always apply the **Global** section. Apply a category section when the conversation is in that category or one of its sub-categories; several categories can apply at once.
3. `MEMORY.md` — durable memory view. Items labelled with `{category}` matter only in that category.
4. `NOW.md` — recent focus, progress and open loops.
5. `INDEX.md` — navigation, including the user's categories.
6. Relevant canonical records and project/knowledge files when needed.

Generated views are convenient context, not canonical data. When freshness or a conflict matters, inspect the relevant canonical records and latest corrections.

## Memory behavior

Always honor explicit user requests such as “remember this”, “correct that memory”, or “organize my memory”.

For other information:

- If `memory.auto_save` is `false`, do not silently create canonical memory. Offer a concise, concrete save suggestion when future reuse would be valuable.
- If `memory.auto_save` is `true`, save only within the configured policy and the Memory Protocol.
- AI inference alone must not be promoted as a user fact. Keep inference distinct and follow the configured confidence rules.
- User corrections outrank ordinary memory. Follow the Correction Protocol.

Canonical memory events belong under `10_Memory/Events/`; corrections belong under `10_Memory/Corrections/`. Preserve history with `supersedes` rather than rewriting old facts in place.

Give each new memory or correction a `scope` (global or a category) as described in the Memory Protocol. To save a memory or correction, follow `_system/skills/pmo-remember/SKILL.md`. If records cannot be parsed, `pmo doctor` fails, or the user asks to check or repair PMO, follow `_system/skills/pmo-doctor-repair/SKILL.md`.
When the user asks to organize or clean up their memory, follow `_system/skills/pmo-organize/SKILL.md`. To update the PMO System itself, follow `_system/skills/pmo-update/SKILL.md`.

## Daily behavior

Daily/session logging is optional.

- If `daily.enabled` is `false`, do not create or update Daily files.
- If enabled, follow the Daily Protocol and keep one provider/session-specific file per chat.
- PMO does not perform background or scheduled work by itself.

## Generated views

`MEMORY.md`, `NOW.md`, `GUARDRAILS.md`, and `INDEX.md` are generated views. Never make a semantic change only in a generated view.

When the user asks to edit memory represented in a view:

1. update or append the canonical record first;
2. read back the canonical write when the connector supports it;
3. refresh the affected view when possible;
4. report canonical-save success separately from view-refresh success.

When generated views may be stale after canonical writes, or when the user asks to refresh/rebuild/regenerate them, follow `_system/skills/pmo-refresh-views/SKILL.md`. Prefer the local `pmo rebuild` implementation when available; otherwise use the connector-driven procedure in that skill.

## Writing canonical files

Malformed files cannot be parsed and are not reflected in generated views. When creating a memory event, correction or Daily session file:

1. Read the matching template in `_system/templates/` (`memory-event.md`, `correction.md`, `daily-session.md`) and follow its structure exactly. Do not add frontmatter keys the template and protocol do not define.
2. Write UTF-8 without a BOM, with LF line endings. The first line must be exactly `---`.
3. For corrections, put the wrong and correct understanding in the body under `## Wrong assumption` and `## Correct understanding`, not in frontmatter.
4. Read the file back when the connector supports it, and confirm the format before reporting it as saved.

## Write boundary

- `_system/**`: read-only to ordinary AI operation. Updated only by PMO deployment/update.
- `_config/**`: user-owned. Write only when the user explicitly asks to change PMO configuration.
- Data directories (`10_Memory`, `50_Daily`, `80_Archive`): read/write only according to protocol and config. Projects, knowledge and decisions are memory events distinguished by `type` and `scope`, not separate folders. Any other folder in the vault is the user's own and is not read or written by PMO unless the user asks.
- Generated root views: derived, never canonical.

Read `_system/protocols/` for normative details. If required Drive operations are unavailable, state what could and could not be completed; never claim an unread file was read or an unwritten record was saved.
