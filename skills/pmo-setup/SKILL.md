---
name: pmo-setup
description: Safely initialize or attach Personal Memory OS (PMO) in a user-owned Google Drive location, verify the deployed files, and return a minimal runtime instruction that points new chats to START_HERE.md. Use when a user asks to install, initialize, set up, connect, or repair PMO in Google Drive.
---

# PMO Setup Skill

Set up Personal Memory OS from the repository into a user-approved Google Drive location. Treat the repository implementation as the source of truth and the user's existing Drive data as higher priority than setup convenience.

## Non-negotiable rules

1. **Before the first Google Drive write, have a user-approved destination.**
   - If the user already supplied a Drive folder, path, or URL in the request, use that as approval.
   - Otherwise propose `My Drive/PMO` and ask for explicit approval or a different destination.
   - Do not create even a temporary setup folder before this condition is met.
2. The standard new root folder name is `PMO`.
3. Never delete, overwrite, rename, or move pre-existing user content merely to make setup easier.
4. Do not infer the PMO layout from README alone. Inspect the current implementation.
5. Do not report setup complete until the Drive copy has been listed and important files have been read back.
6. Do not claim background synchronization, scheduled work, or connector permissions that do not exist.
7. Do not copy provider-native memory or old chats into PMO unless the user separately requests a migration.

## Phase 1 — Pin the source

Read the target repository and pin the exact source before writing Drive data.

For this repository, inspect at minimum:

- `AGENTS.md`
- `README.md` / `README.ja.md`
- `pyproject.toml`
- `src/personal_memory_os/__init__.py`
- `src/personal_memory_os/constants.py`
- `src/personal_memory_os/paths.py`
- `src/personal_memory_os/deploy.py`
- `src/personal_memory_os/resources.py`
- `src/personal_memory_os/views.py`
- all files under `src/personal_memory_os/system/`

Record the exact commit SHA and PMO version being deployed. If the repository or required files cannot be read, stop rather than inventing a layout.

## Phase 2 — Check Drive capability and destination

Confirm that the available Google Drive connection can:

- list folders/files;
- create folders;
- create ordinary raw files such as `.md`, `.yaml`, and `.json`;
- update file contents when needed;
- read file contents back;
- delete setup-created temporary files if temporary files are necessary.

A search-only connection or native Google Docs editing alone is insufficient.

Then enforce the destination rule:

- user-specified destination → proceed there;
- no destination → propose `My Drive/PMO` and wait for explicit approval.

Inspect the approved destination before writing. If it already contains a PMO installation, do not create a duplicate PMO. Inspect version, manifest, and contents and switch to repair/attach behavior. If it contains unrelated data, preserve it and avoid collisions.

## Phase 3 — Reproduce the current installer

Reproduce the behavior of the pinned `pmo install`, not a memorized file list.

Derive from the implementation:

- Data directories from `constants.py`;
- Config defaults from `system/defaults/settings.yaml`;
- System deployment files from `resources.py` and `system/`;
- generated root views from `views.py`;
- version metadata from `deploy.py`;
- manifest structure, protected paths, generated views, and file hashes from `deploy.py`.

Create the approved PMO root and required subdirectories. Save Markdown/YAML/JSON as ordinary files, not converted Google Docs.

System files are deployment-owned. Config and Data are user-owned. Never place personal user memory into the public repository.

## Phase 4 — Generate exact metadata

Create `SYSTEM_VERSION.md` using the pinned version/commit and the user's timezone when available.

Create `_system/SYSTEM_MANIFEST.json` from the files actually deployed. Hash the exact deployed bytes using the algorithm required by the implementation. Do not guess hashes or copy stale hashes from another installation.

If required metadata cannot be produced exactly, report setup incomplete rather than fabricating integrity data.

## Phase 5 — Verify from Drive

A successful create/upload response is not sufficient.

Re-list the PMO folder from Google Drive and verify the complete expected structure. Follow pagination if the connector paginates.

At minimum read back and inspect:

- `START_HERE.md`
- `_config/settings.yaml`
- `_system/SYSTEM_MANIFEST.json`
- `SYSTEM_VERSION.md`

Also verify that the expected adapter, protocol, schema, and template directories are populated.

If temporary connection/upload test files were created by this setup, remove them before completion. Never remove files that existed before setup.

## Phase 6 — Return the runtime bootstrap

Retrieve actual Drive links; never invent them.

Return:

- whether setup is complete;
- PMO version;
- deployed commit SHA;
- verified PMO folder link;
- verified `START_HERE.md` link;
- whether readback verification succeeded;
- any incomplete operations.

Then provide a minimal instruction for the current AI app, inserting the real `START_HERE.md` URL:

```text
このユーザーはPersonal Memory OS（PMO）を導入しています。
各新規チャットの開始時に、Google Drive上の［START_HERE.mdの実URL］を必ず読み、そこに記載された最新のルールに従ってください。
PMOへの読み書きが必要な場合はGoogle Drive接続を使用してください。START_HEREへアクセスできない場合は、読めた・保存できたと装わず、その旨を伝えてください。
```

Use the app's appropriate persistent instruction surface. If you cannot change that setting directly, provide the text for the user to paste; do not claim it was registered.

## Repair / re-run behavior

Setup should be idempotent where possible.

On a re-run:

1. inspect the existing PMO before creating anything;
2. compare version, manifest, System files, Config, and Data ownership;
3. preserve all canonical Data and user Config;
4. create only missing safe items unless the user explicitly requested an update/repair;
5. do not silently force-overwrite System drift;
6. verify again from Drive.

## Completion gate

Only say "setup complete" when all applicable checks are true:

- exact source version and commit are known;
- destination was supplied or explicitly approved;
- expected directories exist;
- System files exist;
- Config exists;
- generated initial views exist;
- version file exists;
- manifest exists and corresponds to deployed files;
- Drive listing was re-checked;
- important files were read back;
- setup-created temporary files are gone;
- no pre-existing user data was destroyed.

Otherwise report the completed subset and the specific remaining work.
