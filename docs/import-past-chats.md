# Import past chats

Chats from before you set up PMO still hold preferences, decisions and corrections. This is how to bring them into PMO, one chat at a time.

## Before you start

- PMO setup is complete
- The app you use for importing has the PMO entry point (custom instructions or similar) set

For the entry point, see [Getting started](../README.md#getting-started) in the README.

## Steps

1. Open the past chat you want to import, in the app where it was created.
2. Send the prompt below in that chat.
3. The assistant reports what it registered, grouped by scope. Check it, and say "that's wrong" to correct anything.

```text
Register the useful content of this chat in my PMO.

First read START_HERE in my Google Drive and follow the latest PMO rules.
From this whole chat, extract facts, preferences, decisions, project information and corrections that will be useful again, and save them as the appropriate canonical records.

- Do not save the transcript; keep only the important information.
- Give every record a scope: "global" only for what matters in every conversation; otherwise reuse an existing category, or create a new one if none fits.
- Keep what I said explicitly separate from AI inferences or suggestions; never save an inference as a fact about me.
- For information that may change over time, state in the record as of when it was true.
- Check for duplicates and contradictions with existing records, and follow the Correction Protocol when needed.

When done, briefly list what you registered, grouped by scope.
```

## What is imported and what is not

| Imported | Not imported |
|---|---|
| Facts, preferences, decisions, ongoing projects, corrections | The full transcript, one-off exchanges |
| What you said explicitly | AI inferences or suggestions (never saved as facts about you) |

Information that can change over time ("I currently use …") is recorded with the date it was true.

## Troubleshooting

- **The assistant says it cannot read START_HERE**: check that Google Drive is connected in that app.
- **The same item was registered twice**: ask "organize my memory" to get a proposal to merge duplicates.
- **New records do not appear in the lists (`MEMORY.md` etc.)**: the lists are not refreshed automatically. Ask "update the lists".

The setup skill ([`pmo-setup`](../skills/pmo-setup/SKILL.md)) also points to this import step at the end of setup.
