from __future__ import annotations

import httpx


async def test_reviewer_console_loads(client: httpx.AsyncClient) -> None:
    response = await client.get("/")

    assert response.status_code == 200
    assert "VideoEdgeAI-Task" in response.text
    assert "Run Full Pipeline" in response.text
    assert "Current / Final Text" in response.text
    assert "/api/v1/pipeline/start" in response.text
    assert "finalizeBtn" in response.text
    assert "providerChoice" in response.text
    assert "ollamaBaseUrl" in response.text
    assert "ollamaModel" in response.text
    assert "openaiBaseUrl" in response.text
    assert "openaiApiKey" in response.text


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
    assert audit.json()["is_perfect"] is False
    assert audit.json()["quality_score"] < 90
    assert audit.json()["rationale"]

    final = await client.post(f"/api/v1/pipeline/finalize/{tracking_id}")
    assert final.status_code == 200
    payload = final.json()
    assert payload["convergence_reason"] == "declared_perfect"
    assert payload["iteration_count"] == 1
    assert "Success measure:" in payload["final_text"]

    detail = await client.get(f"/api/v1/pipeline/{tracking_id}")
    assert detail.status_code == 200
    detail_payload = detail.json()
    assert len(detail_payload["versions"]) == 2
    assert len(detail_payload["audits"]) == 2
    assert len(detail_payload["llm_calls"]) == 3
    assert {call["prompt_type"] for call in detail_payload["llm_calls"]} == {"audit", "polish"}

    metrics = await client.get(f"/api/v1/pipeline/{tracking_id}/metrics")
    assert metrics.status_code == 200
    metrics_payload = metrics.json()
    assert metrics_payload["version_count"] == 2
    assert metrics_payload["audit_count"] == 2
    assert metrics_payload["llm_call_count"] == 3
    assert metrics_payload["successful_llm_call_count"] == 3
    assert metrics_payload["polish_iteration_count"] == 1
    assert metrics_payload["latest_needs_polish"] is False
    assert metrics_payload["air_gap_trace_ok"] is True
    assert metrics_payload["latest_is_perfect"] is True
    assert metrics_payload["latest_quality_score"] >= 90


async def test_action_endpoints_accept_mock_provider_body(client: httpx.AsyncClient) -> None:
    start = await client.post(
        "/api/v1/pipeline/start",
        json={"text": "make notes better for founders"},
    )
    tracking_id = start.json()["tracking_id"]

    audit = await client.post(
        f"/api/v1/pipeline/audit/{tracking_id}",
        json={"provider": "mock"},
    )
    final = await client.post(
        f"/api/v1/pipeline/finalize/{tracking_id}",
        json={"provider": "mock"},
    )

    assert audit.status_code == 200
    assert final.status_code == 200
    assert final.json()["convergence_reason"] == "declared_perfect"


async def test_openai_provider_body_requires_key(client: httpx.AsyncClient) -> None:
    start = await client.post(
        "/api/v1/pipeline/start",
        json={"text": "make notes better for founders"},
    )
    tracking_id = start.json()["tracking_id"]

    response = await client.post(
        f"/api/v1/pipeline/audit/{tracking_id}",
        json={"provider": "openai"},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "openai_api_key is required when provider is openai"


async def test_openai_compatible_provider_body_requires_base_url(
    client: httpx.AsyncClient,
) -> None:
    start = await client.post(
        "/api/v1/pipeline/start",
        json={"text": "make notes better for founders"},
    )
    tracking_id = start.json()["tracking_id"]

    response = await client.post(
        f"/api/v1/pipeline/audit/{tracking_id}",
        json={"provider": "openai_compatible"},
    )

    assert response.status_code == 422
    assert (
        response.json()["detail"]
        == "openai_base_url is required when provider is openai_compatible"
    )


async def test_finalize_is_idempotent_after_completion(client: httpx.AsyncClient) -> None:
    start = await client.post(
        "/api/v1/pipeline/start",
        json={"text": "make notes better for founders"},
    )
    tracking_id = start.json()["tracking_id"]

    first = await client.post(f"/api/v1/pipeline/finalize/{tracking_id}")
    second = await client.post(f"/api/v1/pipeline/finalize/{tracking_id}")
    metrics = await client.get(f"/api/v1/pipeline/{tracking_id}/metrics")

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["final_text"] == second.json()["final_text"]
    assert second.json()["iteration_count"] == 0
    assert metrics.json()["llm_call_count"] == 3


async def test_unknown_tracking_id_returns_404(client: httpx.AsyncClient) -> None:
    response = await client.post("/api/v1/pipeline/audit/missing")
    assert response.status_code == 404


async def test_blank_text_returns_422(client: httpx.AsyncClient) -> None:
    response = await client.post("/api/v1/pipeline/start", json={"text": "   \n\t   "})
    assert response.status_code == 422
