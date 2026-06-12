from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Protocol

from videoedgeai_task.config import Settings

AUDIT_SYSTEM_PROMPT = (
    "You are a precise editor in an air-gapped pipeline. "
    "You receive only the current text, with no prior conversation. "
    "Suggest concrete improvements. Return strict JSON only."
)

AUDIT_USER_PROMPT = (
    'Suggest improvements. Return a JSON object with a key "suggestions" containing '
    "a list of strings. If no improvements are needed, return an empty list.\n\n"
    "Text:\n{text}"
)

POLISH_SYSTEM_PROMPT = (
    "You are a precise editor in an air-gapped pipeline. "
    "Apply only the supplied suggestions to the supplied text. "
    "Return only the improved version."
)

POLISH_USER_PROMPT = "Text:\n{text}\n\nSuggestions:\n{suggestions}"


class LLMProviderError(RuntimeError):
    pass


class AuditParseError(ValueError):
    pass


@dataclass(frozen=True)
class RawLLMResponse:
    content: str
    latency_ms: int


class LLMProvider(Protocol):
    name: str

    async def suggest_improvements(self, text: str, *, repair: bool = False) -> RawLLMResponse:
        raise NotImplementedError

    async def apply_suggestions(self, text: str, suggestions: list[str]) -> RawLLMResponse:
        raise NotImplementedError


def parse_audit_json(raw_output: str) -> list[str]:
    try:
        payload = json.loads(raw_output)
    except json.JSONDecodeError as exc:
        raise AuditParseError("audit response was not valid JSON") from exc

    if not isinstance(payload, dict):
        raise AuditParseError("audit response must be a JSON object")

    suggestions = payload.get("suggestions")
    if not isinstance(suggestions, list):
        raise AuditParseError('audit response must include a "suggestions" list')

    parsed: list[str] = []
    for suggestion in suggestions:
        if not isinstance(suggestion, str):
            raise AuditParseError("all suggestions must be strings")
        clean = suggestion.strip()
        if clean:
            parsed.append(clean)
    return parsed


class MockLLMProvider:
    name = "mock"

    async def suggest_improvements(self, text: str, *, repair: bool = False) -> RawLLMResponse:
        start = time.perf_counter()
        suggestions: list[str] = []
        required_labels = ["Problem:", "Audience:", "Value:", "Next step:", "Success measure:"]
        missing_labels = [label for label in required_labels if label not in text]

        if missing_labels:
            suggestions.append(
                "Restructure the idea with Problem, Audience, Value, Next step, "
                "and Success measure."
            )
        if len(text.split()) < 45:
            suggestions.append("Add enough concrete context for a reviewer to understand the idea.")
        if "Success measure:" not in text:
            suggestions.append("Add a measurable way to decide whether the idea improved.")

        raw = json.dumps({"suggestions": suggestions})
        latency_ms = round((time.perf_counter() - start) * 1000)
        return RawLLMResponse(content=raw, latency_ms=latency_ms)

    async def apply_suggestions(self, text: str, suggestions: list[str]) -> RawLLMResponse:
        start = time.perf_counter()
        compact = " ".join(text.split())
        improved = (
            "Polished idea\n\n"
            f"Problem: {compact}\n\n"
            "Audience: The people or team who feel this problem directly and need a clearer way "
            "to act on the idea.\n\n"
            "Value: The idea is easier to evaluate because it states the problem, the intended "
            "audience, the practical benefit, and the next decision point.\n\n"
            "Next step: Test the idea with one realistic user scenario, then revise the wording "
            "based on what felt unclear or unsupported.\n\n"
            "Success measure: A reviewer can identify the user, problem, benefit, next step, and "
            "evaluation criterion without asking follow-up questions."
        )
        latency_ms = round((time.perf_counter() - start) * 1000)
        return RawLLMResponse(content=improved, latency_ms=latency_ms)


class OpenAILLMProvider:
    name = "openai"

    def __init__(self, settings: Settings) -> None:
        if not settings.openai_api_key:
            raise LLMProviderError("OPENAI_API_KEY is required when LLM_PROVIDER=openai")
        try:
            from openai import AsyncOpenAI
        except ImportError as exc:
            raise LLMProviderError("Install the openai package to use LLM_PROVIDER=openai") from exc

        self._client = AsyncOpenAI(api_key=settings.openai_api_key)
        self._model = settings.openai_model

    async def suggest_improvements(self, text: str, *, repair: bool = False) -> RawLLMResponse:
        start = time.perf_counter()
        user_prompt = AUDIT_USER_PROMPT.format(text=text)
        if repair:
            user_prompt = (
                "Your previous response could not be parsed. Return strict JSON only, with exactly "
                'this shape: {"suggestions": ["..."]}.\n\n'
                f"{user_prompt}"
            )
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": AUDIT_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        content = response.choices[0].message.content or '{"suggestions": []}'
        latency_ms = round((time.perf_counter() - start) * 1000)
        return RawLLMResponse(content=content, latency_ms=latency_ms)

    async def apply_suggestions(self, text: str, suggestions: list[str]) -> RawLLMResponse:
        start = time.perf_counter()
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": POLISH_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": POLISH_USER_PROMPT.format(
                        text=text,
                        suggestions="\n".join(f"- {suggestion}" for suggestion in suggestions),
                    ),
                },
            ],
            temperature=0.3,
        )
        content = response.choices[0].message.content or text
        latency_ms = round((time.perf_counter() - start) * 1000)
        return RawLLMResponse(content=content, latency_ms=latency_ms)


def get_llm_provider(settings: Settings) -> LLMProvider:
    provider = settings.llm_provider.lower().strip()
    if provider == "mock":
        return MockLLMProvider()
    if provider == "openai":
        return OpenAILLMProvider(settings)
    raise LLMProviderError(f"Unsupported LLM_PROVIDER: {settings.llm_provider}")
