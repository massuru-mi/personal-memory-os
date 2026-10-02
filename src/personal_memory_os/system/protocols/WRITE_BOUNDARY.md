# Write Boundary v1

## Ownership
- System: GitHub/release owns `_system/**` and `START_HERE.md`.
- Config: user owns `_config/**`.
- Data: user owns all memory, project, knowledge, decision, daily and archive data.
- Runtime: local program owns `~/.personal-memory-os/**`; it is disposable and never canonical.

## AI permissions
AI assistants may read System and Config. They may write Data according to protocol. They must not modify System. Config writes require explicit user intent to change PMO configuration.

## Updater permissions
Updater may replace only manifest-declared System files and generated views. It must never overwrite canonical Data. User Config survives updates and receives only missing default keys via schema-aware merge/migration.

## Drift
If a System-owned deployed file is edited manually, update must fail closed unless the operator explicitly chooses a force update. Custom behavior belongs in `_config/custom_rules.md`, not in `_system/`.
