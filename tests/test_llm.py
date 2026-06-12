from __future__ import annotations

import pytest

from videoedgeai_task.config import Settings
from videoedgeai_task.llm import (
    AuditParseError,
    MockLLMProvider,
    get_llm_provider,
    parse_audit_json,
)


def test_parse_audit_json_accepts_suggestions() -> None:
    assert parse_audit_json('{"suggestions": ["make it clearer", "add metric"]}') == [
        "make it clearer",
        "add metric",
    ]


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
