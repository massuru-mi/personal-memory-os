---
name: pmo-transcribe
description: Archive the current conversation into PMO's raw transcript layer (60_Transcripts/) with the most faithful method this assistant has — run the pmo importer, copy the app's log with a script, or, when neither is possible, write the transcript from the conversation in context and mark it as reconstructed. Use when the user asks to keep, archive or save the conversation's raw text in PMO, or at a checkpoint the user agreed to (for example the end of the day).
---

# PMO Transcribe Skill

Raw transcripts let a memory be traced back to what was actually said. Use the most faithful method available, say which one was used, and never touch another conversation's transcript.

## Non-negotiable rules

1. Read the active PMO `START_HERE.md` first. Transcripts are written only when `privacy.raw_chat_archiving` is `true` in `_config/settings.yaml`; otherwise stop and tell the user.
2. Write only the transcript of the conversation you are in. Never create, edit or delete a transcript of another conversation, and never write a file whose `source` the pmo importer handles (`claude-code`, `codex`).
3. Keep the user's and the assistant's words. Do not summarize, paraphrase, translate or correct them. Leave out tool output, thinking, and text the app injects (system prompts, reminders, environment and instruction blocks).
4. Replace secrets (API keys, tokens, passwords, private keys) with `[REDACTED:<kind>]` and count them. Other personal information stays as written.
5. Record how the transcript was captured (`capture`) honestly. Do not report it as saved until it has been written and read back.

## 1. Choose the method

Use the first one that works:

| | When | Method | `capture` |
|---|---|---|---|
| 1 | The pmo CLI has an importer for this app (`claude-code`, `codex`) | Run `pmo transcripts sync <vault>` (or `import`). Do not write the file yourself | (left out; written by pmo) |
| 2 | No importer, but a program can read the app's log or export file | Copy it with a script (section 2) | `copied` |
| 3 | Neither: the conversation is only available in your context | Write it from the conversation (section 3) | `agent-reconstructed` |

It is method 2 only if the text goes from the log to the file inside a program. If you read the log into your context and write it out again, it is method 3.

## 2. Copy with a script

1. Read the log or export with a script; keep only user and assistant messages, in order, with their times.
2. Drop tool output, thinking and injected text. Turn tool calls into one-line markers: `- tool \`<name>\`: <main argument>`.
3. Render the file as in section 4 from the script, then apply the redaction in section 5 in the script.
4. If the same app is copied this way more than once, suggest to the user that PMO add an importer for it, so it can move to method 1.

## 3. Write from the conversation

1. Write each message as it was said. When a message is too long to reproduce, keep what you can and mark the gap as `[omitted: <what was left out>]`. Never fill a gap with a summary presented as the original.
2. Tool calls may be one-line markers, only for calls you are sure of. Do not invent any.
3. Write at a checkpoint, not after every turn: one write per session covers everything since the last write. When the session's file already exists, replace it with the full, updated content.

## 4. File and frontmatter

Path: `60_Transcripts/<YYYY-MM-DD>/<source>_<session id>.md`, where the date is the day the session started in the vault timezone.

- `source`: a short lowercase name for the app, such as `muse` or `chatgpt`.
- `session_id`: the app's ID for the conversation. When a chat never ends (one long main chat), split it by day in the vault timezone and use `<chat id>_<YYYY-MM-DD>`; each day is its own file. Without any app ID, use a new random ID and keep using it for that conversation.

Follow `_system/templates/transcript.md` exactly:

- required: `schema: pmo.transcript/v1`, `source`, `session_id`, `title` (the first user message, 60 characters at most), `started_at`, `updated_at` (with timezone offset), `turns`, `redactions`, `capture`;
- optional, only when known: `cwd`, `chat_id`, `thread` (`main` or `side`), `parent_chat_id` (for a side chat), `app`, `app_version`, `models`, `efforts`. Do not guess a model or effort; leave the key out.

Body: `# <title>`, then one `## YYYY-MM-DD HH:MM User` or `## YYYY-MM-DD HH:MM Assistant` section per turn, in order. Push headings inside a message down two levels (`#` → `###`) so they never look like turn headings. The full format is in the repository's `docs/transcripts.md`.

Save as UTF-8 without a BOM, with LF line endings, as an ordinary file (not a converted Google Doc). The first line must be exactly `---`.

## 5. Redaction

Replace each of these with `[REDACTED:<kind>]` and add the count to `redactions`:

- private keys (`-----BEGIN … PRIVATE KEY-----` blocks): `private-key`;
- API keys and tokens: `sk-ant-…` (`anthropic-key`), `sk-…` (`openai-key`), `ghp_…` / `github_pat_…` (`github-token`), `AKIA…` (`aws-access-key`), `AIza…` (`google-api-key`), `xox…` (`slack-token`), JWTs `eyJ….eyJ….…` (`jwt`), the value after `Bearer ` (`bearer-token`);
- the value in `api_key=`, `secret=`, `access_token:`, `client_secret`, `password=` and similar assignments: `secret`.

When unsure whether something is a secret, redact it.

## 6. Read back and link memories

1. Read the file back; check the first line, the frontmatter keys, the turn headings and that no secret remains.
2. When you record a memory from this conversation, set `source_session: "<source>:<session id>"` to the same ID, using the session (day) the remembered message belongs to.

## 7. Report

Tell the user, in their language: the path, the method and `capture` value, the number of turns and redactions, anything omitted, and anything that could not be completed.
