from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from videoedgeai_task.utils import normalize_input_text


class StartPipelineRequest(BaseModel):
    text: str = Field(..., min_length=1)

    @field_validator("text")
    @classmethod
    def text_must_not_be_blank(cls, value: str) -> str:
        normalized = normalize_input_text(value)
        if not normalized:
            raise ValueError("text must not be blank")
        return value


class StartPipelineResponse(BaseModel):
    tracking_id: str


class AuditResponse(BaseModel):
    tracking_id: str
    suggestions: list[str]
    needs_polish: bool
    is_perfect: bool
    quality_score: int
    rationale: str
    iteration: int


class FinalizeResponse(BaseModel):
    tracking_id: str
    final_text: str
    iteration_count: int
    convergence_reason: str
    summary: str
    version_count: int
    audit_count: int


class TextVersionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    version_number: int
    text: str
    source_step: str
    created_at: datetime


class AuditRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    iteration: int
    suggestions: list[str]
    needs_polish: bool
    created_at: datetime


class LLMCallRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    input_text_version_id: int | None
    output_text_version_id: int | None
    iteration: int
    provider: str
    model_name: str | None
    prompt_type: str
    prompt_version: str
    request_hash: str
    request_payload: dict[str, Any]
    provider_params: dict[str, Any] | None
    raw_output: str | None
    parsed_output: dict[str, Any] | list[Any] | None
    latency_ms: int
    success: bool
    error: str | None
    created_at: datetime


class PipelineRunRead(BaseModel):
    tracking_id: str
    status: str
    original_text: str
    current_text: str
    created_at: datetime
    updated_at: datetime
    versions: list[TextVersionRead]
    audits: list[AuditRead]
    llm_calls: list[LLMCallRead]


class PipelineMetricsResponse(BaseModel):
    tracking_id: str
    status: str
    version_count: int
    audit_count: int
    llm_call_count: int
    successful_llm_call_count: int
    polish_iteration_count: int
    original_word_count: int
    current_word_count: int
    word_delta: int
    latest_needs_polish: bool | None
    air_gap_trace_ok: bool
    latest_is_perfect: bool | None
    latest_quality_score: int | None
    latest_rationale: str | None


class HealthResponse(BaseModel):
    status: str
    provider: str
    max_iterations: int
