from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache


def _int_env(name: str, default: int) -> int:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    try:
        value = int(raw_value)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer") from exc
    if value < 1:
        raise ValueError(f"{name} must be greater than 0")
    return value


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "VideoEdgeAI-Task")
    app_env: str = os.getenv("APP_ENV", "local")
    database_url: str = os.getenv(
        "DATABASE_URL",
        "sqlite+aiosqlite:///./videoedgeai_task.db",
    )
    llm_provider: str = os.getenv("LLM_PROVIDER", "mock")
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    openai_base_url: str | None = os.getenv("OPENAI_BASE_URL")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
    llm_timeout_seconds: int = _int_env("LLM_TIMEOUT_SECONDS", 60)
    max_iterations: int = _int_env("MAX_ITERATIONS", 5)
    sql_echo: bool = os.getenv("SQL_ECHO", "false").lower() == "true"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
