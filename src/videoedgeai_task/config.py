from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


def _load_local_env() -> None:
    env_path = Path(".env")
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


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


_load_local_env()


def _default_provider() -> str:
    explicit_provider = os.getenv("LLM_PROVIDER")
    if explicit_provider:
        return explicit_provider
    if os.getenv("GEMINI_API_KEY"):
        return "gemini"
    return "mock"


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "VideoEdgeAI-Task")
    app_env: str = os.getenv("APP_ENV", "local")
    database_url: str = os.getenv(
        "DATABASE_URL",
        "sqlite+aiosqlite:///./videoedgeai_task.db",
    )
    llm_provider: str = _default_provider()
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    openai_base_url: str | None = os.getenv("OPENAI_BASE_URL")
    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    gemini_base_url: str = os.getenv(
        "GEMINI_BASE_URL",
        "https://generativelanguage.googleapis.com",
    )
    anthropic_api_key: str | None = os.getenv("ANTHROPIC_API_KEY")
    anthropic_model: str = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5")
    anthropic_base_url: str = os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
    llm_timeout_seconds: int = _int_env("LLM_TIMEOUT_SECONDS", 60)
    max_iterations: int = _int_env("MAX_ITERATIONS", 5)
    sql_echo: bool = os.getenv("SQL_ECHO", "false").lower() == "true"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
