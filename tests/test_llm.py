from __future__ import annotations

import json
from dataclasses import replace
from typing import Any

import httpx
import pytest

from videoedgeai_task.config import Settings
from videoedgeai_task.llm import (
    AuditParseError,
    MockLLMProvider,
    OllamaLLMProvider,
    get_llm_provider,
    parse_audit_json,
    parse_audit_verdict,
)


def test_parse_audit_json_accepts_suggestions() -> None:
    assert parse_audit_json('{"suggestions": ["make it clearer", "add metric"]}') == [
        "make it clearer",
        "add metric",
    ]


def test_parse_audit_verdict_accepts_explicit_perfection() -> None:
    verdict = parse_audit_verdict(
        json.dumps(
            {
                "is_perfect": True,
                "quality_score": 97,
                "rationale": "Ready for review.",
                "suggestions": [],
            }
        )
    )

    assert verdict.is_perfect is True
    assert verdict.needs_polish is False
    assert verdict.quality_score == 97
    assert verdict.rationale == "Ready for review."


def test_parse_audit_verdict_stops_optional_style_churn() -> None:
    verdict = parse_audit_verdict(
        json.dumps(
            {
                "is_perfect": False,
                "quality_score": 90,
                "rationale": "The text clearly states the problem, audience, value, next step.",
                "suggestions": ["Consider adding a specific example or anecdote."],
            }
        )
    )

    assert verdict.is_perfect is True
    assert verdict.suggestions == []


def test_parse_audit_json_accepts_json_code_fence() -> None:
    raw = '```json\n{"suggestions": ["make it sharper"]}\n```'
    assert parse_audit_json(raw) == ["make it sharper"]


def test_parse_audit_json_deduplicates_and_caps_suggestions() -> None:
    long_suggestion = "x" * 700
    raw = {
        "suggestions": [
            "Add a metric",
            " add a metric ",
            long_suggestion,
            *[f"suggestion {index}" for index in range(20)],
        ]
    }
    parsed = parse_audit_json(json.dumps(raw))
    assert parsed[0] == "Add a metric"
    assert len(parsed) == 10
    assert parsed[1].endswith("...")
    assert len(parsed[1]) <= 503


@pytest.mark.parametrize(
    "raw",
    [
        "not json",
        "[]",
        '{"suggestions": "make it clearer"}',
        '{"suggestions": [123]}',
    ],
)
def test_parse_audit_json_rejects_malformed_output(raw: str) -> None:
    with pytest.raises(AuditParseError):
        parse_audit_json(raw)


def test_provider_selection_defaults_to_mock(settings: Settings) -> None:
    provider = get_llm_provider(settings)
    assert isinstance(provider, MockLLMProvider)


def test_provider_selection_supports_ollama(settings: Settings) -> None:
    provider = get_llm_provider(replace(settings, llm_provider="ollama"))
    assert isinstance(provider, OllamaLLMProvider)


async def test_ollama_provider_uses_chat_json_contract(
    settings: Settings,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    requests: list[dict[str, Any]] = []

    class FakeAsyncClient:
        def __init__(self, *, timeout: int) -> None:
            self.timeout = timeout

        async def __aenter__(self) -> FakeAsyncClient:
            return self

        async def __aexit__(self, *args: object) -> None:
            return None

        async def post(self, url: str, json: dict[str, Any]) -> httpx.Response:
            requests.append({"url": url, "json": json, "timeout": self.timeout})
            return httpx.Response(
                200,
                request=httpx.Request("POST", url),
                json={
                    "model": json["model"],
                    "message": {
                        "role": "assistant",
                        "content": (
                            '{"is_perfect": false, "quality_score": 72, '
                            '"rationale": "Needs a clearer success metric.", '
                            '"suggestions": ["Add a measurable success criterion."]}'
                        ),
                    },
                    "done": True,
                },
            )

    monkeypatch.setattr(httpx, "AsyncClient", FakeAsyncClient)
    provider = OllamaLLMProvider(
        replace(
            settings,
            ollama_base_url="http://localhost:11434",
            ollama_model="llama3.2:3b",
            llm_timeout_seconds=7,
        )
    )

    response = await provider.suggest_improvements("make notes better for founders")

    assert response.model_name == "llama3.2:3b"
    assert response.provider_params["base_url"] == "http://localhost:11434"
    assert requests[0]["url"] == "http://localhost:11434/api/chat"
    assert requests[0]["timeout"] == 7
    assert requests[0]["json"]["model"] == "llama3.2:3b"
    assert requests[0]["json"]["stream"] is False
    assert requests[0]["json"]["format"] == "json"
    assert requests[0]["json"]["options"]["temperature"] == 0.2
