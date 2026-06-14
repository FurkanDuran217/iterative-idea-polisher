from __future__ import annotations

from collections.abc import AsyncGenerator

import httpx
import pytest

from videoedgeai_task.config import Settings, get_settings
from videoedgeai_task.db import configure_database, dispose_db, drop_db, init_db
from videoedgeai_task.main import app


@pytest.fixture()
async def client(tmp_path) -> AsyncGenerator[httpx.AsyncClient, None]:
    db_path = tmp_path / "test.db"
    configure_database(f"sqlite+aiosqlite:///{db_path}")
    await init_db()
    app.dependency_overrides[get_settings] = lambda: Settings(
        database_url=f"sqlite+aiosqlite:///{db_path}",
        llm_provider="mock",
        gemini_api_key=None,
        openai_api_key=None,
        anthropic_api_key=None,
        max_iterations=5,
    )
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client
    app.dependency_overrides.clear()
    await drop_db()
    await dispose_db()


@pytest.fixture()
def settings() -> Settings:
    return Settings(
        database_url="sqlite+aiosqlite:///:memory:",
        llm_provider="mock",
        max_iterations=5,
    )
