---
name: pmo-update
description: Update an existing Personal Memory OS (PMO) vault to a newer PMO System version safely — install a pmo CLI that is not older than the vault, stop on System drift, run pmo update with its automatic backup, then verify with doctor, rebuild and readback. Use when the user asks to update, upgrade or redeploy PMO, or when a vault's System files are older than the PMO release they want.
---

# PMO Update Skill

Replace the System part of a PMO vault (`START_HERE.md`, `_system/**` and other manifest-owned files) with a newer PMO version. Config and Data are never overwritten.

## Non-negotiable rules

1. Read the active PMO `START_HERE.md` first.
2. Never downgrade: the PMO package used for the update must be the same or a newer version than the vault's `system_version`, and built from the commit the user chose (normally the latest `main` or a release).
3. If System drift is reported, stop. Do not use `--force-system-drift` without the user's explicit approval for that action.
4. Keep the automatic backup: never pass `--no-backup`.
5. Do not report the update complete until doctor passes and the deployed files have been read back.

## Preferred path: the pmo CLI

### 1. Inspect the vault

```bash
pmo --json status /path/to/PMO
```

Note `system_version`, `deployed_commit` and `system_drift`. If `system_drift` is not empty, stop and report the listed files. If the user customized System files, suggest moving those rules to `_config/custom_rules.md`; restoring the System files needs explicit approval.

### 2. Install the target PMO version

`pmo update` deploys **the installed package**; it does not download anything. Install the package from the chosen source first, for example:

```bash
uv tool install --reinstall --python 3.12 /path/to/personal-memory-os-checkout
# or: python -m pip install --upgrade /path/to/personal-memory-os-checkout
```

Use a clean checkout or exported snapshot of the chosen commit, not a working tree with unrelated local changes. Confirm the installed version (`uv tool list` or `python -m pip show personal-memory-os`) is not older than the vault's `system_version`, and record the commit SHA.

### 3. Update

```bash
pmo update /path/to/PMO --commit <commit sha>
```

Note the `backup` path in the output. If the output reports files it skipped because the user already owned them (for example an existing `AGENTS.md` or `CLAUDE.md`), tell the user; PMO never overwrites them.

### 4. Verify

```bash
pmo --json doctor /path/to/PMO
pmo rebuild /path/to/PMO
pmo --json status /path/to/PMO
```

Check that doctor passes, `deployed_commit` is the chosen commit, `system_drift` is empty, and read back `START_HERE.md` to confirm the new content is there. If doctor reports unreadable records, follow `_system/skills/pmo-doctor-repair/SKILL.md`.

## Without the CLI

A cloud assistant cannot run `pmo update`. Follow the "Repair / re-run behavior" of `skills/pmo-setup/SKILL.md` in the PMO repository, with the user's explicit request to update: pin the new commit, compare the manifest, stop on drift, replace only manifest-owned System files, regenerate the manifest and version file exactly, and verify from Drive. If any of this cannot be done exactly, report the update as incomplete.

## Report

Tell the user, in their language:

- the version and commit before and after;
- the backup path;
- skipped files, if any;
- the doctor result;
- that assistants pick up the new rules when they next read `START_HERE.md`, normally at the start of a new chat.
