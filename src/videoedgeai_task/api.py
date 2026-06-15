from __future__ import annotations

from dataclasses import replace
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from videoedgeai_task.config import Settings, get_settings
from videoedgeai_task.db import get_session
from videoedgeai_task.llm import AuditVerdict, LLMProviderError, get_llm_provider
from videoedgeai_task.schemas import (
    AuditRead,
    AuditResponse,
    FinalizeResponse,
    HealthResponse,
    LLMCallRead,
    PipelineActionRequest,
    PipelineMetricsResponse,
    PipelineReportResponse,
    PipelineReviewResponse,
    PipelineRunRead,
    StartPipelineRequest,
    StartPipelineResponse,
    TextReviewScoreResponse,
    TextVersionRead,
)
from videoedgeai_task.service import PipelineInputError, PipelineNotFoundError, PipelineService

router = APIRouter(prefix="/api/v1", tags=["pipeline"])


def get_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> PipelineService:
    return PipelineService(session=session, provider=get_llm_provider(settings), settings=settings)


def build_action_service(
    session: AsyncSession,
    settings: Settings,
    payload: PipelineActionRequest | None,
) -> PipelineService:
    action = payload or PipelineActionRequest()
    if action.provider == "server":
        action_settings = settings
    elif action.provider == "mock":
        action_settings = replace(settings, llm_provider="mock")
    elif action.provider == "ollama":
        action_settings = replace(
            settings,
            llm_provider="ollama",
            ollama_base_url=action.ollama_base_url or settings.ollama_base_url,
            ollama_model=action.ollama_model or settings.ollama_model,
        )
    elif action.provider == "gemini":
        api_key = action.gemini_api_key or settings.gemini_api_key
        if not api_key:
            raise HTTPException(
                status_code=422,
                detail="gemini_api_key is required when provider is gemini",
            )
        action_settings = replace(
            settings,
            llm_provider="gemini",
            gemini_api_key=api_key,
            gemini_model=action.gemini_model or settings.gemini_model,
            gemini_base_url=action.gemini_base_url or settings.gemini_base_url,
        )
    elif action.provider == "claude":
        api_key = action.anthropic_api_key or settings.anthropic_api_key
        if not api_key:
            raise HTTPException(
                status_code=422,
                detail="anthropic_api_key is required when provider is claude",
            )
        action_settings = replace(
            settings,
            llm_provider="claude",
            anthropic_api_key=api_key,
            anthropic_model=action.anthropic_model or settings.anthropic_model,
            anthropic_base_url=action.anthropic_base_url or settings.anthropic_base_url,
        )
    elif action.provider == "openai":
        api_key = action.openai_api_key or settings.openai_api_key
        if not api_key:
            raise HTTPException(
                status_code=422,
                detail="openai_api_key is required when provider is openai",
            )
        action_settings = replace(
            settings,
            llm_provider="openai",
            openai_api_key=api_key,
            openai_model=action.openai_model or settings.openai_model,
            openai_base_url=action.openai_base_url or settings.openai_base_url,
        )
    else:
        base_url = action.openai_base_url or settings.openai_base_url
        if not base_url:
            raise HTTPException(
                status_code=422,
                detail="openai_base_url is required when provider is openai_compatible",
            )
        action_settings = replace(
            settings,
            llm_provider="openai_compatible",
            openai_api_key=action.openai_api_key or settings.openai_api_key or "local",
            openai_model=action.openai_model or settings.openai_model,
            openai_base_url=base_url,
        )

    try:
        provider = get_llm_provider(action_settings)
    except LLMProviderError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    return PipelineService(session=session, provider=provider, settings=action_settings)


@router.post(
    "/pipeline/start",
    response_model=StartPipelineResponse,
    status_code=status.HTTP_201_CREATED,
)
async def start_pipeline(
    payload: StartPipelineRequest,
    service: Annotated[PipelineService, Depends(get_service)],
) -> StartPipelineResponse:
    try:
        run = await service.start(payload.text)
    except PipelineInputError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc
    return StartPipelineResponse(tracking_id=run.tracking_id)


@router.post("/pipeline/audit/{tracking_id}", response_model=AuditResponse)
async def audit_pipeline(
    tracking_id: str,
    session: Annotated[AsyncSession, Depends(get_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    payload: Annotated[PipelineActionRequest | None, Body()] = None,
) -> AuditResponse:
    service = build_action_service(session=session, settings=settings, payload=payload)
    try:
        audit = await service.audit(tracking_id)
    except PipelineNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except LLMProviderError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    verdict = getattr(
        audit,
        "verdict",
        AuditVerdict(
            is_perfect=not audit.needs_polish,
            quality_score=95 if not audit.needs_polish else 68,
            rationale=(
                "The idea is ready for review."
                if not audit.needs_polish
                else "The idea still needs concrete refinement."
            ),
            suggestions=audit.suggestions,
        ),
    )
    return AuditResponse(
        tracking_id=tracking_id,
        suggestions=verdict.suggestions,
        needs_polish=verdict.needs_polish,
        is_perfect=verdict.is_perfect,
        quality_score=verdict.quality_score,
        rationale=verdict.rationale,
        iteration=audit.iteration,
    )


@router.post("/pipeline/finalize/{tracking_id}", response_model=FinalizeResponse)
async def finalize_pipeline(
    tracking_id: str,
    session: Annotated[AsyncSession, Depends(get_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    payload: Annotated[PipelineActionRequest | None, Body()] = None,
) -> FinalizeResponse:
    service = build_action_service(session=session, settings=settings, payload=payload)
    try:
        result = await service.finalize(tracking_id)
    except PipelineNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except LLMProviderError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    return FinalizeResponse(**result.__dict__)


@router.get("/pipeline/{tracking_id}", response_model=PipelineRunRead)
async def get_pipeline(
    tracking_id: str,
    service: Annotated[PipelineService, Depends(get_service)],
) -> PipelineRunRead:
    try:
        run = await service.get_detail(tracking_id)
    except PipelineNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return PipelineRunRead(
        tracking_id=run.tracking_id,
        status=run.status,
        original_text=run.original_text,
        current_text=run.current_text,
        created_at=run.created_at,
        updated_at=run.updated_at,
        versions=[TextVersionRead.model_validate(version) for version in run.versions],
        audits=[AuditRead.model_validate(audit) for audit in run.audits],
        llm_calls=[LLMCallRead.model_validate(call) for call in run.llm_calls],
    )


@router.get("/pipeline/{tracking_id}/metrics", response_model=PipelineMetricsResponse)
async def get_pipeline_metrics(
    tracking_id: str,
    service: Annotated[PipelineService, Depends(get_service)],
) -> PipelineMetricsResponse:
    try:
        metrics = await service.get_metrics(tracking_id)
    except PipelineNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return PipelineMetricsResponse(**metrics.__dict__)


@router.get("/pipeline/{tracking_id}/review", response_model=PipelineReviewResponse)
async def get_pipeline_review(
    tracking_id: str,
    service: Annotated[PipelineService, Depends(get_service)],
) -> PipelineReviewResponse:
    try:
        review = await service.get_review(tracking_id)
    except PipelineNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return PipelineReviewResponse(
        tracking_id=review.tracking_id,
        status=review.status,
        original_text=review.original_text,
        current_text=review.current_text,
        original_score=TextReviewScoreResponse(**review.original_score.__dict__),
        current_score=TextReviewScoreResponse(**review.current_score.__dict__),
        quality_delta=review.quality_delta,
        word_delta=review.word_delta,
        likely_better_than_original=review.likely_better_than_original,
        decision_rationale=review.decision_rationale,
        air_gap_trace_ok=review.air_gap_trace_ok,
        version_count=review.version_count,
        audit_count=review.audit_count,
        llm_call_count=review.llm_call_count,
        polish_iteration_count=review.polish_iteration_count,
        latest_needs_polish=review.latest_needs_polish,
        latest_is_perfect=review.latest_is_perfect,
    )


@router.get("/pipeline/{tracking_id}/report", response_model=PipelineReportResponse)
async def get_pipeline_report(
    tracking_id: str,
    service: Annotated[PipelineService, Depends(get_service)],
) -> PipelineReportResponse:
    try:
        report = await service.get_report(tracking_id)
    except PipelineNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return PipelineReportResponse(**report.__dict__)


@router.get("/health", response_model=HealthResponse)
async def api_health(settings: Annotated[Settings, Depends(get_settings)]) -> HealthResponse:
    return HealthResponse(
        status="ok",
        provider=settings.llm_provider,
        max_iterations=settings.max_iterations,
    )
