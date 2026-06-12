from __future__ import annotations

import json

import pytest

from videoedgeai_task.config import Settings
from videoedgeai_task.llm import (
    AuditParseError,
    MockLLMProvider,
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
