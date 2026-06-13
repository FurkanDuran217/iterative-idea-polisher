from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from typing import Any, Protocol

from videoedgeai_task.config import Settings

AUDIT_PROMPT_VERSION = "audit.v2"
POLISH_PROMPT_VERSION = "polish.v2"
MAX_SUGGESTIONS = 10
MAX_SUGGESTION_CHARS = 500

AUDIT_SYSTEM_PROMPT = (
    "You are a senior product editor inside an air-gapped refinement pipeline. "
    "You receive only the current text, with no prior conversation or memory. "
    "Judge whether the idea is ready for a reviewer. Return strict JSON only."
)

AUDIT_USER_PROMPT = (
    "Audit the idea for clarity, specificity, actionability, faithfulness, and reviewer fit. "
    "Return exactly this JSON shape:\n"
    "{{\n"
    '  "is_perfect": true|false,\n'
    '  "quality_score": 0-100,\n'
    '  "rationale": "one short sentence",\n'
    '  "suggestions": ["concrete edit 1", "concrete edit 2"]\n'
    "}}\n"
    "Mark is_perfect true only when the text is ready to submit without more edits. "
    "If is_perfect is false, include at least one specific suggestion. "
    "If is_perfect is true, suggestions must be an empty list.\n\n"
    "Text:\n{text}"
)

POLISH_SYSTEM_PROMPT = (
    "You are a precise product editor inside an air-gapped pipeline. "
    "Apply only the supplied audit suggestions to the current text. "
    "Preserve the user's original intent. Return only the improved text."
)

POLISH_USER_PROMPT = (
    "Rewrite the text as a clean idea brief with these sections when useful: "
    "Problem, Audience, Value, Next step, Success measure. "
    "Avoid generic filler and do not add a product that the user did not imply.\n\n"
    "Current text:\n{text}\n\n"
    "Audit suggestions:\n{suggestions}"
)


class LLMProviderError(RuntimeError):
    pass


class AuditParseError(ValueError):
    pass


@dataclass(frozen=True)
class AuditVerdict:
    is_perfect: bool
    quality_score: int
    rationale: str
    suggestions: list[str]

    @property
    def needs_polish(self) -> bool:
        return not self.is_perfect

    def to_dict(self) -> dict[str, Any]:
        return {
            "is_perfect": self.is_perfect,
            "quality_score": self.quality_score,
            "rationale": self.rationale,
            "suggestions": self.suggestions,
        }


@dataclass(frozen=True)
class RawLLMResponse:
    content: str
    latency_ms: int
    model_name: str
    provider_params: dict[str, Any] = field(default_factory=dict)


class LLMProvider(Protocol):
    name: str

    async def suggest_improvements(self, text: str, *, repair: bool = False) -> RawLLMResponse:
        raise NotImplementedError

    async def apply_suggestions(self, text: str, suggestions: list[str]) -> RawLLMResponse:
        raise NotImplementedError


def build_audit_request_payload(text: str, *, repair: bool = False) -> dict[str, Any]:
    user_prompt = AUDIT_USER_PROMPT.format(text=text)
    if repair:
        user_prompt = (
            "Your previous response could not be parsed. Return strict JSON only, with exactly "
            'this shape: {"is_perfect": false, "quality_score": 70, '
            '"rationale": "...", "suggestions": ["..."]}.\n\n'
            f"{user_prompt}"
        )
    return {
        "prompt_version": AUDIT_PROMPT_VERSION,
        "messages": [
            {"role": "system", "content": AUDIT_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.2,
    }


def build_polish_request_payload(text: str, suggestions: list[str]) -> dict[str, Any]:
    return {
        "prompt_version": POLISH_PROMPT_VERSION,
        "messages": [
            {"role": "system", "content": POLISH_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": POLISH_USER_PROMPT.format(
                    text=text,
                    suggestions="\n".join(f"- {suggestion}" for suggestion in suggestions),
                ),
            },
        ],
        "temperature": 0.3,
    }


def parse_audit_json(raw_output: str) -> list[str]:
    return parse_audit_verdict(raw_output).suggestions


def parse_audit_verdict(raw_output: str) -> AuditVerdict:
    normalized_output = _extract_json_object(raw_output)
    try:
        payload = json.loads(normalized_output)
    except json.JSONDecodeError as exc:
        raise AuditParseError("audit response was not valid JSON") from exc

    if not isinstance(payload, dict):
        raise AuditParseError("audit response must be a JSON object")

    suggestions = payload.get("suggestions")
    if not isinstance(suggestions, list):
        raise AuditParseError('audit response must include a "suggestions" list')

    parsed = _parse_suggestions(suggestions)
    quality_score = _parse_quality_score(payload.get("quality_score"), parsed)
    rationale = _parse_rationale(payload.get("rationale"), parsed)
    raw_is_perfect = payload.get("is_perfect")
    if raw_is_perfect is None:
        is_perfect = not parsed and quality_score >= 90
    elif isinstance(raw_is_perfect, bool):
        is_perfect = raw_is_perfect
    else:
        raise AuditParseError('"is_perfect" must be a boolean when provided')

    if parsed and is_perfect:
        is_perfect = False
    if not is_perfect and not parsed:
        raise AuditParseError("non-perfect audit responses must include suggestions")
    if is_perfect and quality_score < 90:
        quality_score = 90

    return AuditVerdict(
        is_perfect=is_perfect,
        quality_score=quality_score,
        rationale=rationale,
        suggestions=parsed,
    )


def _parse_suggestions(suggestions: list[Any]) -> list[str]:
    parsed: list[str] = []
    seen: set[str] = set()
    for suggestion in suggestions:
        if not isinstance(suggestion, str):
            raise AuditParseError("all suggestions must be strings")
        clean = re.sub(r"\s+", " ", suggestion).strip()
        if not clean:
            continue
        if len(clean) > MAX_SUGGESTION_CHARS:
            clean = f"{clean[:MAX_SUGGESTION_CHARS].rstrip()}..."
        dedupe_key = clean.casefold()
        if dedupe_key not in seen:
            parsed.append(clean)
            seen.add(dedupe_key)
        if len(parsed) >= MAX_SUGGESTIONS:
            break
    return parsed


def _parse_quality_score(raw_score: Any, suggestions: list[str]) -> int:
    if raw_score is None:
        return 68 if suggestions else 95
    if isinstance(raw_score, bool):
        raise AuditParseError('"quality_score" must be a number')
    if isinstance(raw_score, int | float):
        return max(0, min(100, round(raw_score)))
    raise AuditParseError('"quality_score" must be a number')


def _parse_rationale(raw_rationale: Any, suggestions: list[str]) -> str:
    if raw_rationale is None:
        return (
            "The idea still needs concrete refinement."
            if suggestions
            else "The idea is clear, specific, and ready for review."
        )
    if not isinstance(raw_rationale, str):
        raise AuditParseError('"rationale" must be a string')
    clean = re.sub(r"\s+", " ", raw_rationale).strip()
    return clean[:300] or "No rationale provided."


def _extract_json_object(raw_output: str) -> str:
    text = raw_output.strip()
    fenced = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", text, flags=re.DOTALL | re.IGNORECASE)
    if fenced:
        text = fenced.group(1).strip()
    if text.startswith("{") and text.endswith("}"):
        return text
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end > start:
        return text[start : end + 1]
    return text


class MockLLMProvider:
    name = "mock"
    model_name = "mock-rule-engine-v1"
    provider_params = {"temperature": 0.0, "deterministic": True}

    async def suggest_improvements(self, text: str, *, repair: bool = False) -> RawLLMResponse:
        start = time.perf_counter()
        verdict = self._audit_text(text)
        raw = json.dumps(verdict.to_dict())
        latency_ms = round((time.perf_counter() - start) * 1000)
        return RawLLMResponse(
            content=raw,
            latency_ms=latency_ms,
            model_name=self.model_name,
            provider_params=self.provider_params,
        )

    def _audit_text(self, text: str) -> AuditVerdict:
        suggestions: list[str] = []
        required_labels = ["Problem:", "Audience:", "Value:", "Next step:", "Success measure:"]
        missing_labels = [label for label in required_labels if label not in text]
        word_count = len(text.split())
        if missing_labels:
            suggestions.append(
                "Rewrite the idea as a reviewer-ready brief with Problem, Audience, Value, "
                "Next step, and Success measure."
            )
        if word_count < 55:
            suggestions.append(
                "Add enough concrete context so a reviewer can understand the user, problem, "
                "benefit, and decision point."
            )
        if "Success measure:" not in text:
            suggestions.append(
                "Add a measurable criterion for deciding whether the idea is better."
            )
        if "Audience:" in text and "people or team" in text:
            suggestions.append("Replace generic audience wording with the specific user implied.")
        if suggestions:
            score = max(35, 92 - len(suggestions) * 14)
            return AuditVerdict(
                is_perfect=False,
                quality_score=score,
                rationale="The idea is promising but not yet submission-ready.",
                suggestions=suggestions,
            )
        return AuditVerdict(
            is_perfect=True,
            quality_score=96,
            rationale="The idea is structured, specific, actionable, and ready for review.",
            suggestions=[],
        )

    async def apply_suggestions(self, text: str, suggestions: list[str]) -> RawLLMResponse:
        start = time.perf_counter()
        compact = " ".join(text.split())
        topic = compact.rstrip(".")
        audience = self._infer_audience(compact)
        problem = self._infer_problem(compact, audience)
        value = self._infer_value(compact, audience)
        improved = (
            f"Problem: {problem}\n\n"
            f"Audience: {audience}\n\n"
            f"Value: {value}\n\n"
            f"Next step: Test the brief with one realistic user who would say: {topic}.\n\n"
            "Success measure: A reviewer can identify the user, problem, benefit, next step, "
            "and evaluation criterion without asking follow-up questions."
        )
        latency_ms = round((time.perf_counter() - start) * 1000)
        return RawLLMResponse(
            content=improved,
            latency_ms=latency_ms,
            model_name=self.model_name,
            provider_params=self.provider_params,
        )

    def _infer_audience(self, text: str) -> str:
        lowered = text.lower()
        if "founder" in lowered:
            return "Early-stage founders who turn rough notes into product decisions or pitches."
        if "teacher" in lowered:
            return "Teachers who need to turn rough lesson ideas into measurable activities."
        if "analyst" in lowered:
            return "Analysts who convert raw research notes into stakeholder-ready briefs."
        if "ops" in lowered or "incident" in lowered:
            return "Operations teams that need cleaner postmortem drafts from scattered notes."
        return "The specific user group implied by the original idea."

    def _infer_problem(self, text: str, audience: str) -> str:
        lowered = text.lower()
        if "notes" in lowered:
            return (
                f"{audience.split(' who ')[0]} collect useful notes but struggle to turn them "
                "into a clear, reviewable next action."
            )
        return f"The current idea is useful but too rough for {audience.lower()} to evaluate."

    def _infer_value(self, text: str, audience: str) -> str:
        lowered = text.lower()
        if "pitch" in lowered:
            return "The service turns messy product notes into a clearer pitch or roadmap input."
        if "lesson" in lowered:
            return "The workflow turns rough teaching ideas into concrete, measurable activities."
        if "postmortem" in lowered or "incident" in lowered:
            return "The service turns incident fragments into a coherent postmortem draft faster."
        return (
            "The workflow turns a vague idea into a structured brief that is easier to judge, "
            "test, and improve."
        )


class OpenAILLMProvider:
    name = "openai"

    def __init__(self, settings: Settings, *, provider_name: str = "openai") -> None:
        api_key = settings.openai_api_key
        if not api_key and provider_name == "openai_compatible" and settings.openai_base_url:
            api_key = "local"
        if not api_key:
            raise LLMProviderError(
                "OPENAI_API_KEY is required when LLM_PROVIDER=openai"
            )
        try:
            from openai import AsyncOpenAI
        except ImportError as exc:
            raise LLMProviderError("Install the openai package to use LLM_PROVIDER=openai") from exc

        self._base_url: str | None
        if settings.openai_base_url:
            self._base_url = settings.openai_base_url.rstrip("/")
            self._client = AsyncOpenAI(api_key=api_key, base_url=self._base_url)
        else:
            self._base_url = None
            self._client = AsyncOpenAI(api_key=api_key)
        self.name = provider_name
        self._model = settings.openai_model

    async def suggest_improvements(self, text: str, *, repair: bool = False) -> RawLLMResponse:
        start = time.perf_counter()
        payload = build_audit_request_payload(text, repair=repair)
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=payload["messages"],
            response_format=payload["response_format"],
            temperature=payload["temperature"],
        )
        content = response.choices[0].message.content or '{"suggestions": []}'
        latency_ms = round((time.perf_counter() - start) * 1000)
        return RawLLMResponse(
            content=content,
            latency_ms=latency_ms,
            model_name=self._model,
            provider_params=self._provider_params(payload["temperature"]),
        )

    async def apply_suggestions(self, text: str, suggestions: list[str]) -> RawLLMResponse:
        start = time.perf_counter()
        payload = build_polish_request_payload(text, suggestions)
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=payload["messages"],
            temperature=payload["temperature"],
        )
        content = response.choices[0].message.content or text
        latency_ms = round((time.perf_counter() - start) * 1000)
        return RawLLMResponse(
            content=content,
            latency_ms=latency_ms,
            model_name=self._model,
            provider_params=self._provider_params(payload["temperature"]),
        )

    def _provider_params(self, temperature: object) -> dict[str, object]:
        params: dict[str, object] = {"temperature": temperature}
        if self._base_url:
            params["base_url"] = self._base_url
        return params


class OllamaLLMProvider:
    name = "ollama"

    def __init__(self, settings: Settings) -> None:
        self._base_url = settings.ollama_base_url.rstrip("/")
        self._model = settings.ollama_model
        self._timeout_seconds = settings.llm_timeout_seconds

    async def suggest_improvements(self, text: str, *, repair: bool = False) -> RawLLMResponse:
        payload = build_audit_request_payload(text, repair=repair)
        return await self._chat(
            messages=payload["messages"],
            temperature=float(payload["temperature"]),
            response_format="json",
        )

    async def apply_suggestions(self, text: str, suggestions: list[str]) -> RawLLMResponse:
        payload = build_polish_request_payload(text, suggestions)
        return await self._chat(
            messages=payload["messages"],
            temperature=float(payload["temperature"]),
            response_format=None,
        )

    async def _chat(
        self,
        *,
        messages: list[dict[str, str]],
        temperature: float,
        response_format: str | None,
    ) -> RawLLMResponse:
        try:
            import httpx
        except ImportError as exc:
            raise LLMProviderError("Install httpx to use LLM_PROVIDER=ollama") from exc

        request_payload: dict[str, object] = {
            "model": self._model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature},
        }
        if response_format:
            request_payload["format"] = response_format

        start = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
                response = await client.post(f"{self._base_url}/api/chat", json=request_payload)
                response.raise_for_status()
                payload = response.json()
        except Exception as exc:
            raise LLMProviderError(
                "Ollama provider call failed; verify Ollama is running and the model is pulled"
            ) from exc

        message = payload.get("message")
        if not isinstance(message, dict) or not isinstance(message.get("content"), str):
            raise LLMProviderError("Ollama response did not include message.content")

        latency_ms = round((time.perf_counter() - start) * 1000)
        return RawLLMResponse(
            content=message["content"],
            latency_ms=latency_ms,
            model_name=self._model,
            provider_params={
                "temperature": temperature,
                "base_url": self._base_url,
            },
        )


def get_llm_provider(settings: Settings) -> LLMProvider:
    provider = settings.llm_provider.lower().strip()
    if provider == "mock":
        return MockLLMProvider()
    if provider == "ollama":
        return OllamaLLMProvider(settings)
    if provider == "openai":
        return OpenAILLMProvider(settings)
    if provider == "openai_compatible":
        return OpenAILLMProvider(settings, provider_name="openai_compatible")
    raise LLMProviderError(f"Unsupported LLM_PROVIDER: {settings.llm_provider}")
