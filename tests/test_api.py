from __future__ import annotations

import httpx


async def test_reviewer_console_loads(client: httpx.AsyncClient) -> None:
    response = await client.get("/")

    assert response.status_code == 200
    assert "VideoEdgeAI-Task" in response.text
    assert "Run Full Pipeline" in response.text
    assert "Current / Final Text" in response.text
    assert "Review Score" in response.text
    assert "Reviewer Report" in response.text
    assert "copyReportBtn" in response.text
    assert "providerInfoBtn" in response.text
    assert "providerSummary" in response.text
    assert "/api/v1/pipeline/start" in response.text
    assert "/api/v1/pipeline/${id}/review" in response.text
    assert "/api/v1/pipeline/${id}/report" in response.text
    assert "finalizeBtn" in response.text
    assert "reviewPill" in response.text
    assert "providerChoice" in response.text
    assert "providerHelp" in response.text
    assert "How this provider is connected" in response.text
    assert "https://aistudio.google.com/app/apikey" in response.text
    assert "geminiApiKey" in response.text
    assert "anthropicApiKey" in response.text
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

    review = await client.get(f"/api/v1/pipeline/{tracking_id}/review")
    assert review.status_code == 200
    review_payload = review.json()
    assert review_payload["status"] == "completed"
    assert review_payload["likely_better_than_original"] is True
    assert review_payload["air_gap_trace_ok"] is True
    assert review_payload["quality_delta"] > 0
    assert review_payload["current_score"]["structure_coverage"] == 1.0
    assert review_payload["current_score"]["actionability_score"] == 5.0
    assert review_payload["latest_is_perfect"] is True

    report = await client.get(f"/api/v1/pipeline/{tracking_id}/report")
    assert report.status_code == 200
    report_payload = report.json()
    assert report_payload["status"] == "completed"
    assert report_payload["summary"] == "Ready for reviewer handoff."
    assert report_payload["trace_step_count"] == 3
    assert report_payload["providers"] == ["mock"]
    assert "audit.v5" in report_payload["prompt_versions"]
    assert "polish.v5" in report_payload["prompt_versions"]
    assert "# Pipeline Reviewer Report" in report_payload["markdown"]
    assert "## Air-Gap Evidence" in report_payload["markdown"]
    assert "## Recommended Next Checks" in report_payload["markdown"]


async def test_review_endpoint_handles_started_run(client: httpx.AsyncClient) -> None:
    start = await client.post(
        "/api/v1/pipeline/start",
        json={"text": "make notes better for founders"},
    )
    tracking_id = start.json()["tracking_id"]

    response = await client.get(f"/api/v1/pipeline/{tracking_id}/review")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "active"
    assert payload["likely_better_than_original"] is False
    assert payload["air_gap_trace_ok"] is False
    assert payload["version_count"] == 1
    assert payload["audit_count"] == 0
    assert payload["llm_call_count"] == 0
    assert payload["quality_delta"] == 0

    report = await client.get(f"/api/v1/pipeline/{tracking_id}/report")
    assert report.status_code == 200
    report_payload = report.json()
    assert report_payload["summary"] == "Needs reviewer attention before handoff."
    assert "Run finalize" in report_payload["recommended_next_checks"][0]


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


async def test_gemini_provider_body_requires_key(client: httpx.AsyncClient) -> None:
    start = await client.post(
        "/api/v1/pipeline/start",
        json={"text": "make notes better for founders"},
    )
    tracking_id = start.json()["tracking_id"]

    response = await client.post(
        f"/api/v1/pipeline/audit/{tracking_id}",
        json={"provider": "gemini"},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "gemini_api_key is required when provider is gemini"


async def test_claude_provider_body_requires_key(client: httpx.AsyncClient) -> None:
    start = await client.post(
        "/api/v1/pipeline/start",
        json={"text": "make notes better for founders"},
    )
    tracking_id = start.json()["tracking_id"]

    response = await client.post(
        f"/api/v1/pipeline/audit/{tracking_id}",
        json={"provider": "claude"},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "anthropic_api_key is required when provider is claude"


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
