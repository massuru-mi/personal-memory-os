# Daily / Session Protocol v1

The daily record is an activity log, not the canonical long-term memory store.

## One chat, one session file
Each AI conversation owns exactly one session file under:
`50_Daily/YYYY-MM-DD/<provider>_<session-id>_<topic>.md`

Different providers/chats MUST NOT edit the same session file. This prevents Google Drive synchronization conflicts.

Update the session after every meaningful turn. Keep it concise and cumulative under these sections:
- What we did
- What we learned
- Decisions
- Corrections
- Open loops

Do not paste the entire conversation transcript by default. Raw transcript archiving is optional and controlled by config.

`SUMMARY.md` is generated from session files and may be rebuilt at any time.
