from __future__ import annotations

import argparse
import asyncio
import json
import tempfile
from dataclasses import asdict, replace
from pathlib import Path
from uuid import uuid4

from videoedgeai_task.config import get_settings
from videoedgeai_task.db import configure_database, dispose_db, drop_db, get_sessionmaker, init_db
from videoedgeai_task.llm import get_llm_provider
from videoedgeai_task.service import PipelineService


async def run(provider: str, text: str) -> dict[str, object]:
    settings = replace(get_settings(), llm_provider=provider)
    db_path = Path(tempfile.gettempdir()) / f"videoedgeai_task_provider_smoke_{uuid4().hex}.db"
    configure_database(f"sqlite+aiosqlite:///{db_path}")
    await init_db()
    try:
        async with get_sessionmaker()() as session:
            service = PipelineService(
                session=session,
                provider=get_llm_provider(settings),
                settings=settings,
            )
            run_record = await service.start(text)
            result = await service.finalize(run_record.tracking_id)
            metrics = await service.get_metrics(run_record.tracking_id)
            return {
                "provider": provider,
                "tracking_id": run_record.tracking_id,
                "result": asdict(result),
                "metrics": asdict(metrics),
            }
    finally:
        await drop_db()
        await dispose_db()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a real-provider pipeline smoke test.")
    parser.add_argument("--provider", default=get_settings().llm_provider)
    parser.add_argument(
        "--text",
        default="make a tool that helps founders clean up messy product notes",
    )
    args = parser.parse_args()
    payload = asyncio.run(run(args.provider, args.text))
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
