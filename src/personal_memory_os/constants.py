from __future__ import annotations

from pathlib import Path

SYSTEM_DIR = "_system"
CONFIG_DIR = "_config"
INBOX_DIR = "00_Inbox"
MEMORY_DIR = "10_Memory"
DAILY_DIR = "50_Daily"
ARCHIVE_DIR = "80_Archive"

DATA_DIRECTORIES = (
    f"{INBOX_DIR}/MemoryCandidates",
    f"{MEMORY_DIR}/Events",
    f"{MEMORY_DIR}/Corrections",
    DAILY_DIR,
    ARCHIVE_DIR,
)

GENERATED_VIEWS = ("MEMORY.md", "NOW.md", "GUARDRAILS.md", "INDEX.md")
# Vault root file -> System resource. Agent entrypoints use a non-standard source
# name so they are not picked up as instructions inside this repository.
ROOT_SYSTEM_FILES = {
    "START_HERE.md": "START_HERE.md",
    "AGENTS.md": "entrypoints/AGENTS.vault.md",
    "CLAUDE.md": "entrypoints/CLAUDE.vault.md",
}
VERSION_FILE = "SYSTEM_VERSION.md"
MANIFEST_FILE = Path(SYSTEM_DIR) / "SYSTEM_MANIFEST.json"
SETTINGS_FILE = Path(CONFIG_DIR) / "settings.yaml"
CUSTOM_RULES_FILE = Path(CONFIG_DIR) / "custom_rules.md"
