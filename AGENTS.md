# Repository instructions

Personal Memory OS is a privacy-preserving OSS system. Never add real user memory, credentials, exported conversations, Drive IDs, account identifiers, or private vault content to this repository.

## Architectural invariants
- Markdown is the canonical portable data format.
- System, Config, Data and Runtime ownership boundaries must remain explicit.
- System updates must never overwrite canonical Data.
- User corrections outrank ordinary memory.
- Generated views are disposable and rebuildable.
- Runtime DB/index/cache files must stay outside synchronized vaults.
- AI-provider-specific integrations must map to the provider-neutral PMO protocol instead of changing the canonical schema.
- `skills/pmo-setup/SKILL.md` is the canonical AI-driven install procedure; `START_HERE.md` is the canonical runtime entrypoint.
- AI-driven setup must obtain a user-specified or explicitly approved Drive destination before the first write.
- The standard PMO root folder name in code, docs and examples is `PMO`; do not introduce alternate root naming.
- Updates fail closed on system drift unless the operator explicitly overrides.

Run tests and lint before proposing changes.
