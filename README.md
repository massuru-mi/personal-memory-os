[日本語](README.ja.md) | English

# Personal Memory OS

**An open Memory OS that puts the memories scattered across AI assistants back in the user's hands.**

We use more AI tools in everyday life: ChatGPT, Claude, Gemini, and others. Yet their conversation histories and memories do not automatically become a shared understanding of us. Context and decisions built up with one assistant often need to be explained again to another.

Important decisions, project progress, and corrections can also get buried in long conversations. We explain the same background again, or an assistant repeats a mistake we already corrected.

Personal Memory OS (PMO) aims to provide **a shared memory layer that the user owns, independent of any AI service**. Its canonical records are Markdown files in private storage, designed to remain portable as the tools we use change.

> PMO is in early development. Markdown protocols and a Python CLI are implemented. Cloud setup from the ChatGPT and Claude apps, and conversational maintenance of cloud views, are design proposals. The vision below is distinct from the [features available today](#available-today-and-in-development).

## Why go beyond Obsidian alone?

Owning knowledge as Markdown and combining Obsidian with AI is a useful foundation. Local agents such as Claude Code and Codex can search, edit, and organize a vault directly.

But everyday conversations with AI also happen away from a computer: ChatGPT on an iPhone during a commute, Claude while thinking through an idea, and Codex or Claude Code while working at a desk.

PMO aims to let **mobile, cloud, and local assistants use the same personal memory**, alongside Obsidian. Obsidian remains an option for reading and organizing that memory yourself.

```text
ChatGPT / Claude / Gemini / Codex / Claude Code
                      ↕
            Personal Memory OS
       Shared protocols, formats and tools
                      ↕
        User-owned Markdown ←→ Obsidian
              Private storage
```

This is the intended architecture, not a claim that integrations with every service shown are implemented.

## Why open source?

Building an AI-assisted second brain involves recurring infrastructure questions:

- How should files be organized, and what belongs in long-term memory?
- When, if ever, should an AI inference become memory?
- How should user corrections take precedence over older information?
- How can concurrent writes from different assistants cause fewer conflicts?
- How should daily conversations be organized?
- How should search, backups, migrations, and system updates preserve existing memory?

Everyone should not have to design this foundation from scratch and solve the same problems again.

**Once someone has solved a piece of second-brain infrastructure, the next person should be able to build on it.** That is one reason PMO is open source.

Each user's actual memory stays in private storage. GitHub shares the machinery: protocols, schemas, templates, deployment tools, and migrations.

```text
GitHub: Personal Memory OS
    │  Shared as open source
    ▼
System / Protocol / Schema / Templates / Tools
    │  Deploy into private storage
    ▼
Your Private Storage
    ├─ Memory
    ├─ Projects
    ├─ Knowledge
    └─ Daily
```

## The experience we are working toward

Ideally, managing memory does not require a special action every time.

You talk to an assistant as usual. Important information is retained according to the saving policy you chose. When you correct the assistant, that correction takes precedence next time. The things you thought about, decided, and worked on can become a concise daily record.

Memory saved through ChatGPT can be used by Claude. Moving to another assistant does not mean starting over. The original records remain Markdown that you own, rather than context accessible only inside one AI service.

**From a world where AI remembers the user, toward one where users own their memory and choose which AI can use it.** PMO aims to be open infrastructure for that transition.

Automatic saving is a user choice. The proposed initial policy is to carry out explicit save/correction requests and suggest other updates during the conversation. Users can authorize automatic saving within a chosen scope and enable daily records.

## Local execution and scheduled jobs are optional goals

The intended cloud workflow does not require users to install Python or desktop synchronization software:

1. Ask **ChatGPT or the Claude app** to read a published setup guide on GitHub.
2. Use that app's Google Drive connection to initialize a private PMO folder.
3. Receive verified storage links and text to paste into the app's instruction settings.
4. Ask it to remember something, correct an old understanding, or organize recent memory.

The setup should provide ChatGPT custom instructions or Claude profile/project instructions. Adding another assistant should connect it to the same vault without recreating the memory. Using the Claude app should not require Claude Code.

A request to edit `MEMORY.md` should update the canonical records and then refresh the view, so a later CLI rebuild does not erase the change. Maintenance should happen on request or through accepted suggestions, without requiring a recurring job.

**This cloud workflow is not implemented or verified end to end.** Each app needs a connection that supports creating, updating, and reading back ordinary files. Pasting instructions does not grant access or create background automation. See the [cloud workflow proposal](docs/local-optional-design.ja.md) and [app instruction drafts](docs/custom-instructions.ja.md), currently in Japanese.

## Available today and in development

| Area | Current status |
|---|---|
| Markdown memory and corrections | CLI and shared schemas implemented |
| Correction and replacement handling | Resolves `supersedes` and excludes old records from current views |
| Explicit information vs. inference | MEMORY and NOW use the configured confidence threshold and label accepted inferences |
| MEMORY / NOW / GUARDRAILS / INDEX | Rebuildable through the CLI |
| Session logs and daily summaries | Turn ingestion and generation of a selected day's summary implemented |
| Local search, duplicate detection, backups | Available through the CLI |
| System updates and migrations | Deployment, drift detection, backups and schema migration foundation implemented; known limitations below |
| Setup from ChatGPT / Claude apps | Design stage; connection, recovery and readback need live verification |
| Cloud memory maintenance, suggestions and view refresh | Workflow design in progress |
| Gemini and other assistants | Future integration targets through the shared protocol; not verified |
| Automatic memory across all assistants or background processing | Not provided; requires integration and an authorized saving policy |

External writes do not currently refresh views or the search index automatically. In the CLI workflow, run `pmo rebuild` when needed. A scheduled job is not required.

## Storage and ownership

| Layer | Contents | Ownership and updates |
|---|---|---|
| System | Shared protocols, schemas, templates | Deployed from a distribution; not changed during ordinary AI memory writes |
| Config | Language, saving and presentation preferences | User-owned; preserved across system updates |
| Data | Memory, corrections, projects, session logs | Private canonical records; not system deployment targets |
| Runtime | Search database, locks | Disposable local files outside the synchronized vault |

```text
SecondBrain/
├─ START_HERE.md
├─ SYSTEM_VERSION.md
├─ MEMORY.md / NOW.md / GUARDRAILS.md / INDEX.md  # rebuildable views
├─ _system/
├─ _config/
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

Session logs use `50_Daily/YYYY-MM-DD/<provider>_<session-id>_<topic>.md` to reduce contention on shared files. This does not eliminate synchronization conflicts; shared views and concurrent writes still need coordination.

## Try the local CLI

Requires Python 3.11+. Obtain a branch or release containing this README and `pyproject.toml`, and run the commands from its source directory, separate from your private vault. To try an unmerged pull request, check out that PR's branch first.

```bash
python -m pip install .
pmo install /path/to/SecondBrain
pmo record /path/to/SecondBrain --type preference --content "Example: prefer concise answers"
pmo rebuild /path/to/SecondBrain
pmo search /path/to/SecondBrain "concise"
pmo doctor /path/to/SecondBrain
```

Replace `/path/to/SecondBrain` with your actual destination. For local CLI use with Drive, mirror the folder so tools can read and write ordinary files. You can also open that private folder in Obsidian.

Other commands:

```bash
pmo correct <vault> --wrong "..." --correct "..."
pmo ingest-turn <vault> turn.json
pmo daily <vault> YYYY-MM-DD
pmo status <vault>
pmo duplicates <vault>
pmo backup <vault>
pmo update <vault>
```

`ingest-turn` accepts structured memory and session records prepared by an agent. It does not automatically connect to a conversation service or extract memory candidates from raw conversation text.

## Configuration, updates and current limitations

`_config/settings.yaml` contains both instructions for assistants and values used by the CLI. The CLI reads the timezone, inferred-memory confidence threshold and NOW window. Language preferences guide assistants; CLI headings are currently English. Some settings, including automatic archiving, describe intended behavior whose implementation is still pending.

`pmo update` **deploys the already installed package into the vault**. It does not download a GitHub release. Upgrade the package from your selected version first, then update the vault. Backups default to `PMO-Backups` beside the vault.

The search database lives under `~/.personal-memory-os/` and can be rebuilt from Markdown. Run `pmo rebuild` before searching newly added records.

Known remaining issues include update protection when the manifest is missing, Windows timezone dependencies, partial turn ingestion and retries, and concurrent Daily updates. This version is not yet a complete solution to concurrency and update failures. See the [design and acceptance criteria](docs/local-optional-design.ja.md#実装状況と受け入れ条件).

## Development and contributions

Keep personal memory in private storage. Do not add real memory, exported conversations, credentials or private vault contents to the public repository or issues.

```bash
python -m pip install -e '.[dev]'
pytest
ruff check .
```

- [Architecture](docs/architecture.md) / [Storage contract](docs/storage-contract.md)
- [AI integration](docs/ai-integration.md) / [Memory protocol](docs/memory-protocol.md)
- [Cloud workflow proposal](docs/local-optional-design.ja.md) / [Instruction drafts](docs/custom-instructions.ja.md)
- [Contributing](CONTRIBUTING.md) / [Security](SECURITY.md)

## License

MIT. See [LICENSE](LICENSE).
