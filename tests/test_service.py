from __future__ import annotations

import json
from dataclasses import replace

import pytest

from videoedgeai_task.db import configure_database, dispose_db, drop_db, get_sessionmaker, init_db
from videoedgeai_task.llm import MockLLMProvider, RawLLMResponse
from videoedgeai_task.service import PipelineService


class MalformedOnceProvider(MockLLMProvider):
    def __init__(self) -> None:
        self.calls = 0

    async def suggest_improvements(self, text: str, *, repair: bool = False) -> RawLLMResponse:
        self.calls += 1
        if self.calls == 1:
            return RawLLMResponse(content="not json", latency_ms=1)
        return RawLLMResponse(content=json.dumps({"suggestions": []}), latency_ms=1)


class NeverConvergesProvider(MockLLMProvider):
    async def suggest_improvements(self, text: str, *, repair: bool = False) -> RawLLMResponse:
        return RawLLMResponse(content=json.dumps({"suggestions": ["keep improving"]}), latency_ms=1)

    async def apply_suggestions(self, text: str, suggestions: list[str]) -> RawLLMResponse:
        return RawLLMResponse(content=f"{text}\nImproved again.", latency_ms=1)


@pytest.fixture()
async def session(settings, tmp_path):
    configure_database(f"sqlite+aiosqlite:///{tmp_path / 'service.db'}")
    await init_db()
    async with get_sessionmaker()() as db_session:
        yield db_session
    await drop_db()
    await dispose_db()


async def test_audit_retries_malformed_json_once(session, settings) -> None:
    service = PipelineService(session, MalformedOnceProvider(), settings)
    run = await service.start("a complete idea")
    audit = await service.audit(run.tracking_id)
    assert audit.suggestions == []

    detail = await service.get_detail(run.tracking_id)
    assert len(detail.llm_calls) == 2
    assert detail.llm_calls[0].success is False
    assert detail.llm_calls[1].success is True


async def test_finalize_stops_at_max_iterations(session, settings) -> None:
    low_limit_settings = replace(settings, max_iterations=2)
    service = PipelineService(session, NeverConvergesProvider(), low_limit_settings)
    run = await service.start("launch something useful")
    result = await service.finalize(run.tracking_id)
    assert result.convergence_reason == "max_iterations_reached"
    assert result.iteration_count == 2
    assert result.version_count == 3
