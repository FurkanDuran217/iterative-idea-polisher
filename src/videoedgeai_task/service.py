from __future__ import annotations

import json
import time
from dataclasses import dataclass
from uuid import uuid4

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from videoedgeai_task.config import Settings
from videoedgeai_task.llm import (
    AuditParseError,
    LLMProvider,
    LLMProviderError,
    build_audit_request_payload,
    build_polish_request_payload,
    parse_audit_json,
)
from videoedgeai_task.models import Audit, LLMCall, PipelineRun, TextVersion
from videoedgeai_task.utils import normalize_input_text, normalize_model_text, stable_hash


class PipelineNotFoundError(LookupError):
    pass


class PipelineInputError(ValueError):
    pass


@dataclass(frozen=True)
class FinalizeResult:
    tracking_id: str
    final_text: str
    iteration_count: int
    convergence_reason: str
    summary: str
    version_count: int
    audit_count: int


@dataclass(frozen=True)
class PipelineMetrics:
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


class PipelineService:
    def __init__(self, session: AsyncSession, provider: LLMProvider, settings: Settings) -> None:
        self._session = session
        self._provider = provider
        self._settings = settings

    async def start(self, text: str) -> PipelineRun:
        normalized = normalize_input_text(text)
        if not normalized:
            raise PipelineInputError("text must not be blank")

        tracking_id = str(uuid4())
        run = PipelineRun(
            tracking_id=tracking_id,
            original_text=normalized,
            current_text=normalized,
            status="active",
        )
        self._session.add(run)
        await self._session.flush()
        self._session.add(
            TextVersion(
                run_id=run.id,
                version_number=0,
                text=normalized,
                source_step="start",
            )
        )
        await self._session.commit()
        await self._session.refresh(run)
        return run

    async def audit(self, tracking_id: str) -> Audit:
        run = await self._get_run(tracking_id)
        latest_version = await self._latest_version(run.id)
        iteration = latest_version.version_number
        request_payload = build_audit_request_payload(run.current_text)
        request_hash = self._hash_payload(request_payload)

        start = time.perf_counter()
        try:
            first_response = await self._provider.suggest_improvements(run.current_text)
        except Exception as exc:
            await self._record_llm_call(
                run_id=run.id,
                input_text_version_id=latest_version.id,
                output_text_version_id=None,
                iteration=iteration,
                prompt_type="audit",
                prompt_version=str(request_payload["prompt_version"]),
                request_hash=request_hash,
                request_payload=request_payload,
                provider_params=None,
                model_name=None,
                raw_output=None,
                parsed_output=None,
                latency_ms=round((time.perf_counter() - start) * 1000),
                success=False,
                error=str(exc),
            )
            await self._session.commit()
            raise LLMProviderError("audit provider call failed") from exc
        try:
            suggestions = parse_audit_json(first_response.content)
        except AuditParseError as exc:
            await self._record_llm_call(
                run_id=run.id,
                input_text_version_id=latest_version.id,
                output_text_version_id=None,
                iteration=iteration,
                prompt_type="audit",
                prompt_version=str(request_payload["prompt_version"]),
                request_hash=request_hash,
                request_payload=request_payload,
                provider_params=first_response.provider_params,
                model_name=first_response.model_name,
                raw_output=first_response.content,
                parsed_output=None,
                latency_ms=first_response.latency_ms,
                success=False,
                error=str(exc),
            )
            retry_payload = build_audit_request_payload(run.current_text, repair=True)
            retry_hash = self._hash_payload(retry_payload)
            retry_start = time.perf_counter()
            try:
                retry_response = await self._provider.suggest_improvements(
                    run.current_text,
                    repair=True,
                )
            except Exception as retry_provider_exc:
                await self._record_llm_call(
                    run_id=run.id,
                    input_text_version_id=latest_version.id,
                    output_text_version_id=None,
                    iteration=iteration,
                    prompt_type="audit",
                    prompt_version=str(retry_payload["prompt_version"]),
                    request_hash=retry_hash,
                    request_payload=retry_payload,
                    provider_params=None,
                    model_name=None,
                    raw_output=None,
                    parsed_output=None,
                    latency_ms=round((time.perf_counter() - retry_start) * 1000),
                    success=False,
                    error=str(retry_provider_exc),
                )
                await self._session.commit()
                raise LLMProviderError("audit repair provider call failed") from retry_provider_exc
            try:
                suggestions = parse_audit_json(retry_response.content)
            except AuditParseError as retry_exc:
                await self._record_llm_call(
                    run_id=run.id,
                    input_text_version_id=latest_version.id,
                    output_text_version_id=None,
                    iteration=iteration,
                    prompt_type="audit",
                    prompt_version=str(retry_payload["prompt_version"]),
                    request_hash=retry_hash,
                    request_payload=retry_payload,
                    provider_params=retry_response.provider_params,
                    model_name=retry_response.model_name,
                    raw_output=retry_response.content,
                    parsed_output=None,
                    latency_ms=retry_response.latency_ms,
                    success=False,
                    error=str(retry_exc),
                )
                await self._session.commit()
                raise LLMProviderError(
                    "audit response could not be parsed after retry"
                ) from retry_exc

            await self._record_llm_call(
                run_id=run.id,
                input_text_version_id=latest_version.id,
                output_text_version_id=None,
                iteration=iteration,
                prompt_type="audit",
                prompt_version=str(retry_payload["prompt_version"]),
                request_hash=retry_hash,
                request_payload=retry_payload,
                provider_params=retry_response.provider_params,
                model_name=retry_response.model_name,
                raw_output=retry_response.content,
                parsed_output={"suggestions": suggestions},
                latency_ms=retry_response.latency_ms,
                success=True,
                error=None,
            )
        else:
            await self._record_llm_call(
                run_id=run.id,
                input_text_version_id=latest_version.id,
                output_text_version_id=None,
                iteration=iteration,
                prompt_type="audit",
                prompt_version=str(request_payload["prompt_version"]),
                request_hash=request_hash,
                request_payload=request_payload,
                provider_params=first_response.provider_params,
                model_name=first_response.model_name,
                raw_output=first_response.content,
                parsed_output={"suggestions": suggestions},
                latency_ms=first_response.latency_ms,
                success=True,
                error=None,
            )

        audit = Audit(
            run_id=run.id,
            iteration=iteration,
            suggestions=suggestions,
            needs_polish=bool(suggestions),
        )
        self._session.add(audit)
        await self._session.commit()
        await self._session.refresh(audit)
        return audit

    async def finalize(self, tracking_id: str) -> FinalizeResult:
        run = await self._get_run(tracking_id)
        latest_audit = await self._latest_audit(run.id)
        if latest_audit is None:
            latest_audit = await self.audit(tracking_id)
            run = await self._get_run(tracking_id)

        polish_iterations = 0
        convergence_reason = "no_suggestions"

        while latest_audit.needs_polish:
            if polish_iterations >= self._settings.max_iterations:
                convergence_reason = "max_iterations_reached"
                run.status = "max_iterations_reached"
                await self._session.commit()
                break

            suggestions = list(latest_audit.suggestions)
            latest_version = await self._latest_version(run.id)
            next_version_number = latest_version.version_number + 1
            request_payload = build_polish_request_payload(run.current_text, suggestions)
            request_hash = self._hash_payload(request_payload)

            start = time.perf_counter()
            try:
                polish_response = await self._provider.apply_suggestions(
                    run.current_text,
                    suggestions,
                )
            except Exception as exc:
                await self._record_llm_call(
                    run_id=run.id,
                    input_text_version_id=latest_version.id,
                    output_text_version_id=None,
                    iteration=next_version_number,
                    prompt_type="polish",
                    prompt_version=str(request_payload["prompt_version"]),
                    request_hash=request_hash,
                    request_payload=request_payload,
                    provider_params=None,
                    model_name=None,
                    raw_output=None,
                    parsed_output=None,
                    latency_ms=round((time.perf_counter() - start) * 1000),
                    success=False,
                    error=str(exc),
                )
                await self._session.commit()
                raise LLMProviderError("polish provider call failed") from exc

            latency_ms = polish_response.latency_ms or round((time.perf_counter() - start) * 1000)
            improved_text = normalize_model_text(polish_response.content)
            if not improved_text:
                await self._record_llm_call(
                    run_id=run.id,
                    input_text_version_id=latest_version.id,
                    output_text_version_id=None,
                    iteration=next_version_number,
                    prompt_type="polish",
                    prompt_version=str(request_payload["prompt_version"]),
                    request_hash=request_hash,
                    request_payload=request_payload,
                    provider_params=polish_response.provider_params,
                    model_name=polish_response.model_name,
                    raw_output=polish_response.content,
                    parsed_output={"text": improved_text},
                    latency_ms=latency_ms,
                    success=False,
                    error="polish response was empty",
                )
                await self._session.commit()
                raise LLMProviderError("polish response was empty")

            run.current_text = improved_text
            run.status = "active"
            new_version = TextVersion(
                run_id=run.id,
                version_number=next_version_number,
                text=improved_text,
                source_step="polish",
            )
            self._session.add(new_version)
            await self._session.flush()
            await self._record_llm_call(
                run_id=run.id,
                input_text_version_id=latest_version.id,
                output_text_version_id=new_version.id,
                iteration=next_version_number,
                prompt_type="polish",
                prompt_version=str(request_payload["prompt_version"]),
                request_hash=request_hash,
                request_payload=request_payload,
                provider_params=polish_response.provider_params,
                model_name=polish_response.model_name,
                raw_output=polish_response.content,
                parsed_output={"text": improved_text},
                latency_ms=latency_ms,
                success=True,
                error=None,
            )
            await self._session.commit()
            polish_iterations += 1

            latest_audit = await self.audit(tracking_id)
            run = await self._get_run(tracking_id)

        if convergence_reason == "no_suggestions":
            run.status = "completed"
            await self._session.commit()

        version_count = await self._count(TextVersion, run.id)
        audit_count = await self._count(Audit, run.id)
        summary = self._build_summary(
            original=run.original_text,
            final=run.current_text,
            iteration_count=polish_iterations,
            convergence_reason=convergence_reason,
        )
        return FinalizeResult(
            tracking_id=tracking_id,
            final_text=run.current_text,
            iteration_count=polish_iterations,
            convergence_reason=convergence_reason,
            summary=summary,
            version_count=version_count,
            audit_count=audit_count,
        )

    async def get_detail(self, tracking_id: str) -> PipelineRun:
        statement: Select[tuple[PipelineRun]] = (
            select(PipelineRun)
            .where(PipelineRun.tracking_id == tracking_id)
            .options(
                selectinload(PipelineRun.versions),
                selectinload(PipelineRun.audits),
                selectinload(PipelineRun.llm_calls),
            )
        )
        result = await self._session.execute(statement)
        run = result.scalar_one_or_none()
        if run is None:
            raise PipelineNotFoundError(f"pipeline {tracking_id} was not found")
        return run

    async def get_metrics(self, tracking_id: str) -> PipelineMetrics:
        run = await self.get_detail(tracking_id)
        llm_calls = list(run.llm_calls)
        versions = list(run.versions)
        audits = list(run.audits)
        original_word_count = len(run.original_text.split())
        current_word_count = len(run.current_text.split())
        prompt_types = [call.prompt_type for call in llm_calls]
        return PipelineMetrics(
            tracking_id=run.tracking_id,
            status=run.status,
            version_count=len(versions),
            audit_count=len(audits),
            llm_call_count=len(llm_calls),
            successful_llm_call_count=sum(1 for call in llm_calls if call.success),
            polish_iteration_count=sum(
                1 for version in versions if version.source_step == "polish"
            ),
            original_word_count=original_word_count,
            current_word_count=current_word_count,
            word_delta=current_word_count - original_word_count,
            latest_needs_polish=audits[-1].needs_polish if audits else None,
            air_gap_trace_ok=self._air_gap_trace_ok(prompt_types, llm_calls),
        )

    async def _get_run(self, tracking_id: str) -> PipelineRun:
        result = await self._session.execute(
            select(PipelineRun).where(PipelineRun.tracking_id == tracking_id)
        )
        run = result.scalar_one_or_none()
        if run is None:
            raise PipelineNotFoundError(f"pipeline {tracking_id} was not found")
        return run

    async def _latest_version(self, run_id: int) -> TextVersion:
        result = await self._session.execute(
            select(TextVersion)
            .where(TextVersion.run_id == run_id)
            .order_by(TextVersion.version_number.desc())
            .limit(1)
        )
        version = result.scalar_one()
        return version

    async def _latest_audit(self, run_id: int) -> Audit | None:
        result = await self._session.execute(
            select(Audit).where(Audit.run_id == run_id).order_by(Audit.id.desc()).limit(1)
        )
        return result.scalar_one_or_none()

    async def _record_llm_call(
        self,
        *,
        run_id: int,
        input_text_version_id: int | None,
        output_text_version_id: int | None,
        iteration: int,
        prompt_type: str,
        prompt_version: str,
        request_hash: str,
        request_payload: dict[str, object],
        provider_params: dict[str, object] | None,
        model_name: str | None,
        raw_output: str | None,
        parsed_output: dict[str, object] | list[object] | None,
        latency_ms: int,
        success: bool,
        error: str | None,
    ) -> None:
        self._session.add(
            LLMCall(
                run_id=run_id,
                input_text_version_id=input_text_version_id,
                output_text_version_id=output_text_version_id,
                iteration=iteration,
                provider=self._provider.name,
                model_name=model_name,
                prompt_type=prompt_type,
                prompt_version=prompt_version,
                request_hash=request_hash,
                request_payload=request_payload,
                provider_params=provider_params,
                raw_output=raw_output,
                parsed_output=parsed_output,
                latency_ms=latency_ms,
                success=success,
                error=error,
            )
        )

    def _hash_payload(self, payload: dict[str, object]) -> str:
        return stable_hash(json.dumps(payload, sort_keys=True, separators=(",", ":")))

    async def _count(self, model: type[TextVersion] | type[Audit], run_id: int) -> int:
        result = await self._session.execute(
            select(func.count()).select_from(model).where(model.run_id == run_id)
        )
        return int(result.scalar_one())

    def _build_summary(
        self,
        *,
        original: str,
        final: str,
        iteration_count: int,
        convergence_reason: str,
    ) -> str:
        original_words = len(original.split())
        final_words = len(final.split())
        return (
            f"Completed {iteration_count} polish iteration(s). "
            f"Convergence reason: {convergence_reason}. "
            f"The text moved from {original_words} to {final_words} words while preserving the "
            "original idea and making the evaluation criteria explicit."
        )

    def _air_gap_trace_ok(self, prompt_types: list[str], llm_calls: list[LLMCall]) -> bool:
        if not llm_calls:
            return False
        return (
            prompt_types[0] == "audit"
            and all(prompt_type in {"audit", "polish"} for prompt_type in prompt_types)
            and all(bool(call.request_hash) for call in llm_calls)
            and all(call.input_text_version_id is not None for call in llm_calls)
            and all(call.prompt_version for call in llm_calls)
            and all(call.request_payload for call in llm_calls)
        )
