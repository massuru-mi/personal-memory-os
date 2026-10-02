# AI integration

PMO intentionally avoids making one model vendor the orchestrator.

## Cloud/mobile assistants

When a provider can access the user's private cloud folder, point it at `START_HERE.md`. The assistant reads context views and writes provider/session-specific Markdown according to the protocols. No PMO server is required for this path.

## App-based setup (design proposal)

ChatGPT and the Claude app are equal setup entrypoints in the
[cloud setup proposal](local-optional-design.ja.md). Neither requires Claude Code,
a local PMO installation or a scheduled job. Each app reads the same pinned GitHub
release and creates or connects to the same private Markdown vault through its
available Drive connection. App-specific setup changes the connector and instruction
settings, not the canonical schema.

After setup, present verified vault links and instructions for ChatGPT custom
instructions or Claude profile/project instructions. A project-scoped instruction
applies only inside that project. See the [instruction draft](custom-instructions.ja.md).
Check raw-file creation, content updates, listing and readback on each connection;
search access or native Google Docs editing alone is insufficient. End-to-end setup
and cross-app handoff remain unverified.

## Local agents

Local agents can operate directly on the mirrored vault or submit the provider-neutral JSON turn contract to `pmo ingest-turn`.

Example:

```json
{
  "source": "chatgpt",
  "session_id": "abc123",
  "topic": "Second Brain design",
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

Provider-native memory can coexist, but PMO treats it as a cache/optimization rather than canonical user memory. When the two conflict, explicit user correction and canonical PMO data win.
