"""Shared pytest fixtures."""

import pytest


@pytest.fixture(autouse=True)
def disable_codex_agents(monkeypatch):
    monkeypatch.setenv("CODEX_AGENTS_ENABLED", "false")
    from app.config import get_settings

    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
