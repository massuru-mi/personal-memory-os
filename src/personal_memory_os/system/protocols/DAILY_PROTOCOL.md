# Daily / Session Protocol v1

The Daily record is an optional activity log, not the canonical long-term memory store.

## Enablement

Do not create or update Daily files when `daily.enabled: false`.

When Daily is enabled, each AI conversation owns one provider/session-specific session file under:

`50_Daily/YYYY-MM-DD/<provider>_<session-id>_<topic>.md`

Different providers/chats must not edit the same session file.

If `daily.update_on_every_meaningful_turn` is enabled, keep the session file concise and cumulative under:

- What we did
- What we learned
- Decisions
- Corrections
- Open loops

Do not paste the full conversation transcript by default. Raw transcript archiving is separately controlled by Config.

`SUMMARY.md` is derived from session files and may be rebuilt. PMO does not create scheduled/background Daily updates by itself.
