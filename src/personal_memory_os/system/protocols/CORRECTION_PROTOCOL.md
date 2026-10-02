# Correction Protocol v1

User corrections are first-class memory and outrank ordinary memory.

A correction exists when the user says or clearly implies that an AI's prior assumption, interpretation, preference, fact or implementation direction was wrong, outdated or inconsistent with the user's intent.

Store each correction as an append-only file under `10_Memory/Corrections/` with:
- `wrong`: the incorrect assumption in concise terms
- `correct`: the corrected understanding
- `priority`: normally `critical` for direct user corrections
- `topic`
- `repeat_error_count`
- `supersedes` when replacing an older correction

Do not manufacture a “wrong” statement the user never corrected. Do not generalize a narrow correction beyond its supported scope.

When the same class of error repeats, increment the repeat count in a new superseding correction or create a stronger guardrail event. Generated `GUARDRAILS.md` is always consulted before ordinary memory.
