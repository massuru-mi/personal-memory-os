# Personal Memory OS — Start Here

This vault is the user's portable, AI-independent memory layer. The Markdown data in this vault is the source of truth; model-native memory is only supplementary.

## Required read order

Before answering a request that may depend on personal context, read in this order:
1. `GUARDRAILS.md` — user corrections and hard constraints. Highest priority.
2. `MEMORY.md` — durable user facts, preferences and decisions.
3. `NOW.md` — recent focus, progress and open loops.
4. `INDEX.md` — navigate deeper only when needed.
5. Relevant project/knowledge files when the current request needs them.

## Required turn behavior

For every meaningful user turn, perform a Memory Check before finishing the response. Do not wait for the user to say “remember this.” Decide whether the interaction contains durable information, a decision, project progress, a correction, an open loop, or something worth retaining.

If memory-worthy, append a new event under `10_Memory/Events/`. If the user corrects an AI misunderstanding or reverses an earlier assumption, write a correction under `10_Memory/Corrections/` and treat it as higher priority than ordinary memory. AI inference alone must not silently become canonical memory.

Maintain one session log per chat under `50_Daily/YYYY-MM-DD/`. Update it after every meaningful turn with what was done, learned, decided, corrected and left open. Different chats and different AI providers must use different files to avoid sync conflicts.

## Write boundary

- `_system/**`: read-only to AI assistants. Updated only by PMO deployment from the OSS repository.
- `_config/**`: read by AI. Write only when the user explicitly asks to change PMO configuration.
- Data directories (`00_Inbox`, `10_Memory`, `20_Projects`, `30_Knowledge`, `40_Decisions`, `50_Daily`, `80_Archive`): read/write according to protocol.
- `MEMORY.md`, `NOW.md`, `GUARDRAILS.md`, `INDEX.md`: generated views. Never treat them as canonical data.

Read `_system/protocols/` for the normative rules and `_config/settings.yaml` for user-specific settings such as language and timezone.
