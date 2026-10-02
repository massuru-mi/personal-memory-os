# Claude adapter guidance

The profile/project instruction should stay minimal: each new chat reads `START_HERE.md` from the user's PMO and follows it.

Use the available Google Drive connection, or a user-selected local PMO folder when operating locally. Do not duplicate runtime policy in Claude instructions. Do not modify `_system/**`. If required PMO files cannot be accessed, report the limitation.
