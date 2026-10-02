# Personal Memory OS

**An open, portable memory layer shared across AI assistants.**

Personal Memory OS (PMO) lets ChatGPT, Claude, Gemini, local agents, Obsidian, and future AI tools share the same user-owned memory without making any model vendor the source of truth.

The public GitHub repository contains only the **system**: protocols, schemas, templates, updater/migration logic, CLI, and tests. A user's real memory lives in a **private Markdown vault** such as a Google Drive folder mirrored to a PC.

```text
ChatGPT / Claude / Gemini / local agents
                 ↕
       private Markdown vault
        (e.g. Google Drive)
                 ↕
      Drive for Desktop / sync
                 ↕
 Obsidian / Codex / Claude Code / PMO CLI
```

## Core principles

1. **User-owned memory** — Markdown is canonical; provider-native memory is optional.
2. **Cross-AI** — every assistant follows the same provider-neutral protocol.
3. **Automatic memory check** — meaningful turns are evaluated for durable memory without requiring “remember this.”
4. **Corrections outrank memory** — user corrections are first-class, high-priority records.
5. **Daily by default** — every chat maintains its own concise daily/session record.
6. **Append-oriented canonical data** — assistants create small event files instead of fighting over one giant memory file.
7. **System / Config / Data separation** — software updates never own the user's private data.
8. **Local-first compatible, cloud-synced friendly** — the same files can be available to mobile AI connectors and local tools.
9. **Rebuildable runtime** — search indexes/caches are local and disposable.
10. **Fail closed on system drift** — updater refuses to overwrite modified system-owned files unless explicitly forced.

## Storage model

| Layer | Source of truth | Typical owner | Update behavior |
|---|---|---|---|
| System | GitHub release | PMO maintainers | replace only manifest-owned files |
| Config | private vault | user | preserve; schema-merge/migrate |
| Data | private vault | user + authorized AI | never overwritten by system update |
| Runtime | local PC | PMO tools | disposable / rebuildable |

A deployed vault looks like:

```text
SecondBrain/
├─ START_HERE.md
├─ SYSTEM_VERSION.md
├─ MEMORY.md                 # generated view
├─ NOW.md                    # generated view
├─ GUARDRAILS.md             # generated view
├─ INDEX.md                  # generated view
├─ _system/                  # GitHub-owned, AI read-only
├─ _config/                  # user-owned configuration
├─ 00_Inbox/
├─ 10_Memory/
│  ├─ Events/
│  └─ Corrections/
├─ 20_Projects/
├─ 30_Knowledge/
├─ 40_Decisions/
├─ 50_Daily/
└─ 80_Archive/
```

## Install

Requires Python 3.11+.

```bash
pip install .
pmo install "G:/My Drive/SecondBrain"
```

For a Google Drive-backed vault, mirror the target folder (or make it available offline) so local tools see ordinary files. PMO itself does not require a Google API credential: cloud synchronization and AI connectors remain independent from the local CLI.

## AI behavior

Every assistant starts at `START_HERE.md`. On every meaningful turn it performs a **Memory Check**. Durable facts, preferences, decisions, progress, and open loops become separate memory events. A direct user correction becomes a Correction event and is consulted before ordinary memory.

Every conversation owns one file under:

```text
50_Daily/YYYY-MM-DD/<provider>_<session-id>_<topic>.md
```

That file is incrementally maintained with:
- what we did
- what we learned
- decisions
- corrections
- open loops

Different chats never share a session file, avoiding cloud-sync conflicts.

## Language and locale

`_config/settings.yaml` controls user-specific language, locale, timezone, output language, memory thresholds and maintenance behavior. System rules only require assistants to honor this config; they do not hard-code Japanese or English.

Example:

```yaml
language:
  primary: ja
  fallback: en
  locale: ja-JP
  timezone: Asia/Tokyo
  output:
    responses: ja
    memory: ja
    daily: ja
    summaries: ja
    tags: en
```

## CLI

```bash
pmo install <vault>
pmo update <vault>
pmo status <vault>
pmo doctor <vault>
pmo rebuild <vault>
pmo record <vault> --type decision --content "..."
pmo correct <vault> --wrong "..." --correct "..."
pmo ingest-turn <vault> turn.json
pmo daily <vault> 2026-10-02
pmo search <vault> "query"
pmo duplicates <vault>
pmo backup <vault>
```

`pmo ingest-turn` is the provider-neutral integration surface for local agents and automations. Mobile assistants may instead write the same documented Markdown schemas through their cloud-storage connectors.

## Update model

The GitHub repository is **not** cloned into the private Drive vault. Treat GitHub as a distribution source and the vault as a running private instance.

`pmo update`:
1. detects system drift,
2. creates a backup by default,
3. runs config/data migrations,
4. merges new config defaults without deleting user settings,
5. replaces only system-manifest-owned files,
6. regenerates derived views,
7. updates `SYSTEM_VERSION.md`.

`SYSTEM_VERSION.md` tracks system, config-schema and data-schema versions independently.

## Runtime search

`pmo rebuild` creates a local SQLite FTS5 index under `~/.personal-memory-os/…`, outside the synchronized vault. The index is never canonical and can always be rebuilt from Markdown.

## Privacy boundary

PMO never requires private user data to be committed to this repository. The OSS repo contains no personal memory. Users should keep their private vault out of Git, and should keep workplace/confidential data in environments permitted by their organization's policies.

## Development

```bash
python -m pip install -e '.[dev]'
pytest
ruff check .
```

Architecture and protocol details are in [`docs/`](docs/).

## License

MIT. See [LICENSE](LICENSE).
