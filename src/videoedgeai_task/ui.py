from __future__ import annotations

REVIEWER_CONSOLE_HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>VideoEdgeAI-Task</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f7f8fb;
      --panel: #ffffff;
      --ink: #17202a;
      --muted: #65758b;
      --line: #d8dee9;
      --accent: #0f766e;
      --accent-strong: #115e59;
      --warn: #b45309;
      --error: #b91c1c;
      --shadow: 0 18px 40px rgba(20, 32, 45, 0.08);
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
        "Segoe UI", sans-serif;
      line-height: 1.45;
    }

    header {
      border-bottom: 1px solid var(--line);
      background: var(--panel);
    }

    main,
    .topbar {
      width: min(1180px, calc(100% - 32px));
      margin: 0 auto;
    }

    .topbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      min-height: 72px;
      gap: 18px;
    }

    h1 {
      margin: 0;
      font-size: 22px;
      font-weight: 760;
      letter-spacing: 0;
    }

    .provider {
      display: flex;
      gap: 8px;
      align-items: center;
      color: var(--muted);
      font-size: 13px;
    }

    .dot {
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background: var(--accent);
      display: inline-block;
    }

    main {
      display: grid;
      grid-template-columns: minmax(320px, 0.9fr) minmax(460px, 1.35fr);
      gap: 18px;
      padding: 22px 0 34px;
    }

    section {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: var(--shadow);
      min-width: 0;
    }

    .panel-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      padding: 14px 16px;
      border-bottom: 1px solid var(--line);
    }

    h2 {
      margin: 0;
      font-size: 15px;
      font-weight: 720;
      letter-spacing: 0;
    }

    .panel-body {
      padding: 16px;
    }

    label {
      display: block;
      color: var(--muted);
      font-size: 13px;
      font-weight: 650;
      margin-bottom: 8px;
    }

    textarea,
    input {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 7px;
      color: var(--ink);
      background: #ffffff;
      font: inherit;
      outline: none;
    }

    textarea {
      min-height: 154px;
      resize: vertical;
      padding: 12px;
    }

    input {
      height: 42px;
      padding: 0 11px;
    }

    textarea:focus,
    input:focus {
      border-color: var(--accent);
      box-shadow: 0 0 0 3px rgba(15, 118, 110, 0.14);
    }

    .field + .field,
    .field + .actions,
    .actions + .field {
      margin-top: 14px;
    }

    .actions {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 8px;
    }

    button {
      min-height: 40px;
      border: 1px solid var(--line);
      border-radius: 7px;
      background: #ffffff;
      color: var(--ink);
      font: inherit;
      font-weight: 700;
      cursor: pointer;
    }

    button.primary {
      border-color: var(--accent);
      background: var(--accent);
      color: #ffffff;
    }

    button:hover {
      border-color: var(--accent-strong);
    }

    button:disabled {
      cursor: not-allowed;
      opacity: 0.58;
    }

    .status {
      min-height: 24px;
      margin-top: 12px;
      color: var(--muted);
      font-size: 13px;
    }

    .status.error {
      color: var(--error);
    }

    .grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 10px;
    }

    .metric {
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 10px;
      min-height: 74px;
    }

    .metric b {
      display: block;
      font-size: 22px;
      line-height: 1.1;
    }

    .metric span {
      color: var(--muted);
      display: block;
      font-size: 12px;
      margin-top: 6px;
    }

    .tabs {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }

    .tab {
      min-height: 34px;
      padding: 0 10px;
      font-size: 13px;
    }

    .tab.active {
      border-color: var(--accent);
      color: var(--accent-strong);
    }

    pre {
      margin: 0;
      white-space: pre-wrap;
      overflow-wrap: anywhere;
      font-size: 13px;
      background: #f4f6f8;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      min-height: 190px;
      max-height: 560px;
      overflow: auto;
    }

    .split {
      display: grid;
      grid-template-columns: 1fr;
      gap: 12px;
    }

    .list {
      display: grid;
      gap: 8px;
    }

    .item {
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 10px;
      background: #ffffff;
    }

    .item strong {
      display: block;
      margin-bottom: 5px;
    }

    .item small {
      color: var(--muted);
    }

    @media (max-width: 880px) {
      main {
        grid-template-columns: 1fr;
      }

      .topbar {
        align-items: flex-start;
        flex-direction: column;
        padding: 14px 0;
      }
    }

    @media (max-width: 560px) {
      main,
      .topbar {
        width: min(100% - 20px, 1180px);
      }

      .grid,
      .actions {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>
<body>
  <header>
    <div class="topbar">
      <h1>VideoEdgeAI-Task</h1>
      <div class="provider"><span class="dot"></span><span id="health">Checking</span></div>
    </div>
  </header>
  <main>
    <section>
      <div class="panel-header">
        <h2>Pipeline</h2>
      </div>
      <div class="panel-body">
        <div class="field">
          <label for="ideaText">Idea text</label>
          <textarea id="ideaText">make notes better for founders</textarea>
        </div>
        <div class="actions">
          <button class="primary" id="startBtn" type="button">Start</button>
          <button id="finalizeBtn" type="button">Finalize</button>
          <button id="auditBtn" type="button">Audit</button>
          <button id="refreshBtn" type="button">Refresh</button>
        </div>
        <div class="field">
          <label for="trackingId">Tracking ID</label>
          <input id="trackingId" autocomplete="off" spellcheck="false">
        </div>
        <div id="status" class="status">Ready</div>
      </div>
    </section>

    <section>
      <div class="panel-header">
        <h2>Run State</h2>
        <div class="tabs">
          <button class="tab active" data-tab="summary" type="button">Summary</button>
          <button class="tab" data-tab="versions" type="button">Versions</button>
          <button class="tab" data-tab="calls" type="button">LLM Calls</button>
          <button class="tab" data-tab="json" type="button">JSON</button>
        </div>
      </div>
      <div class="panel-body">
        <div class="grid">
          <div class="metric"><b id="versionCount">0</b><span>versions</span></div>
          <div class="metric"><b id="auditCount">0</b><span>audits</span></div>
          <div class="metric"><b id="llmCount">0</b><span>LLM calls</span></div>
        </div>
        <div class="split" style="margin-top: 12px;">
          <div id="summaryTab">
            <pre id="summaryOutput">No run loaded.</pre>
          </div>
          <div id="versionsTab" hidden>
            <div id="versionsOutput" class="list"></div>
          </div>
          <div id="callsTab" hidden>
            <div id="callsOutput" class="list"></div>
          </div>
          <div id="jsonTab" hidden>
            <pre id="jsonOutput">{}</pre>
          </div>
        </div>
      </div>
    </section>
  </main>

  <script>
    const state = {
      detail: null,
      metrics: null,
      final: null,
      audit: null,
    };

    const $ = (id) => document.getElementById(id);

    function setStatus(message, isError = false) {
      const status = $("status");
      status.textContent = message;
      status.className = isError ? "status error" : "status";
    }

    function setBusy(isBusy) {
      ["startBtn", "auditBtn", "finalizeBtn", "refreshBtn"].forEach((id) => {
        $(id).disabled = isBusy;
      });
    }

    async function requestJson(method, url, body) {
      const options = { method, headers: { "Content-Type": "application/json" } };
      if (body !== undefined) {
        options.body = JSON.stringify(body);
      }
      const response = await fetch(url, options);
      const text = await response.text();
      const payload = text ? JSON.parse(text) : {};
      if (!response.ok) {
        throw new Error(payload.detail || response.statusText);
      }
      return payload;
    }

    function trackingId() {
      return $("trackingId").value.trim();
    }

    async function startPipeline() {
      setBusy(true);
      try {
        const text = $("ideaText").value;
        const payload = await requestJson(
          "POST",
          "/api/v1/pipeline/start",
          { text },
        );
        $("trackingId").value = payload.tracking_id;
        setStatus("Started " + payload.tracking_id);
        await refreshRun();
      } catch (error) {
        setStatus(error.message, true);
      } finally {
        setBusy(false);
      }
    }

    async function auditPipeline() {
      await postRunAction("audit");
    }

    async function finalizePipeline() {
      await postRunAction("finalize");
    }

    async function postRunAction(action) {
      const id = trackingId();
      if (!id) {
        setStatus("Tracking ID required", true);
        return;
      }
      setBusy(true);
      try {
        const payload = await requestJson(
          "POST",
          `/api/v1/pipeline/${action}/${id}`,
        );
        state[action === "audit" ? "audit" : "final"] = payload;
        setStatus(action.charAt(0).toUpperCase() + action.slice(1) + " complete");
        await refreshRun();
      } catch (error) {
        setStatus(error.message, true);
      } finally {
        setBusy(false);
      }
    }

    async function refreshRun() {
      const id = trackingId();
      if (!id) {
        render();
        return;
      }
      setBusy(true);
      try {
        state.detail = await requestJson("GET", `/api/v1/pipeline/${id}`);
        state.metrics = await requestJson("GET", `/api/v1/pipeline/${id}/metrics`);
        setStatus("Loaded " + id);
        render();
      } catch (error) {
        setStatus(error.message, true);
      } finally {
        setBusy(false);
      }
    }

    function render() {
      const detail = state.detail;
      const metrics = state.metrics || {};
      $("versionCount").textContent = metrics.version_count || 0;
      $("auditCount").textContent = metrics.audit_count || 0;
      $("llmCount").textContent = metrics.llm_call_count || 0;

      if (!detail) {
        $("summaryOutput").textContent = "No run loaded.";
        $("versionsOutput").innerHTML = "";
        $("callsOutput").innerHTML = "";
        $("jsonOutput").textContent = "{}";
        return;
      }

      const summaryLines = [
        `Status: ${detail.status}`,
        `Trace OK: ${metrics.air_gap_trace_ok}`,
        `Latest needs polish: ${metrics.latest_needs_polish}`,
        "",
        "Current text:",
        detail.current_text,
      ];
      if (state.audit) {
        summaryLines.splice(
          3,
          0,
          `Last audit suggestions: ${state.audit.suggestions.length}`,
        );
      }
      if (state.final) {
        summaryLines.splice(3, 0, `Convergence: ${state.final.convergence_reason}`);
      }
      $("summaryOutput").textContent = summaryLines.join("\\n");

      $("versionsOutput").innerHTML = detail.versions.map((version) => `
        <div class="item">
          <strong>v${version.version_number} · ${version.source_step}</strong>
          <small>${version.created_at}</small>
          <pre>${escapeHtml(version.text)}</pre>
        </div>
      `).join("");

      $("callsOutput").innerHTML = detail.llm_calls.map((call) => `
        <div class="item">
          <strong>${call.prompt_type} · ${call.prompt_version}</strong>
          <small>${call.provider} · ${call.model_name || "mock"} · ${call.request_hash}</small>
          <pre>${escapeHtml(JSON.stringify({
            input_text_version_id: call.input_text_version_id,
            output_text_version_id: call.output_text_version_id,
            success: call.success,
            request_payload: call.request_payload,
            parsed_output: call.parsed_output,
            error: call.error,
          }, null, 2))}</pre>
        </div>
      `).join("");

      $("jsonOutput").textContent = JSON.stringify({ detail, metrics }, null, 2);
    }

    function escapeHtml(value) {
      return String(value).replace(/[&<>"']/g, (char) => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;",
      }[char]));
    }

    function activateTab(name) {
      document.querySelectorAll(".tab").forEach((button) => {
        button.classList.toggle("active", button.dataset.tab === name);
      });
      $("summaryTab").hidden = name !== "summary";
      $("versionsTab").hidden = name !== "versions";
      $("callsTab").hidden = name !== "calls";
      $("jsonTab").hidden = name !== "json";
    }

    document.querySelectorAll(".tab").forEach((button) => {
      button.addEventListener("click", () => activateTab(button.dataset.tab));
    });
    $("startBtn").addEventListener("click", startPipeline);
    $("auditBtn").addEventListener("click", auditPipeline);
    $("finalizeBtn").addEventListener("click", finalizePipeline);
    $("refreshBtn").addEventListener("click", refreshRun);

    requestJson("GET", "/health")
      .then((payload) => {
        $("health").textContent = `${payload.provider} · max ${payload.max_iterations}`;
      })
      .catch(() => {
        $("health").textContent = "health unavailable";
      });
  </script>
</body>
</html>
"""
