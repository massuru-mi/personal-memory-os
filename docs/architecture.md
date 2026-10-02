# Architecture

Personal Memory OS separates portable personal memory from any AI provider.

## Trust and ownership model

- **System**: released OSS policy, protocol, schema and templates. Deployed read-only for AI.
- **Config**: private user overrides. Preserved across system updates.
- **Data**: private canonical memory and activity records. Never owned by updater.
- **Runtime**: disposable local indexes, locks and caches outside the synchronized vault.

## Canonical vs derived

Canonical data is small, append-oriented Markdown. `MEMORY.md`, `NOW.md`, `GUARDRAILS.md`, daily `SUMMARY.md`, and `INDEX.md` are views. They can be deleted and rebuilt.

## Concurrency model

Cloud-connected assistants should avoid shared mutable hot files. Each memory item is a new file; each chat has its own Daily file. The local maintenance layer may atomically regenerate views. This minimizes Drive synchronization conflicts and retains provenance.

## Retrieval order

Correction/guardrail context comes first, then durable memory, then current context. Deeper project and knowledge data is read only when necessary. This reduces irrelevant context while preserving the strongest user constraints.

## Update model

A release is deployed into the vault; the Git repository is not the vault. Manifest hashes detect manual system drift. Backup and schema migrations precede system replacement. Protected Data paths are never update targets.
