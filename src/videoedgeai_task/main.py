from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from videoedgeai_task import __version__
from videoedgeai_task.api import router
from videoedgeai_task.config import get_settings
from videoedgeai_task.db import init_db
from videoedgeai_task.schemas import HealthResponse


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    await init_db()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version=__version__, lifespan=lifespan)
    app.include_router(router)

    @app.get("/health", response_model=HealthResponse, tags=["health"])
    async def health() -> HealthResponse:
        return HealthResponse(
            status="ok",
            provider=settings.llm_provider,
            max_iterations=settings.max_iterations,
        )

    return app


app = create_app()
