from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from typing import Any, Protocol

import httpx

from videoedgeai_task.config import Settings

AUDIT_PROMPT_VERSION = "audit.v5"
POLISH_PROMPT_VERSION = "polish.v5"
MAX_SUGGESTIONS = 10
MAX_SUGGESTION_CHARS = 500

AUDIT_SYSTEM_PROMPT = (
    "You are a strict senior product editor inside an air-gapped refinement pipeline. "
    "You receive only the current text, with no prior conversation or memory. "
    "Judge whether the idea is ready for a hiring-task reviewer. Return strict JSON only."
)

AUDIT_USER_PROMPT = (
    "Audit the idea for clarity, specificity, actionability, faithfulness, and reviewer fit. "
    "Evaluate it as a concise idea brief, not as a full product specification. "
    "The best final output should help a reviewer quickly identify who the idea is for, what pain "
    "it addresses, why the rewrite helps, what should be tested next, and how success is measured. "
    "Do not ask for implementation details, UI details, technology stack, revenue projections, "
    "or extra features unless the current text explicitly makes those necessary. "
    "If the text states a clear user, problem, value, next step, and success measure while "
    "preserving the original intent, mark it perfect. "
    "Do not keep polishing just to add optional examples, anecdotes, implementation details, "
    "extra features, or ornamental specificity. Scores from 90 to 100 mean is_perfect must be "
    "true and suggestions must be empty. "
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
    "Apply only the supplied audit suggestions to the current text, infer cautiously from the "
    "user's wording, and preserve the original intent. Return only the improved text."
)

POLISH_USER_PROMPT = (
    "Rewrite the text as a concise, reviewer-ready idea brief. Use plain text only with exactly "
    "these labels in this order: Problem:, Audience:, Value:, Next step:, Success measure:. "
    "Write one tight sentence per label. Prefer concrete wording over longer wording. "
    "Make the next step a small validation action and the success measure observable. "
    "Avoid markdown headings, explanations, generic filler, implementation details, technology "
    "stack choices, UI details, revenue projections, and features the user did not imply. "
    "The output should be about 55-95 words and ready for a reviewer, not a product requirements "
    "document.\n\n"
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
    if not is_perfect and quality_score >= 90 and _only_optional_polish_suggestions(parsed):
        is_perfect = True
        parsed = []
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


def _only_optional_polish_suggestions(suggestions: list[str]) -> bool:
    if not suggestions:
        return True
    optional_markers = (
        "consider adding",
        "could benefit",
        "specific example",
        "anecdote",
        "illustrate",
        "more specific details",
    )
    return all(
        any(marker in suggestion.casefold() for marker in optional_markers)
        for suggestion in suggestions
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
            f"Next step: Test this brief with one target user using the original idea: {topic}.\n\n"
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
        return "People who need to turn a rough idea into a clearer decision."

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


class GeminiLLMProvider:
    name = "gemini"

    def __init__(self, settings: Settings) -> None:
        if not settings.gemini_api_key:
            raise LLMProviderError("GEMINI_API_KEY is required when provider=gemini")
        self._api_key = settings.gemini_api_key
        self._model = settings.gemini_model
        self._base_url = settings.gemini_base_url.rstrip("/")
        self._timeout_seconds = settings.llm_timeout_seconds

    async def suggest_improvements(self, text: str, *, repair: bool = False) -> RawLLMResponse:
        payload = build_audit_request_payload(text, repair=repair)
        return await self._generate(
            system_prompt=str(payload["messages"][0]["content"]),
            user_prompt=str(payload["messages"][1]["content"]),
            temperature=float(payload["temperature"]),
            response_mime_type="application/json",
        )

    async def apply_suggestions(self, text: str, suggestions: list[str]) -> RawLLMResponse:
        payload = build_polish_request_payload(text, suggestions)
        return await self._generate(
            system_prompt=str(payload["messages"][0]["content"]),
            user_prompt=str(payload["messages"][1]["content"]),
            temperature=float(payload["temperature"]),
            response_mime_type="text/plain",
        )

    async def _generate(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        response_mime_type: str,
    ) -> RawLLMResponse:
        request_payload: dict[str, Any] = {
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "responseMimeType": response_mime_type,
            },
        }
        start = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
                response = await client.post(
                    f"{self._base_url}/v1beta/models/{self._model}:generateContent",
                    headers={"x-goog-api-key": self._api_key},
                    json=request_payload,
                )
                response.raise_for_status()
                payload = response.json()
        except httpx.HTTPStatusError as exc:
            raise LLMProviderError(f"Gemini request failed: {_http_status_detail(exc)}") from exc
        except httpx.HTTPError as exc:
            raise LLMProviderError(f"Gemini request failed: {exc}") from exc

        latency_ms = round((time.perf_counter() - start) * 1000)
        return RawLLMResponse(
            content=_extract_gemini_text(payload),
            latency_ms=latency_ms,
            model_name=self._model,
            provider_params={
                "temperature": temperature,
                "response_mime_type": response_mime_type,
                "base_url": self._base_url,
            },
        )


class AnthropicLLMProvider:
    name = "claude"

    def __init__(self, settings: Settings) -> None:
        if not settings.anthropic_api_key:
            raise LLMProviderError("ANTHROPIC_API_KEY is required when provider=claude")
        self._api_key = settings.anthropic_api_key
        self._model = settings.anthropic_model
        self._base_url = settings.anthropic_base_url.rstrip("/")
        self._timeout_seconds = settings.llm_timeout_seconds

    async def suggest_improvements(self, text: str, *, repair: bool = False) -> RawLLMResponse:
        payload = build_audit_request_payload(text, repair=repair)
        return await self._generate(
            system_prompt=str(payload["messages"][0]["content"]),
            user_prompt=str(payload["messages"][1]["content"]),
            temperature=float(payload["temperature"]),
        )

    async def apply_suggestions(self, text: str, suggestions: list[str]) -> RawLLMResponse:
        payload = build_polish_request_payload(text, suggestions)
        return await self._generate(
            system_prompt=str(payload["messages"][0]["content"]),
            user_prompt=str(payload["messages"][1]["content"]),
            temperature=float(payload["temperature"]),
        )

    async def _generate(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
    ) -> RawLLMResponse:
        request_payload: dict[str, Any] = {
            "model": self._model,
            "max_tokens": 1200,
            "temperature": temperature,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}],
        }
        start = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
                response = await client.post(
                    f"{self._base_url}/v1/messages",
                    headers={
                        "x-api-key": self._api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json",
                    },
                    json=request_payload,
                )
                response.raise_for_status()
                payload = response.json()
        except httpx.HTTPStatusError as exc:
            raise LLMProviderError(f"Claude request failed: {_http_status_detail(exc)}") from exc
        except httpx.HTTPError as exc:
            raise LLMProviderError(f"Claude request failed: {exc}") from exc

        latency_ms = round((time.perf_counter() - start) * 1000)
        return RawLLMResponse(
            content=_extract_anthropic_text(payload),
            latency_ms=latency_ms,
            model_name=self._model,
            provider_params={
                "temperature": temperature,
                "max_tokens": 1200,
                "base_url": self._base_url,
            },
        )


def _extract_gemini_text(payload: dict[str, Any]) -> str:
    candidates = payload.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        raise LLMProviderError("Gemini response did not include candidates")
    parts = candidates[0].get("content", {}).get("parts", [])
    if not isinstance(parts, list):
        raise LLMProviderError("Gemini response did not include text parts")
    texts = [part.get("text", "") for part in parts if isinstance(part, dict)]
    content = "\n".join(text for text in texts if isinstance(text, str)).strip()
    if not content:
        raise LLMProviderError("Gemini returned an empty response")
    return content


def _extract_anthropic_text(payload: dict[str, Any]) -> str:
    content_blocks = payload.get("content")
    if not isinstance(content_blocks, list):
        raise LLMProviderError("Claude response did not include content blocks")
    texts = [
        block.get("text", "")
        for block in content_blocks
        if isinstance(block, dict) and block.get("type") == "text"
    ]
    content = "\n".join(text for text in texts if isinstance(text, str)).strip()
    if not content:
        raise LLMProviderError("Claude returned an empty response")
    return content


def _http_status_detail(exc: httpx.HTTPStatusError) -> str:
    body = exc.response.text.strip().replace("\n", " ")
    try:
        payload = exc.response.json()
    except ValueError:
        payload = None
    if isinstance(payload, dict):
        error = payload.get("error")
        if isinstance(error, dict) and isinstance(error.get("message"), str):
            body = error["message"].splitlines()[0].strip()
    if len(body) > 320:
        body = f"{body[:320].rstrip()}..."
    return f"{exc.response.status_code} {exc.response.reason_phrase}: {body}"


def get_llm_provider(settings: Settings) -> LLMProvider:
    provider = settings.llm_provider.lower().strip()
    if provider == "mock":
        return MockLLMProvider()
    if provider == "ollama":
        return OllamaLLMProvider(settings)
    if provider == "gemini":
        return GeminiLLMProvider(settings)
    if provider in {"claude", "anthropic"}:
        return AnthropicLLMProvider(settings)
    if provider == "openai":
        return OpenAILLMProvider(settings)
    if provider == "openai_compatible":
        return OpenAILLMProvider(settings, provider_name="openai_compatible")
    raise LLMProviderError(f"Unsupported LLM_PROVIDER: {settings.llm_provider}")
