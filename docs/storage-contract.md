# Storage contract

## System-owned

`START_HERE.md` and `_system/**` are deployment-owned. Manual edits are detected as drift. User customizations belong in `_config/custom_rules.md`.

## User-owned

`_config/**` and all Data directories are user-owned. The updater may migrate schema with backup, but must not blanket-replace them.

## Generated

`SYSTEM_VERSION.md`, `MEMORY.md`, `NOW.md`, `GUARDRAILS.md`, `INDEX.md` and daily `SUMMARY.md` are machine-generated artifacts.

## Runtime

The local FTS database and lock files live under `~/.personal-memory-os/<vault-id>/`. They can be removed without data loss.
