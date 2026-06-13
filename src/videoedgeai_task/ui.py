from __future__ import annotations

# ruff: noqa: E501

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
      --bg: #eef2f5;
      --panel: #ffffff;
      --panel-soft: #f8fafc;
      --ink: #17202a;
      --muted: #64748b;
      --line: #d8e0ea;
      --teal: #0f766e;
      --teal-dark: #115e59;
      --blue: #2563eb;
      --amber: #b45309;
      --red: #b91c1c;
      --ok-bg: #ecfdf5;
      --warn-bg: #fff7ed;
      --shadow: 0 16px 34px rgba(30, 41, 59, 0.08);
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
        "Segoe UI", sans-serif;
      line-height: 1.45;
    }

    header {
      background: var(--panel);
      border-bottom: 1px solid var(--line);
    }

    .topbar,
    main {
      width: min(1240px, calc(100% - 32px));
      margin: 0 auto;
    }

    .topbar {
      min-height: 70px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 18px;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .mark {
      width: 36px;
      height: 36px;
      border-radius: 8px;
      background: var(--teal);
      color: white;
      display: grid;
      place-items: center;
      font-weight: 800;
    }

    h1 {
      margin: 0;
      font-size: 22px;
      font-weight: 760;
      letter-spacing: 0;
    }

    .subline {
      color: var(--muted);
      font-size: 13px;
      margin-top: 2px;
    }

    .pill {
      min-height: 30px;
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 5px 10px;
      background: var(--panel-soft);
      color: var(--muted);
      display: inline-flex;
      align-items: center;
      gap: 8px;
      font-size: 13px;
      font-weight: 650;
      white-space: nowrap;
    }

    .pill.ok {
      color: var(--teal-dark);
      background: var(--ok-bg);
      border-color: #a7f3d0;
    }

    .pill.warn {
      color: var(--amber);
      background: var(--warn-bg);
      border-color: #fed7aa;
    }

    main {
      padding: 22px 0 36px;
      display: grid;
      grid-template-columns: minmax(310px, 380px) minmax(0, 1fr);
      gap: 18px;
      align-items: start;
    }

    section {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: var(--shadow);
      min-width: 0;
    }

    .panel-header {
      padding: 14px 16px;
      border-bottom: 1px solid var(--line);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
    }

    h2,
    h3 {
      margin: 0;
      font-size: 15px;
      font-weight: 740;
      letter-spacing: 0;
    }

    .panel-body {
      padding: 16px;
    }

    .control-panel {
      position: sticky;
      top: 16px;
    }

    label {
      display: block;
      color: var(--muted);
      font-size: 13px;
      font-weight: 700;
      margin-bottom: 7px;
    }

    textarea,
    input {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 7px;
      background: #ffffff;
      color: var(--ink);
      font: inherit;
      outline: none;
    }

    textarea {
      min-height: 170px;
      resize: vertical;
      padding: 12px;
    }

    input {
      min-height: 40px;
      padding: 0 10px;
      font-size: 13px;
    }

    textarea:focus,
    input:focus {
      border-color: var(--teal);
      box-shadow: 0 0 0 3px rgba(15, 118, 110, 0.14);
    }

    .provider-card {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel-soft);
      padding: 12px;
    }

    .segmented {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 6px;
    }

    .segmented label {
      margin: 0;
      cursor: pointer;
    }

    .segmented input {
      position: absolute;
      opacity: 0;
      pointer-events: none;
    }

    .segmented span {
      min-height: 38px;
      border: 1px solid var(--line);
      border-radius: 7px;
      background: #ffffff;
      color: var(--muted);
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      font-size: 13px;
      font-weight: 800;
    }

    .segmented input:checked + span {
      background: var(--teal);
      border-color: var(--teal);
      color: #ffffff;
    }

    .info-dot {
      width: 18px;
      min-height: 18px;
      height: 18px;
      border: 0;
      border-radius: 50%;
      background: var(--blue);
      color: #ffffff;
      padding: 0;
      font-size: 12px;
      line-height: 18px;
      font-weight: 900;
    }

    .provider-meta {
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
      margin-top: 9px;
    }

    .provider-options {
      display: grid;
      gap: 10px;
      margin-top: 12px;
    }

    .provider-options.hidden {
      display: none;
    }

    .field + .field,
    .field + .button-stack,
    .button-stack + .field {
      margin-top: 14px;
    }

    .button-stack {
      display: grid;
      gap: 8px;
    }

    .button-row {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 8px;
    }

    button {
      min-height: 40px;
      border-radius: 7px;
      border: 1px solid var(--line);
      background: #ffffff;
      color: var(--ink);
      cursor: pointer;
      font: inherit;
      font-size: 14px;
      font-weight: 760;
    }

    button.primary {
      background: var(--teal);
      border-color: var(--teal);
      color: white;
    }

    button.secondary {
      border-color: #bfdbfe;
      color: var(--blue);
      background: #eff6ff;
    }

    button:hover {
      border-color: var(--teal-dark);
    }

    button:disabled {
      opacity: 0.55;
      cursor: not-allowed;
    }

    .workflow {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 8px;
      margin-bottom: 14px;
    }

    .step {
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 9px 10px;
      min-height: 64px;
      background: var(--panel-soft);
    }

    .step b {
      display: block;
      font-size: 18px;
      line-height: 1;
    }

    .step span {
      display: block;
      margin-top: 8px;
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
    }

    .step.done {
      border-color: #99f6e4;
      background: #f0fdfa;
    }

    .step.active {
      border-color: #fbbf24;
      background: #fffbeb;
    }

    .notice {
      min-height: 34px;
      margin-top: 12px;
      padding: 8px 10px;
      border-radius: 7px;
      background: var(--panel-soft);
      border: 1px solid var(--line);
      color: var(--muted);
      font-size: 13px;
    }

    .notice.error {
      color: var(--red);
      background: #fef2f2;
      border-color: #fecaca;
    }

    .content-stack {
      display: grid;
      gap: 18px;
    }

    .result-layout {
      display: grid;
      grid-template-columns: minmax(0, 1.15fr) minmax(250px, 0.85fr);
      gap: 14px;
    }

    .output {
      min-height: 312px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fbfdff;
      padding: 14px;
      white-space: pre-wrap;
      overflow-wrap: anywhere;
      font-size: 14px;
    }

    .empty {
      color: var(--muted);
    }

    .suggestions {
      display: grid;
      gap: 8px;
    }

    .verdict-card {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel-soft);
      padding: 12px;
      margin-bottom: 10px;
    }

    .verdict-card b {
      display: block;
      font-size: 20px;
      line-height: 1.1;
    }

    .verdict-card span {
      display: block;
      margin-top: 7px;
      color: var(--muted);
      font-size: 13px;
    }

    .suggestion {
      border: 1px solid var(--line);
      border-left: 4px solid var(--amber);
      border-radius: 8px;
      padding: 10px;
      background: #fffdf8;
      font-size: 13px;
    }

    .metric-grid {
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 8px;
    }

    .metric {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel-soft);
      padding: 10px;
      min-height: 72px;
    }

    .metric b {
      display: block;
      font-size: 20px;
      line-height: 1.1;
      overflow-wrap: anywhere;
    }

    .metric span {
      display: block;
      margin-top: 7px;
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
    }

    .trace-list {
      display: grid;
      gap: 8px;
    }

    .trace-item {
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 10px;
      background: #ffffff;
    }

    .trace-top {
      display: grid;
      grid-template-columns: 82px 88px 110px 1fr 80px;
      gap: 10px;
      align-items: center;
      font-size: 13px;
    }

    .trace-type {
      font-weight: 800;
      text-transform: uppercase;
      color: var(--teal-dark);
    }

    .trace-hash {
      color: var(--muted);
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    details {
      margin-top: 8px;
    }

    summary {
      cursor: pointer;
      color: var(--blue);
      font-size: 13px;
      font-weight: 700;
    }

    pre {
      margin: 8px 0 0;
      border: 1px solid var(--line);
      border-radius: 7px;
      background: #f8fafc;
      padding: 10px;
      max-height: 300px;
      overflow: auto;
      white-space: pre-wrap;
      overflow-wrap: anywhere;
      font-size: 12px;
    }

    .footer-row {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: center;
      color: var(--muted);
      font-size: 12px;
    }

    @media (max-width: 980px) {
      main,
      .result-layout {
        grid-template-columns: 1fr;
      }

      .control-panel {
        position: static;
      }
    }

    @media (max-width: 680px) {
      .topbar {
        align-items: flex-start;
        flex-direction: column;
        padding: 14px 0;
      }

      main,
      .topbar {
        width: min(100% - 20px, 1240px);
      }

      .workflow,
      .metric-grid,
      .button-row,
      .trace-top {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>
<body>
  <header>
    <div class="topbar">
      <div class="brand">
        <div class="mark">VE</div>
        <div>
          <h1>VideoEdgeAI-Task</h1>
          <div class="subline">Iterative Idea Polisher reviewer console</div>
        </div>
      </div>
      <span class="pill" id="healthPill">checking runtime</span>
    </div>
  </header>

  <main>
    <section class="control-panel">
      <div class="panel-header">
        <h2>Run Control</h2>
        <span class="pill" id="runStatus">idle</span>
      </div>
      <div class="panel-body">
        <div class="workflow">
          <div class="step" id="stepStart"><b>1</b><span>Start</span></div>
          <div class="step" id="stepAudit"><b>2</b><span>Audit</span></div>
          <div class="step" id="stepFinal"><b>3</b><span>Finalize</span></div>
        </div>

        <div class="field">
          <label for="ideaText">Idea</label>
          <textarea id="ideaText">make notes better for founders</textarea>
        </div>

        <div class="field provider-card">
          <label>LLM Provider</label>
          <div class="segmented" role="radiogroup" aria-label="LLM provider">
            <label>
              <input type="radio" name="providerChoice" value="server" checked>
              <span>Server <button class="info-dot" type="button" title="Uses server env. If GEMINI_API_KEY exists, Gemini is the default; otherwise Mock is used.">i</button></span>
            </label>
            <label>
              <input type="radio" name="providerChoice" value="gemini">
              <span>Gemini <button class="info-dot" type="button" title="Get a key from Google AI Studio and paste it below, or set GEMINI_API_KEY in .env.">i</button></span>
            </label>
            <label>
              <input type="radio" name="providerChoice" value="openai">
              <span>GPT <button class="info-dot" type="button" title="Create an OpenAI API key and paste it below, or set OPENAI_API_KEY in .env.">i</button></span>
            </label>
            <label>
              <input type="radio" name="providerChoice" value="claude">
              <span>Claude <button class="info-dot" type="button" title="Create an Anthropic Console API key and paste it below, or set ANTHROPIC_API_KEY in .env.">i</button></span>
            </label>
            <label>
              <input type="radio" name="providerChoice" value="ollama">
              <span>Ollama <button class="info-dot" type="button" title="Install Ollama, pull a model such as llama3.2:3b, and keep it running on 127.0.0.1:11434.">i</button></span>
            </label>
            <label>
              <input type="radio" name="providerChoice" value="mock">
              <span>Mock <button class="info-dot" type="button" title="Deterministic offline provider for tests and demos.">i</button></span>
            </label>
          </div>
          <div class="provider-meta" id="providerMeta">Server default provider</div>
          <div class="provider-options hidden" id="geminiOptions">
            <div class="field">
              <label for="geminiApiKey">Gemini API Key</label>
              <input id="geminiApiKey" type="password" autocomplete="off" spellcheck="false">
            </div>
            <div class="field">
              <label for="geminiModel">Gemini Model</label>
              <input id="geminiModel" autocomplete="off" spellcheck="false" value="gemini-2.0-flash">
            </div>
            <div class="field">
              <label for="geminiBaseUrl">Gemini Base URL</label>
              <input id="geminiBaseUrl" autocomplete="off" spellcheck="false" value="https://generativelanguage.googleapis.com">
            </div>
          </div>
          <div class="provider-options hidden" id="claudeOptions">
            <div class="field">
              <label for="anthropicApiKey">Anthropic API Key</label>
              <input id="anthropicApiKey" type="password" autocomplete="off" spellcheck="false">
            </div>
            <div class="field">
              <label for="anthropicModel">Claude Model</label>
              <input id="anthropicModel" autocomplete="off" spellcheck="false" value="claude-sonnet-4-5">
            </div>
            <div class="field">
              <label for="anthropicBaseUrl">Claude Base URL</label>
              <input id="anthropicBaseUrl" autocomplete="off" spellcheck="false" value="https://api.anthropic.com">
            </div>
          </div>
          <div class="provider-options hidden" id="ollamaOptions">
            <div class="field">
              <label for="ollamaBaseUrl">Ollama Base URL</label>
              <input id="ollamaBaseUrl" autocomplete="off" spellcheck="false" value="http://127.0.0.1:11434">
            </div>
            <div class="field">
              <label for="ollamaModel">Ollama Model</label>
              <input id="ollamaModel" autocomplete="off" spellcheck="false" value="llama3.2:3b">
            </div>
          </div>
          <div class="provider-options hidden" id="openaiOptions">
            <div class="field">
              <label for="openaiBaseUrl">API Base URL</label>
              <input id="openaiBaseUrl" autocomplete="off" spellcheck="false" value="https://api.openai.com/v1">
            </div>
            <div class="field">
              <label for="openaiApiKey">API Key</label>
              <input id="openaiApiKey" type="password" autocomplete="off" spellcheck="false">
            </div>
            <div class="field">
              <label for="openaiModel">Model</label>
              <input id="openaiModel" autocomplete="off" spellcheck="false" value="gpt-4.1-mini">
            </div>
          </div>
        </div>

        <div class="button-stack">
          <button class="primary" id="runFullBtn" type="button">Run Full Pipeline</button>
          <div class="button-row">
            <button id="startBtn" type="button">Start</button>
            <button id="auditBtn" type="button">Audit</button>
          </div>
          <div class="button-row">
            <button id="finalizeBtn" type="button">Finalize</button>
            <button class="secondary" id="resetBtn" type="button">Reset</button>
          </div>
        </div>

        <div class="field">
          <label for="trackingId">Tracking ID</label>
          <input id="trackingId" autocomplete="off" spellcheck="false">
        </div>

        <div id="notice" class="notice" aria-live="polite">Ready.</div>
      </div>
    </section>

    <div class="content-stack">
      <section>
        <div class="panel-header">
          <h2>Current / Final Text</h2>
          <span class="pill" id="convergencePill">not run</span>
        </div>
        <div class="panel-body">
          <div class="result-layout">
            <div>
              <div class="output empty" id="outputText">
                Run the pipeline to see the polished text.
              </div>
            </div>
            <div>
              <h3>Fresh Audit Verdict</h3>
              <div class="verdict-card" id="verdictCard" style="margin-top: 10px;">
                <b id="verdictLabel">Not audited</b>
                <span id="verdictRationale">Run audit or full pipeline to get a verdict.</span>
              </div>
              <h3>Audit Suggestions</h3>
              <div class="suggestions" id="suggestionsList" style="margin-top: 10px;"></div>
            </div>
          </div>
        </div>
      </section>

      <section>
        <div class="panel-header">
          <h2>Run Metrics</h2>
          <span class="pill" id="tracePill">trace pending</span>
        </div>
        <div class="panel-body">
          <div class="metric-grid">
            <div class="metric"><b id="metricStatus">-</b><span>Status</span></div>
            <div class="metric"><b id="metricVersions">0</b><span>Versions</span></div>
            <div class="metric"><b id="metricAudits">0</b><span>Audits</span></div>
            <div class="metric"><b id="metricCalls">0</b><span>LLM Calls</span></div>
            <div class="metric"><b id="metricWords">0</b><span>Word Delta</span></div>
          </div>
        </div>
      </section>

      <section>
        <div class="panel-header">
          <h2>LLM Trace</h2>
          <button id="refreshBtn" type="button">Refresh</button>
        </div>
        <div class="panel-body">
          <div class="trace-list" id="traceList"></div>
        </div>
      </section>

      <div class="footer-row">
        <span id="lastAction">No run loaded.</span>
        <span id="providerFooter">Provider: mock</span>
      </div>
    </div>
  </main>

  <script>
    const state = {
      detail: null,
      metrics: null,
      audit: null,
      final: null,
    };

    const $ = (id) => document.getElementById(id);

    function setNotice(message, isError = false) {
      const notice = $("notice");
      notice.textContent = message;
      notice.className = isError ? "notice error" : "notice";
    }

    function setBusy(isBusy) {
      [
        "runFullBtn",
        "startBtn",
        "auditBtn",
        "finalizeBtn",
        "refreshBtn",
        "resetBtn",
        "geminiApiKey",
        "geminiModel",
        "geminiBaseUrl",
        "anthropicApiKey",
        "anthropicModel",
        "anthropicBaseUrl",
        "ollamaBaseUrl",
        "ollamaModel",
        "openaiBaseUrl",
        "openaiApiKey",
        "openaiModel",
      ].forEach((id) => {
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

    function selectedProvider() {
      const selected = document.querySelector('input[name="providerChoice"]:checked');
      return selected ? selected.value : "mock";
    }

    function providerPayload() {
      const provider = selectedProvider();
      if (provider === "server") {
        return { provider: "server" };
      }
      if (provider === "mock") {
        return { provider: "mock" };
      }

      if (provider === "gemini") {
        return {
          provider: "gemini",
          gemini_api_key: $("geminiApiKey").value.trim(),
          gemini_model: $("geminiModel").value.trim() || "gemini-2.0-flash",
          gemini_base_url:
            $("geminiBaseUrl").value.trim() || "https://generativelanguage.googleapis.com",
        };
      }

      if (provider === "claude") {
        return {
          provider: "claude",
          anthropic_api_key: $("anthropicApiKey").value.trim(),
          anthropic_model: $("anthropicModel").value.trim() || "claude-sonnet-4-5",
          anthropic_base_url: $("anthropicBaseUrl").value.trim() || "https://api.anthropic.com",
        };
      }

      if (provider === "ollama") {
        return {
          provider: "ollama",
          ollama_base_url: $("ollamaBaseUrl").value.trim() || "http://127.0.0.1:11434",
          ollama_model: $("ollamaModel").value.trim() || "llama3.2:3b",
        };
      }

      const baseUrl = $("openaiBaseUrl").value.trim().replace(/[/]+$/, "")
        || "https://api.openai.com/v1";
      const key = $("openaiApiKey").value.trim();
      const model = $("openaiModel").value.trim();
      if (!model) {
        throw new Error("Model required.");
      }
      return {
        provider: "openai",
        openai_api_key: key,
        openai_base_url: baseUrl,
        openai_model: model,
      };
    }

    function updateProviderUi() {
      const provider = selectedProvider();
      const isOllama = provider === "ollama";
      const isGemini = provider === "gemini";
      const isClaude = provider === "claude";
      const isApi = provider === "openai";
      $("geminiOptions").className = isGemini ? "provider-options" : "provider-options hidden";
      $("claudeOptions").className = isClaude ? "provider-options" : "provider-options hidden";
      $("ollamaOptions").className = isOllama ? "provider-options" : "provider-options hidden";
      $("openaiOptions").className = isApi ? "provider-options" : "provider-options hidden";
      $("providerMeta").textContent = isGemini
        ? "Google Gemini API"
        : isClaude
          ? "Anthropic Claude API"
          : isOllama
            ? "Local free model through Ollama"
            : isApi
              ? "OpenAI GPT API"
              : provider === "server"
                ? "Server default provider"
                : "Deterministic local provider";
      $("providerFooter").textContent = "Provider: " + provider;
    }

    async function startRun() {
      const text = $("ideaText").value;
      const payload = await requestJson("POST", "/api/v1/pipeline/start", { text });
      $("trackingId").value = payload.tracking_id;
      state.audit = null;
      state.final = null;
      await loadRun();
      return payload.tracking_id;
    }

    async function startOnly() {
      await withBusy(async () => {
        const id = await startRun();
        setNotice("Started " + id);
      });
    }

    async function auditRun() {
      await withBusy(async () => {
        const id = requireTrackingId();
        state.audit = await requestJson("POST", `/api/v1/pipeline/audit/${id}`, providerPayload());
        await loadRun();
        setNotice("Audit complete.");
      });
    }

    async function finalizeRun() {
      await withBusy(async () => {
        const id = requireTrackingId();
        state.final = await requestJson(
          "POST",
          `/api/v1/pipeline/finalize/${id}`,
          providerPayload(),
        );
        await loadRun();
        setNotice("Finalize complete.");
      });
    }

    async function runFullPipeline() {
      await withBusy(async () => {
        const actionPayload = providerPayload();
        const id = await startRun();
        state.final = await requestJson(
          "POST",
          `/api/v1/pipeline/finalize/${id}`,
          actionPayload,
        );
        await loadRun();
        setNotice("Pipeline complete.");
      });
    }

    async function loadRun() {
      const id = trackingId();
      if (!id) {
        render();
        return;
      }
      state.detail = await requestJson("GET", `/api/v1/pipeline/${id}`);
      state.metrics = await requestJson("GET", `/api/v1/pipeline/${id}/metrics`);
      $("lastAction").textContent = "Loaded " + id;
      render();
    }

    async function refreshRun() {
      await withBusy(async () => {
        await loadRun();
        setNotice(trackingId() ? "Run refreshed." : "No tracking ID.");
      });
    }

    function resetUi() {
      $("trackingId").value = "";
      state.detail = null;
      state.metrics = null;
      state.audit = null;
      state.final = null;
      $("lastAction").textContent = "No run loaded.";
      setNotice("Ready.");
      render();
    }

    async function withBusy(task) {
      setBusy(true);
      try {
        await task();
      } catch (error) {
        setNotice(error.message, true);
      } finally {
        setBusy(false);
      }
    }

    function requireTrackingId() {
      const id = trackingId();
      if (!id) {
        throw new Error("Tracking ID required.");
      }
      return id;
    }

    function render() {
      const detail = state.detail;
      const metrics = state.metrics || {};
      const loaded = Boolean(detail);
      const audits = loaded ? detail.audits : [];
      const calls = loaded ? detail.llm_calls : [];
      const latestAudit = audits.length ? audits[audits.length - 1] : null;
      const verdict = currentVerdict(metrics, calls);
      const suggestions = verdict?.suggestions?.length
        ? verdict.suggestions
        : latestAudit?.suggestions || [];

      $("runStatus").textContent = loaded ? detail.status : "idle";
      $("metricStatus").textContent = loaded ? detail.status : "-";
      $("metricVersions").textContent = metrics.version_count || 0;
      $("metricAudits").textContent = metrics.audit_count || 0;
      $("metricCalls").textContent = metrics.llm_call_count || 0;
      $("metricWords").textContent = metrics.word_delta || 0;

      const traceOk = Boolean(metrics.air_gap_trace_ok);
      $("tracePill").textContent = traceOk ? "trace OK" : "trace pending";
      $("tracePill").className = traceOk ? "pill ok" : "pill warn";

      const convergence = state.final?.convergence_reason || "not run";
      $("convergencePill").textContent = verdict?.is_perfect
        ? "declared perfect"
        : convergence;
      $("convergencePill").className =
        verdict?.is_perfect || convergence === "declared_perfect" ? "pill ok" : "pill";

      renderWorkflow(loaded, audits.length, detail?.status);
      renderOutput(detail);
      renderVerdict(verdict);
      renderSuggestions(suggestions);
      renderTrace(calls);
    }

    function currentVerdict(metrics, calls) {
      for (let index = calls.length - 1; index >= 0; index -= 1) {
        const call = calls[index];
        if (call.prompt_type !== "audit" || !call.success || !call.parsed_output) {
          continue;
        }
        return call.parsed_output;
      }
      if (metrics.latest_is_perfect !== null && metrics.latest_is_perfect !== undefined) {
        return {
          is_perfect: metrics.latest_is_perfect,
          quality_score: metrics.latest_quality_score,
          rationale: metrics.latest_rationale,
          suggestions: state.audit?.suggestions || [],
        };
      }
      return null;
    }

    function renderWorkflow(loaded, auditCount, status) {
      $("stepStart").className = loaded ? "step done" : "step active";
      $("stepAudit").className = auditCount ? "step done" : loaded ? "step active" : "step";
      $("stepFinal").className = status === "completed"
        ? "step done"
        : auditCount
          ? "step active"
          : "step";
    }

    function renderOutput(detail) {
      const output = $("outputText");
      if (!detail) {
        output.textContent = "Run the pipeline to see the polished text.";
        output.className = "output empty";
        return;
      }
      output.textContent = detail.current_text;
      output.className = "output";
    }

    function renderVerdict(verdict) {
      const label = $("verdictLabel");
      const rationale = $("verdictRationale");
      if (!verdict) {
        label.textContent = "Not audited";
        rationale.textContent = "Run audit or full pipeline to get a verdict.";
        return;
      }
      const score = verdict.quality_score ?? "-";
      label.textContent = verdict.is_perfect
        ? `Perfect - ${score}/100`
        : `Needs polish - ${score}/100`;
      rationale.textContent = verdict.rationale || "No rationale returned.";
    }

    function renderSuggestions(suggestions) {
      const list = $("suggestionsList");
      if (!suggestions.length) {
        list.innerHTML = '<div class="suggestion">No active suggestions.</div>';
        return;
      }
      list.innerHTML = suggestions.map((suggestion, index) => `
        <div class="suggestion">
          <strong>${index + 1}.</strong> ${escapeHtml(suggestion)}
        </div>
      `).join("");
    }

    function renderTrace(calls) {
      const list = $("traceList");
      if (!calls.length) {
        list.innerHTML = '<div class="trace-item empty">No LLM calls recorded.</div>';
        return;
      }
      list.innerHTML = calls.map((call) => `
        <div class="trace-item">
          <div class="trace-top">
            <div class="trace-type">${escapeHtml(call.prompt_type)}</div>
            <div>${escapeHtml(call.provider)}</div>
            <div>${escapeHtml(call.prompt_version)}</div>
            <div class="trace-hash">${escapeHtml(call.request_hash)}</div>
            <div>${call.success ? "success" : "failed"}</div>
          </div>
          <details>
            <summary>Payload and parsed output</summary>
            <pre>${escapeHtml(JSON.stringify({
              input_text_version_id: call.input_text_version_id,
              output_text_version_id: call.output_text_version_id,
              model_name: call.model_name,
              provider_params: call.provider_params,
              request_payload: call.request_payload,
              parsed_output: call.parsed_output,
              error: call.error,
            }, null, 2))}</pre>
          </details>
        </div>
      `).join("");
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

    $("runFullBtn").addEventListener("click", runFullPipeline);
    $("startBtn").addEventListener("click", startOnly);
    $("auditBtn").addEventListener("click", auditRun);
    $("finalizeBtn").addEventListener("click", finalizeRun);
    $("refreshBtn").addEventListener("click", refreshRun);
    $("resetBtn").addEventListener("click", resetUi);
    document.querySelectorAll('input[name="providerChoice"]').forEach((input) => {
      input.addEventListener("change", updateProviderUi);
    });

    requestJson("GET", "/health")
      .then((payload) => {
        $("healthPill").textContent = `${payload.provider} - max ${payload.max_iterations}`;
        $("healthPill").className = "pill ok";
      })
      .catch(() => {
        $("healthPill").textContent = "runtime unavailable";
        $("healthPill").className = "pill warn";
      });

    updateProviderUi();
    const initialTrackingId = new URLSearchParams(window.location.search).get("tracking_id");
    if (initialTrackingId) {
      $("trackingId").value = initialTrackingId;
      refreshRun();
    } else {
      render();
    }
  </script>
</body>
</html>
"""
