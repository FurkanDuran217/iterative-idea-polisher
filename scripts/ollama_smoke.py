from __future__ import annotations

import asyncio
import json
import sys
from dataclasses import replace
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WORKSPACE / "src"))

from videoedgeai_task.config import get_settings  # noqa: E402
from videoedgeai_task.llm import (  # noqa: E402
    LLMProviderError,
    OllamaLLMProvider,
    parse_audit_verdict,
)


async def run_smoke() -> dict[str, object]:
    settings = replace(
        get_settings(),
        llm_provider="ollama",
    )
    provider = OllamaLLMProvider(settings)
    audit = await provider.suggest_improvements(
        "Founders paste messy customer notes and need a clearer product roadmap decision."
    )
    verdict = parse_audit_verdict(audit.content)
    polish = await provider.apply_suggestions(
        "Founders paste messy customer notes and need a clearer product roadmap decision.",
        verdict.suggestions,
    )
    return {
        "provider": provider.name,
        "model": audit.model_name,
        "audit_latency_ms": audit.latency_ms,
        "polish_latency_ms": polish.latency_ms,
        "is_perfect": verdict.is_perfect,
        "quality_score": verdict.quality_score,
        "suggestion_count": len(verdict.suggestions),
        "polished_preview": polish.content[:400],
    }


def main() -> int:
    try:
        payload = asyncio.run(run_smoke())
    except LLMProviderError as exc:
        print(str(exc))
        print("Start Ollama and pull a model, for example: ollama pull llama3.2:3b")
        return 1

    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
