# ChatGPT adapter guidance

The app instruction should stay minimal: each new chat reads `START_HERE.md` from the user's PMO and follows it.

Use the available Google Drive connection for PMO reads/writes. Do not duplicate runtime policy in ChatGPT custom instructions. Do not modify `_system/**`. If `START_HERE.md` or a required file cannot be accessed, say so rather than pretending PMO context was loaded.
