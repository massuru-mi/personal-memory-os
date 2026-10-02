# AI integration

PMO intentionally avoids making one model vendor the orchestrator.

## Cloud/mobile assistants

When a provider can access the user's private cloud folder, point it at `START_HERE.md`. The assistant reads context views and writes provider/session-specific Markdown according to the protocols. No PMO server is required for this path.

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
