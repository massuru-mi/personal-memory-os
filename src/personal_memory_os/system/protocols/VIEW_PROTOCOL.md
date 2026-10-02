# Generated View Protocol v1

`MEMORY.md`, `NOW.md`, `GUARDRAILS.md`, and `INDEX.md` are derived views optimized for AI context loading and human navigation.

They are not canonical. Any generated view may be deleted and rebuilt from canonical files under `10_Memory/` and other Data directories.

- `GUARDRAILS.md`: active corrections, strongest first.
- `MEMORY.md`: active durable memory, grouped by type.
- `NOW.md`: recent current-focus, progress, decisions and open loops.
- `INDEX.md`: navigation and counts.

Assistants must resolve conflicts in favor of canonical data and user corrections, not stale generated text.

For each record kind, resolve `supersedes` before rendering the active set. Preserve the
original files. An archived replacement does not revive a superseded predecessor.
For memory views, first exclude inferred records below
`memory.inferred_memory_min_confidence` (default `0.8`); rejected inferences cannot
hide explicit memory. Both MEMORY and NOW use this rule and label accepted inferences
with their confidence. Validate canonical records before replacing a view; do not
silently skip malformed records or claim an incomplete view is current.
