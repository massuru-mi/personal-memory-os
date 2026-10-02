import hashlib

import pytest

from personal_memory_os.paths import VaultPaths


@pytest.fixture(autouse=True)
def isolated_runtime(tmp_path, monkeypatch):
    """Tests must not write private indexes or locks into the user's home directory."""
    def runtime(paths):
        digest = hashlib.sha256(str(paths.root.resolve()).encode()).hexdigest()[:16]
        return tmp_path / "runtime" / digest

    monkeypatch.setattr(VaultPaths, "runtime_root", runtime)
