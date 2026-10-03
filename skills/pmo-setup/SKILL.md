---
name: pmo-setup
description: Safely initialize or attach Personal Memory OS (PMO) in a user-owned Google Drive location, verify the deployed files, and return a minimal runtime instruction that points new chats to START_HERE.md. Use when a user asks to install, initialize, set up, connect, or repair PMO in Google Drive.
---

# PMO Setup Skill

Set up Personal Memory OS from the repository into a user-approved Google Drive location. Treat the repository implementation as the source of truth and the user's existing Drive data as higher priority than setup convenience.

## Before anything else — tell the user

Start your first reply, before reading the repository or touching Drive, with a short notice in the user's language. For a Japanese-speaking user, for example:

```text
PMO のセットアップを始めます。複数ステップの作業なので、段階ごとに進捗をお伝えします。
途中で返答が途切れた場合は「続けて」と送ってください。作ったものを確認し、続きから再開します（重複して作ることはありません）。
```

Then report progress in one short line at the start of each phase (for example "Phase 3/6: System ファイルを配置中"), so that an interrupted run can be resumed from the conversation.

## Non-negotiable rules

1. **Before the first Google Drive write, have a user-approved destination.**
   - If the user already supplied a Drive folder, path, or URL in the request, use that as approval.
   - Otherwise propose `My Drive/PMO` and ask for explicit approval or a different destination.
   - Do not create even a temporary setup folder before this condition is met.
2. **Never create anything outside the approved destination** — no test files, temporary files or folders in `My Drive` root or anywhere else. All capability checks happen inside the approved destination (see Phase 2).
3. The standard new root folder name is `PMO`.
4. Never delete, overwrite, rename, or move pre-existing user content merely to make setup easier.
5. Do not infer the PMO layout from README alone. Inspect the current implementation.
6. Do not report setup complete until the Drive copy has been listed and important files have been read back.
7. Do not claim background synchronization, scheduled work, or connector permissions that do not exist.
8. Do not copy provider-native memory or old chats into PMO unless the user separately requests a migration.

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
- delete a file it created.

A search-only connection or native Google Docs editing alone is insufficient.

Check these **only after the destination is approved, and only inside it**:

1. Create the approved destination folder if it does not exist (this checks folder creation).
2. List the destination before creating the check file. If `.pmo-setup-check.md` already exists, treat it as pre-existing user content: do not modify or delete it, report the collision, and do not create a second check file. Continue only if the setup's required create/readback operations can be verified safely through the actual setup writes; deletion remains unverified.
3. Otherwise create exactly one check file with the fixed name `.pmo-setup-check.md` directly inside the destination, read it back, then delete it.
4. If a setup-created check file cannot be deleted, continue only if everything else works, and tell the user its exact name and location so they can delete it; never create a second check file.

Do not create check or temporary files anywhere else, and do not create them before the destination is approved.

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

Confirm that a setup-created `.pmo-setup-check.md` is gone (or its location was reported to the user). If the name was already occupied by a pre-existing file, confirm it was left untouched and the collision was reported. Also confirm that nothing was created outside the destination. Never remove files that existed before setup.

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

## Resuming after an interruption

When the user says 「続けて」, "continue", or asks to resume a setup that stopped part-way:

1. Do not start over and do not ask for the destination again if it was already approved in this conversation.
2. Reuse the version and commit pinned earlier in the conversation. If they are not available, pin the source again and check that already deployed System files match it; if they do not, report the mismatch instead of mixing versions.
3. List the destination and determine which phases are complete: directories, System files, Config, generated views, `SYSTEM_VERSION.md`, `_system/SYSTEM_MANIFEST.json`.
4. Tell the user in one line where you are resuming from, then continue with the first incomplete phase. Create only what is missing; never duplicate files or folders.
5. Finish with Phase 5 verification and the completion gate as usual.

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
- nothing was created outside the approved destination, and any setup-created `.pmo-setup-check.md` is gone or its location was reported; if the name was pre-existing, it was left untouched and the collision was reported;
- no pre-existing user data was destroyed.

Otherwise report the completed subset and the specific remaining work.
