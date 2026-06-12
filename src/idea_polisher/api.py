from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from idea_polisher.config import Settings, get_settings
from idea_polisher.db import get_session
from idea_polisher.llm import LLMProviderError, get_llm_provider
from idea_polisher.schemas import (
    AuditRead,
    AuditResponse,
    FinalizeResponse,
    HealthResponse,
    LLMCallRead,
    PipelineMetricsResponse,
    PipelineRunRead,
    StartPipelineRequest,
    StartPipelineResponse,
    TextVersionRead,
)
from idea_polisher.service import PipelineInputError, PipelineNotFoundError, PipelineService

router = APIRouter(prefix="/api/v1", tags=["pipeline"])


def get_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> PipelineService:
    return PipelineService(session=session, provider=get_llm_provider(settings), settings=settings)


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
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    return StartPipelineResponse(tracking_id=run.tracking_id)


@router.post("/pipeline/audit/{tracking_id}", response_model=AuditResponse)
async def audit_pipeline(
    tracking_id: str,
    service: Annotated[PipelineService, Depends(get_service)],
) -> AuditResponse:
    try:
        audit = await service.audit(tracking_id)
    except PipelineNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except LLMProviderError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    return AuditResponse(
        tracking_id=tracking_id,
        suggestions=audit.suggestions,
        needs_polish=audit.needs_polish,
        iteration=audit.iteration,
    )


@router.post("/pipeline/finalize/{tracking_id}", response_model=FinalizeResponse)
async def finalize_pipeline(
    tracking_id: str,
    service: Annotated[PipelineService, Depends(get_service)],
) -> FinalizeResponse:
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


@router.get("/health", response_model=HealthResponse)
async def api_health(settings: Annotated[Settings, Depends(get_settings)]) -> HealthResponse:
    return HealthResponse(
        status="ok",
        provider=settings.llm_provider,
        max_iterations=settings.max_iterations,
    )
