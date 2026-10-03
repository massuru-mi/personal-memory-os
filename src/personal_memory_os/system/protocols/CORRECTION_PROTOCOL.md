# Correction Protocol v1

User corrections are first-class memory and outrank ordinary memory.

A correction exists when the user says or clearly implies that an AI's prior assumption, interpretation, preference, fact or implementation direction was wrong, outdated or inconsistent with the user's intent.

Store each correction as an append-only file under `10_Memory/Corrections/` using schema `pmo.correction/v1`. Start from `_system/templates/correction.md`.

Frontmatter fields:
- `schema`, `id`, `type: correction`, `created_at`, `source`, `status`
- `priority`: normally `critical` for direct user corrections
- `topic`
- `repeat_error_count`
- `supersedes` when replacing an older correction

Body sections (required; never put these in frontmatter):

```markdown
## Wrong assumption
The incorrect assumption in concise terms.

## Correct understanding
The corrected understanding.
```

Optional body section:

```markdown
## Trigger
The situation in which this correction should be applied, e.g. "when advising on Claude Code features for this user".
```

Add `## Trigger` when the user's correction makes the situation clear; it helps future assistants recall the correction at the right time. Do not invent a broader trigger than the correction supports. If present, it must not be empty.

Additional body sections, such as guidance for future answers, may follow these.

Do not manufacture a “wrong” statement the user never corrected. Do not generalize a narrow correction beyond its supported scope.

When the same class of error repeats, increment the repeat count in a new superseding correction or create a stronger guardrail event. Generated `GUARDRAILS.md` is always consulted before ordinary memory.
