# ChatGPT adapter guidance

When Google Drive is connected, use `START_HERE.md` as the protocol entrypoint. Read the generated context views before answering context-sensitive requests. Perform the Memory Check every meaningful turn and update the chat's daily session file. New durable items should be written as separate memory-event files; user corrections should be separate correction files.

Do not modify `_system/**`. Avoid multiple assistants writing the same file; use provider/session-specific filenames.
