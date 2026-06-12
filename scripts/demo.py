from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

import httpx

WORKSPACE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WORKSPACE / "src"))

from videoedgeai_task.main import app  # noqa: E402


async def main() -> None:
    idea = "make a tool that helps busy founders turn messy product notes into clearer pitches"

    transport = httpx.ASGITransport(app=app)
    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(transport=transport, base_url="http://demo") as client:
            start = await client.post("/api/v1/pipeline/start", json={"text": idea})
            start.raise_for_status()
            tracking_id = start.json()["tracking_id"]

            audit = await client.post(f"/api/v1/pipeline/audit/{tracking_id}")
            audit.raise_for_status()

            final = await client.post(f"/api/v1/pipeline/finalize/{tracking_id}")
            final.raise_for_status()

            detail = await client.get(f"/api/v1/pipeline/{tracking_id}")
            detail.raise_for_status()

    print("tracking_id:", tracking_id)
    print("\nfirst_audit:")
    print(json.dumps(audit.json(), indent=2))
    print("\nfinalize:")
    print(json.dumps(final.json(), indent=2))
    print("\ncounts:")
    payload = detail.json()
    print(
        json.dumps(
            {
                "versions": len(payload["versions"]),
                "audits": len(payload["audits"]),
                "llm_calls": len(payload["llm_calls"]),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    asyncio.run(main())
