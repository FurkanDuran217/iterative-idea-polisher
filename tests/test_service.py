from __future__ import annotations

import json
from dataclasses import replace

import pytest

from videoedgeai_task.db import configure_database, dispose_db, drop_db, get_sessionmaker, init_db
from videoedgeai_task.llm import LLMProviderError, MockLLMProvider, RawLLMResponse
from videoedgeai_task.service import PipelineService


def raw_response(content: str) -> RawLLMResponse:
    return RawLLMResponse(
        content=content,
        latency_ms=1,
        model_name="test-model",
        provider_params={"temperature": 0.0},
    )


class MalformedOnceProvider(MockLLMProvider):
    def __init__(self) -> None:
        self.calls = 0

    async def suggest_improvements(self, text: str, *, repair: bool = False) -> RawLLMResponse:
        self.calls += 1
        if self.calls == 1:
            return raw_response("not json")
        return raw_response(json.dumps({"suggestions": []}))


class NeverConvergesProvider(MockLLMProvider):
    async def suggest_improvements(self, text: str, *, repair: bool = False) -> RawLLMResponse:
        return raw_response(json.dumps({"suggestions": ["keep improving"]}))

    async def apply_suggestions(self, text: str, suggestions: list[str]) -> RawLLMResponse:
        return raw_response(f"{text}\nImproved again.")


class EmptyPolishProvider(MockLLMProvider):
    async def apply_suggestions(self, text: str, suggestions: list[str]) -> RawLLMResponse:
        return raw_response("   \n   ")


class FailingAuditProvider(MockLLMProvider):
    async def suggest_improvements(self, text: str, *, repair: bool = False) -> RawLLMResponse:
        raise LLMProviderError("Ollama provider call failed; verify Ollama is running")


class FailingPolishProvider(MockLLMProvider):
    async def apply_suggestions(self, text: str, suggestions: list[str]) -> RawLLMResponse:
        raise TimeoutError("provider timed out")


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
    assert detail.llm_calls[1].input_text_version_id == detail.versions[0].id
    assert detail.llm_calls[1].request_payload["prompt_version"] == "audit.v4"
    assert detail.llm_calls[1].parsed_output["is_perfect"] is True


async def test_finalize_stops_at_max_iterations(session, settings) -> None:
    low_limit_settings = replace(settings, max_iterations=2)
    service = PipelineService(session, NeverConvergesProvider(), low_limit_settings)
    run = await service.start("launch something useful")
    result = await service.finalize(run.tracking_id)
    assert result.convergence_reason == "max_iterations_reached"
    assert result.iteration_count == 2
    assert result.version_count == 3


async def test_empty_polish_output_records_failed_llm_call(session, settings) -> None:
    service = PipelineService(session, EmptyPolishProvider(), settings)
    run = await service.start("make notes better for founders")

    with pytest.raises(LLMProviderError, match="polish response was empty"):
        await service.finalize(run.tracking_id)

    detail = await service.get_detail(run.tracking_id)
    assert detail.llm_calls[-1].prompt_type == "polish"
    assert detail.llm_calls[-1].success is False
    assert detail.llm_calls[-1].error == "polish response was empty"
    assert detail.llm_calls[-1].output_text_version_id is None


async def test_provider_error_message_is_preserved_for_audit(session, settings) -> None:
    service = PipelineService(session, FailingAuditProvider(), settings)
    run = await service.start("make notes better for founders")

    with pytest.raises(LLMProviderError, match="verify Ollama is running"):
        await service.audit(run.tracking_id)

    detail = await service.get_detail(run.tracking_id)
    assert "verify Ollama is running" in str(detail.llm_calls[-1].error)


async def test_polish_provider_exception_records_failed_llm_call(session, settings) -> None:
    service = PipelineService(session, FailingPolishProvider(), settings)
    run = await service.start("make notes better for founders")

    with pytest.raises(LLMProviderError, match="polish provider call failed"):
        await service.finalize(run.tracking_id)

    detail = await service.get_detail(run.tracking_id)
    assert detail.llm_calls[-1].prompt_type == "polish"
    assert detail.llm_calls[-1].success is False
    assert "provider timed out" in str(detail.llm_calls[-1].error)
