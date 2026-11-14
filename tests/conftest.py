from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def root() -> Path:
    return ROOT


@pytest.fixture(scope="session")
def cadrage_dir(root: Path) -> Path:
    return root / "docs" / "cadrage"


@pytest.fixture(autouse=True)
def api_test_keys(monkeypatch):
    monkeypatch.setenv("API_KEYS", "test-client-key-123456:client,test-admin-key-123456:admin")
    monkeypatch.setenv("API_KEY", "test-client-key-123456")
