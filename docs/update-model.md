# Release and update model

Use semantic releases for PMO system versions. Config-schema and data-schema versions advance independently.

An update performs: drift check → backup → config migration → data migration → default merge → system deploy → view rebuild → version write.

Downgrading a data/config schema is intentionally unsupported by the generic updater because silent reverse migrations risk data loss. Restore a backup when rollback is needed.
