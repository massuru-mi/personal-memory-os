from __future__ import annotations

from pathlib import Path

SYSTEM_DIR = "_system"
CONFIG_DIR = "_config"
INBOX_DIR = "00_Inbox"
MEMORY_DIR = "10_Memory"
PROJECTS_DIR = "20_Projects"
KNOWLEDGE_DIR = "30_Knowledge"
DECISIONS_DIR = "40_Decisions"
DAILY_DIR = "50_Daily"
ARCHIVE_DIR = "80_Archive"

DATA_DIRECTORIES = (
    f"{INBOX_DIR}/MemoryCandidates",
    f"{MEMORY_DIR}/Events",
    f"{MEMORY_DIR}/Self",
    f"{MEMORY_DIR}/Preferences",
    f"{MEMORY_DIR}/Corrections",
    f"{MEMORY_DIR}/Decisions",
    PROJECTS_DIR,
    KNOWLEDGE_DIR,
    DECISIONS_DIR,
    DAILY_DIR,
    ARCHIVE_DIR,
)

GENERATED_VIEWS = ("MEMORY.md", "NOW.md", "GUARDRAILS.md", "INDEX.md")
ROOT_SYSTEM_FILES = ("START_HERE.md",)
VERSION_FILE = "SYSTEM_VERSION.md"
MANIFEST_FILE = Path(SYSTEM_DIR) / "SYSTEM_MANIFEST.json"
SETTINGS_FILE = Path(CONFIG_DIR) / "settings.yaml"
