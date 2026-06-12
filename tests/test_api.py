from __future__ import annotations

import httpx


async def test_full_pipeline_records_history(client: httpx.AsyncClient) -> None:
    start = await client.post(
        "/api/v1/pipeline/start",
        json={"text": "   make notes better for founders   "},
    )
    assert start.status_code == 201
    tracking_id = start.json()["tracking_id"]

    audit = await client.post(f"/api/v1/pipeline/audit/{tracking_id}")
    assert audit.status_code == 200
    assert audit.json()["needs_polish"] is True

    final = await client.post(f"/api/v1/pipeline/finalize/{tracking_id}")
    assert final.status_code == 200
    payload = final.json()
    assert payload["convergence_reason"] == "no_suggestions"
    assert payload["iteration_count"] == 1
    assert "Success measure:" in payload["final_text"]

    detail = await client.get(f"/api/v1/pipeline/{tracking_id}")
    assert detail.status_code == 200
    detail_payload = detail.json()
    assert len(detail_payload["versions"]) == 2
    assert len(detail_payload["audits"]) == 2
    assert len(detail_payload["llm_calls"]) == 3
    assert {call["prompt_type"] for call in detail_payload["llm_calls"]} == {"audit", "polish"}


async def test_unknown_tracking_id_returns_404(client: httpx.AsyncClient) -> None:
    response = await client.post("/api/v1/pipeline/audit/missing")
    assert response.status_code == 404


async def test_blank_text_returns_422(client: httpx.AsyncClient) -> None:
    response = await client.post("/api/v1/pipeline/start", json={"text": "   \n\t   "})
    assert response.status_code == 422

