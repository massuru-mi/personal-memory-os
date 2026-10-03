# AI integration

PMO intentionally avoids making one model vendor the orchestrator.

## Cloud/mobile assistants

When a provider can access the user's private cloud folder, the runtime entrypoint is `START_HERE.md`. Detailed memory, correction, Daily and write-boundary rules live there and under `_system/protocols/`; app custom instructions should remain a thin bootstrap pointer.

Each new chat/session reads `START_HERE.md` once before relying on PMO context. If the connector cannot read it, the assistant must not pretend PMO context was loaded.

## App-based setup

The canonical AI setup procedure is [`skills/pmo-setup/SKILL.md`](../skills/pmo-setup/SKILL.md).

ChatGPT, Claude, or another capable assistant may use that skill when it has enough GitHub and Google Drive operations. Before any Drive write, it must either receive a destination from the user or obtain explicit approval for a proposed location. The default proposal is `My Drive/PMO`.

The setup assistant pins the repository version/commit, reproduces the current `pmo install` layout, then lists and reads back the deployed files. It returns verified links and the minimal app instruction from [`custom-instructions.ja.md`](custom-instructions.ja.md).

The skill does not grant connector permissions or create background jobs. Required raw-file creation, update, listing and readback capabilities must be checked at runtime.

## Local agents

Local agents can operate directly on the mirrored PMO folder or submit the provider-neutral JSON turn contract to `pmo ingest-turn`. Agents that load folder instructions (Codex, Claude Code, Claudian) pick up the deployed `AGENTS.md` (and `CLAUDE.md`, which imports it); it only points them to `START_HERE.md` and tells them to write through the `pmo` CLI.

Example:

```json
{
  "source": "chatgpt",
  "session_id": "abc123",
  "topic": "PMO design",
  "memory_events": [
    {
      "type": "decision",
      "content": "Use a provider-neutral external memory layer.",
      "importance": 0.95,
      "explicitness": "explicit"
    }
  ],
  "corrections": [],
  "session": {
    "done": ["Designed the storage boundary"],
    "learned": [],
    "decisions": ["Keep private data out of GitHub"],
    "corrections": [],
    "open_loops": []
  }
}
```

## Native provider memory

Provider-native memory can coexist, but PMO treats it as supplementary rather than canonical user memory. When the two conflict, explicit user correction and canonical PMO data win.
