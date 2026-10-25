# Raw transcripts (`60_Transcripts/`)

Raw transcripts keep the words of past conversations so that a memory can be traced back to what was actually said. They are user Data, written only when `privacy.raw_chat_archiving: true`, and they are not memory: bootstrap never loads them, and search includes them only when asked.

## File layout

One Markdown file per conversation:

```
60_Transcripts/<YYYY-MM-DD>/<source>_<session id>.md
```

The date is the day the conversation started, in the vault timezone (`language.timezone`). A conversation that grows keeps its file; re-importing rewrites it.

## Format (`pmo.transcript/v1`)

```markdown
---
schema: pmo.transcript/v1
source: claude-code
session_id: 968302e8-f5ff-477e-b248-d80a44606795
title: First words of the conversation…
cwd: /path/where/it/ran
app: claude-desktop
app_version: 2.1.308
started_at: '2026-10-24T21:14:24.675000+09:00'
updated_at: '2026-10-24T21:42:03.432000+09:00'
turns: 8
models:
- claude-opus-5-5
efforts:
- medium
tokens:
  input: 15963238
  cached_input: 15364078
  output: 73208
redactions: 0
---

# First words of the conversation…

## 2026-10-24 21:14 User

The user's words.

## 2026-10-24 21:14 Assistant (claude-opus-5-5, effort: medium)

- tool `WebSearch`: query

The assistant's words.
```

| Key | Meaning |
|---|---|
| `schema` | Always `pmo.transcript/v1` |
| `source` | Where the conversation came from, e.g. `claude-code` |
| `session_id` | The source's own conversation ID. `<source>:<session_id>` is what a memory's `source_session` points to |
| `title` | The session's title, or its first user message (60 characters at most) |
| `cwd` | Working folder, when the source has one |
| `started_at`, `updated_at` | First and last message times |
| `turns` | Number of `User` / `Assistant` sections |
| `redactions` | Number of secrets replaced with `[REDACTED:<kind>]` |

Optional metadata, written only when the source log records it. Transcripts without it keep exactly the keys above.

| Key | Meaning |
|---|---|
| `app`, `app_version` | The app the conversation ran in and its version |
| `models` | Models that wrote the assistant turns, in order of first use |
| `efforts` | Reasoning effort settings used, in order of first use |
| `tokens` | Session totals: `input` (including cached), `cached_input`, `output`, and `reasoning` when the source counts it separately |

In the body, an `Assistant` heading names the model and effort on the first assistant turn and again whenever they change.

## What is kept

- The user's and the assistant's words, as written.
- Tool calls, as one-line markers (`- tool <name>: <main argument>`).
- Images, as `[image]`.

Tool output, thinking, text the app injects (reminders, hook output, environment and instruction blocks), and subagent conversations are left out. API keys, tokens, passwords and private keys are replaced with `[REDACTED:<kind>]`; other personal information is kept as written. Headings inside a message are pushed two levels down so they never look like turn headings.
