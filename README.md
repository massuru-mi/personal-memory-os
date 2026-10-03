[日本語](README.ja.md) | English

# Personal Memory OS (PMO)

**Your own memory, usable from any AI such as ChatGPT or Claude, kept in your own Google Drive.**

Preferences, decisions and corrections you teach an AI usually stay inside that one AI. When you switch to another assistant, you explain the same things again.

PMO **stores that memory as Markdown files in your own Drive**. What ChatGPT learned, Claude can use too. Change assistants, and your memory stays with you.

## Where it works

Results the author verified on real devices (as of 2026-10-03).

| Device | App | Mode | Setup | Read/write | MCP |
|---|---|---|:---:|:---:|:---:|
| iPhone | ChatGPT | Chat | ✅ | ✅ | ❌ |
| iPhone | Claude | Chat | ❌ | ✅ | ❌ |
| Mac | ChatGPT | Chat | — | ✅ | ❌ |
| Mac | ChatGPT | Work | — | ✅ | ✅ |
| Mac | Claude | Chat | — | ✅ | ❌ |
| Mac | Claude | Cowork | — | ✅ | ❌ |
| Mac | Claude Code | Desktop app | ✅ | ✅ | ✅ |
| Mac | Codex | — | ✅ | ✅ | ✅ |

✅ verified　❌ does not work　— not tried yet

- **Setup**: can create PMO in Google Drive by following [`pmo-setup`](skills/pmo-setup/SKILL.md)
- **Read/write**: can read PMO in Drive and add memories to it
- **MCP**: can use PMO tools from a session in any folder by registering `pmo mcp` ([details](#use-from-any-folder-mcp))

On a computer, Claude Code or Codex is recommended because they support MCP. Gemini and other assistants not listed have not been verified.

## Getting started

No installation is needed. Ask an AI and it sets up PMO in your Drive. Use an app marked "Setup ✅" in the table above.

### 1. Prepare

Connect Google Drive in the assistant so it can create, read and write files.

### 2. Send this one line to the assistant

```text
Read https://github.com/massuru-mi/personal-memory-os/blob/main/skills/pmo-setup/SKILL.md and follow it to set up PMO in "My Drive/PMO" in my Google Drive.
```

**Setup can take five minutes or more.** If the reply stops part-way, send "continue". The assistant checks what already exists and resumes without creating anything twice.

To use another destination, change `My Drive/PMO`. If you leave the destination out, the assistant asks you to approve `My Drive/PMO` before it writes anything.

Following the setup skill ([`skills/pmo-setup/SKILL.md`](skills/pmo-setup/SKILL.md)), the assistant:

- creates the folders and files
- reads back what it created to verify it
- gives you the verified link to `START_HERE.md`
- writes the text to paste into your custom instructions

If the folder already contains PMO, nothing is duplicated; only missing items are added. Existing files are never deleted or overwritten.

### 3. Set the entry point in each assistant

Setup happens once. After that, tell each assistant you want to use with PMO to "read `START_HERE.md` first".

| App | Where to set it |
|---|---|
| ChatGPT | Paste the text the assistant wrote into custom instructions |
| Claude | Paste the text the assistant wrote into your profile |
| Claude Code / Codex | [Register the MCP server](#use-from-any-folder-mcp) |

The detailed rules live in `START_HERE.md` and the rule documents under `_system/` in your Drive. When PMO is updated, the new rules apply without re-pasting the instruction.

## Everyday use

Just talk to the assistant as usual.

| What you want | Example |
|---|---|
| Have it remember | "Remember that I prefer concise answers" |
| Correct it | "That's wrong. Actually, … Remember that" |
| Correct it for a situation | "When you explain Claude Code features, first check whether my plan includes them" |
| Organize | "Organize my memory" |
| Check for problems | "Check my PMO" |
| Refresh the lists | "Update the lists" |

- **By default, only what you ask for is saved.** Anything else is only suggested ("Shall I save this?"). Automatic saving and daily records can be enabled in settings.
- **Corrections outrank ordinary memory**, so the assistant does not repeat a mistake you already corrected.
- **AI inferences are kept separate from facts.**
- **Organizing starts with a proposal.** Duplicates, contradictions and finished items are listed, and only what you accept is applied. Original records are not deleted; new records replace them.

The assistant handles these requests by following the skills in `_system/skills/` in your Drive.

### Import past chats

Chats from before PMO can be imported one at a time. Open a past chat and send a fixed prompt; the assistant keeps only what is worth reusing and saves it with a scope. See [Import past chats](docs/import-past-chats.md) for the prompt and steps.

## View it in Obsidian

The PMO folder in your Drive can be opened as an Obsidian vault as is. Sync it with Google Drive for desktop, then choose "Open folder as vault" in Obsidian.

You can browse what the assistants saved through the lists (`MEMORY.md`, `NOW.md`, `GUARDRAILS.md`) and links, and read it yourself. To add or change memories, ask an assistant or use the `pmo` command instead of editing files directly. That keeps the format intact and preserves the replacement history.

## What works and what does not yet

**Works**

- Saving memories and corrections ([`pmo-remember`](skills/pmo-remember/SKILL.md)); corrections can carry a trigger (the situation in which they apply)
- Splitting memories and corrections into `global` (needed in every conversation) and categories; categories emerge from records. Over MCP only global items load each time; category items load when the topic matches
- Replacing old memories with new ones; replaced memories drop out of the lists
- Separating inferences from what you said explicitly; inferences appear in the lists only above the confidence threshold and are labeled as inferred
- Organizing memory ([`pmo-organize`](skills/pmo-organize/SKILL.md)), diagnosis and repair ([`pmo-doctor-repair`](skills/pmo-doctor-repair/SKILL.md)), and PMO system updates ([`pmo-update`](skills/pmo-update/SKILL.md))
- Rebuilding the lists (MEMORY, NOW, GUARDRAILS, INDEX) with [`pmo-refresh-views`](skills/pmo-refresh-views/SKILL.md) or `pmo rebuild`
- Search, duplicate detection, backups, session logs and daily summaries through the local command (session logs are off by default)

**Not yet**

- Automatic memory across all assistants, or background processing
- Refreshing the lists and search index automatically after new memories are written. Ask an assistant to "update the lists" or run `pmo rebuild` when needed (no scheduled job is required)

## What is in your Drive

| Layer | Contents | Ownership |
|---|---|---|
| System (`_system/`, `START_HERE.md`, `AGENTS.md`, `CLAUDE.md`) | Rules, formats, templates, skills | Deployed and updated by PMO; assistants do not change it in ordinary use |
| Config (`_config/`) | Language, saving policy and other settings; your own extra rules | Yours; kept across PMO updates |
| Data (`10_Memory/` etc.) | Memories, corrections, session logs | Yours; never overwritten by PMO updates |
| Runtime | Search index, locks | Disposable local files on your computer, never in Drive |

```text
PMO/
├─ START_HERE.md        # entry point every assistant reads first
├─ AGENTS.md / CLAUDE.md  # entry point for Codex / Claude Code (points to START_HERE)
├─ SYSTEM_VERSION.md
├─ MEMORY.md / NOW.md / GUARDRAILS.md / INDEX.md  # lists rebuilt from records
├─ _system/             # rules, templates, skills
├─ _config/             # your settings (settings.yaml) and extra rules (custom_rules.md)
├─ 10_Memory/
│  ├─ Events/           # memories (one file each; preferences, facts, decisions… by type)
│  └─ Corrections/      # corrections (one file each)
├─ 50_Daily/            # session logs (when enabled)
└─ 80_Archive/
```

| List | Contents |
|---|---|
| `GUARDRAILS.md` | Corrections; assistants read this with top priority |
| `MEMORY.md` | Long-term memories |
| `NOW.md` | Recent interests and work in progress |
| `INDEX.md` | Table of contents |

Session logs are written one file per conversation, such as `50_Daily/YYYY-MM-DD/<provider>_<session-id>_<topic>.md`, to reduce concurrent writes to the same file. This does not eliminate sync conflicts entirely.

## Use on a computer (optional)

Skip this section if you only use PMO from phone or chat apps. It is for using PMO from Claude Code or Codex, or for searching and rebuilding lists on your computer.

On a computer you work with three different folders:

| Folder | Contents | Location | What you do with it |
|---|---|---|---|
| Repository (`personal-memory-os`) | The PMO machinery (command and distribution files) | Anywhere on your computer | Only for `pip install` and PMO updates. **Its contents are public on GitHub, so never put memories here** |
| PMO folder (`My Drive/PMO`) | Your memories and settings | Google Drive (only you can see it) | Assistants and the `pmo` command read and write it. Open it in Obsidian |
| Your project folders | Your everyday work | Anywhere | Start Claude Code or Codex here; MCP connects them to PMO |

Keep the three in separate places. Do not create the PMO folder inside the repository.

### Use from any folder (MCP)

For Claude Code and Codex, registering the MCP server `pmo mcp` is recommended.

- **Easy on/off**: in a connected session the assistant loads corrections and memories first and records through PMO tools. Disconnect it and no PMO instructions or tools are loaded.
- **On by default if you like**: registered at user scope in Claude Code, it is active in every new session. Disable it per project with `/mcp`.

```bash
claude mcp add --scope user pmo -- pmo mcp --vault "/path/to/PMO"
```

MCP requires installing the command as `personal-memory-os[mcp]` (see [Install the command](#install-the-command)). For registering with Codex and turning it off, see the [MCP guide](docs/mcp.ja.md) (Japanese).

### Install the command

Requires Python 3.11 or later. Get this repository and run the commands from it, separate from your memory folder.

```bash
python -m pip install .
pmo install /path/to/PMO
pmo record /path/to/PMO --type preference --content "Example: prefer concise answers"
pmo rebuild /path/to/PMO
pmo search /path/to/PMO "concise"
pmo doctor /path/to/PMO
```

Replace `/path/to/PMO` with your actual destination. To use PMO in Drive, install Google Drive for desktop so the folder can be read and written as an ordinary folder. If PMO already exists in Drive, skip `pmo install`.

Main commands:

| Command | What it does |
|---|---|
| `pmo record` | Save one memory |
| `pmo correct <vault> --wrong "..." --correct "..." [--trigger "..."]` | Save a correction (`--trigger` adds the situation it applies to) |
| `pmo rebuild` | Rebuild the lists and search index |
| `pmo search` | Search memories |
| `pmo doctor` | Check for broken files and configuration drift |
| `pmo status` | Show the PMO version and whether system files were modified |
| `pmo update` | Deploy the new PMO system into Drive (takes a backup first) |
| `pmo backup` | Back up everything as a zip |
| `pmo duplicates` | Find duplicate memories |
| `pmo set-scope <vault> <id>… --scope <category>` | Change only the scope of existing records |
| `pmo daily <vault> YYYY-MM-DD` | Rebuild a day's summary |
| `pmo ingest-turn <vault> turn.json` | Import memories and session logs prepared by an assistant (including `supersedes` for replacements) |

`ingest-turn` is an entry point for data an assistant has already structured. It does not read conversations or extract memories from them automatically.

## Settings and caveats

**Settings**: `_config/settings.yaml` sets the saving policy (whether to save automatically), whether daily records are on, language and more. The command itself uses the timezone, the confidence threshold for showing inferences, and the NOW window. Language settings are instructions for assistants; command headings are currently English. Some settings, such as automatic archiving, exist but are not implemented yet.

**Updates**: `pmo update` deploys **the PMO installed on your computer** into Drive. It does not download the latest version from GitHub. Upgrade the local package first, and never update with a version older than the one in Drive. A backup is written to `PMO-Backups` beside the vault before updating. If system files were modified by hand, the update stops. See [`pmo-update`](skills/pmo-update/SKILL.md).

**Search**: the search index lives under `~/.personal-memory-os/` on your computer and can always be rebuilt from Markdown. Run `pmo rebuild` before searching newly added memories.

**Known issues**:

- Update protection does not work when the manifest is missing
- Windows needs extra setup for timezone handling
- Retrying a partially failed `ingest-turn` is not fully handled
- Concurrent daily updates are fragile

Protection against conflicts and failed updates is not complete yet. See the [design and acceptance criteria](docs/local-optional-design.ja.md#実装状況と受け入れ条件) (Japanese).

## Why PMO

### Why go beyond Obsidian alone?

Owning knowledge as Markdown and combining Obsidian with AI is a foundation of PMO too. Claude Code and Codex can work with files on your computer directly.

But conversations with AI do not only happen at a desk. ChatGPT on a phone during a commute, Claude while thinking something through, Claude Code or Codex while working. PMO aims to let **mobile, cloud and desktop assistants use the same memory**. Obsidian remains a tool for reading and organizing that memory yourself.

```text
ChatGPT / Claude / Codex / Claude Code / …
                      ↕
            Personal Memory OS
       Shared rules, formats and tools
                      ↕
        Your Markdown files ←→ Obsidian
           Your Drive (private)
```

### Why open source?

Building a memory system to use with AI involves many decisions beyond storage:

- How to organize folders and what to keep long term
- When, if ever, an AI inference should become memory
- How corrections should take precedence over older memory
- How to reduce conflicts when several assistants write at once
- How to summarize daily conversations
- How to handle search and backups, and protect existing memory when the system is updated

No one should have to design this from scratch. **Once someone has solved a piece, the next person should be able to use it as is.** That is why PMO is open source.

GitHub holds only the machinery (rules, formats, templates, update tools). Each person's memory stays private in their own Drive.

## Development and contributions

Do not put your own memories, exported conversations, passwords, API keys or similar in this repository or in issues.

```bash
python -m pip install -e '.[dev]'
pytest
ruff check .
```

- [Architecture](docs/architecture.md) / [Storage contract](docs/storage-contract.md)
- [AI integration](docs/ai-integration.md) / [Memory protocol](docs/memory-protocol.md)
- Skills: [setup](skills/pmo-setup/SKILL.md) / [remember](skills/pmo-remember/SKILL.md) / [organize](skills/pmo-organize/SKILL.md) / [doctor & repair](skills/pmo-doctor-repair/SKILL.md) / [update](skills/pmo-update/SKILL.md) / [view refresh](skills/pmo-refresh-views/SKILL.md)
- [MCP server](docs/mcp.ja.md) (Japanese) / [Cloud workflow](docs/local-optional-design.ja.md) / [Minimal instruction templates](docs/custom-instructions.ja.md) / [Extension design memo](docs/agent-integration-proposals.ja.md) (Japanese)
- [Contributing](CONTRIBUTING.md) / [Security](SECURITY.md)

## License

MIT. See [LICENSE](LICENSE).
