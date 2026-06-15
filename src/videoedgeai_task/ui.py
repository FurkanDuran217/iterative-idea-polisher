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

    .provider-heading {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      margin-bottom: 7px;
    }

    .provider-heading label {
      margin: 0;
    }

    .info-button {
      width: 28px;
      min-height: 28px;
      height: 28px;
      border: 1px solid #bfdbfe;
      border-radius: 50%;
      background: var(--blue);
      color: #ffffff;
      padding: 0;
      font-size: 14px;
      line-height: 26px;
      font-weight: 900;
      flex: 0 0 28px;
      box-shadow: 0 6px 14px rgba(37, 99, 235, 0.18);
    }

    .info-button:hover {
      border-color: #1d4ed8;
      background: #1d4ed8;
    }

    .provider-meta {
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
      margin-top: 9px;
    }

    .provider-summary {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #ffffff;
      color: var(--ink);
      font-size: 12px;
      line-height: 1.4;
      margin-top: 8px;
      padding: 9px 10px;
    }

    .provider-help {
      border: 1px solid #bfdbfe;
      border-radius: 8px;
      background: #eff6ff;
      margin-top: 10px;
      padding: 10px;
      color: #1e3a8a;
      font-size: 12px;
    }

    .provider-help.hidden {
      display: none;
    }

    .provider-help-title {
      display: flex;
      align-items: center;
      gap: 7px;
      color: #1d4ed8;
      font-weight: 850;
      margin-bottom: 7px;
    }

    .provider-help p {
      margin: 7px 0;
    }

    .provider-help ul {
      margin: 7px 0 0;
      padding-left: 18px;
    }

    .provider-help li + li {
      margin-top: 4px;
    }

    .help-mark {
      width: 18px;
      min-height: 18px;
      height: 18px;
      border-radius: 50%;
      background: var(--blue);
      color: #ffffff;
      display: inline-grid;
      place-items: center;
      font-size: 12px;
      line-height: 18px;
      font-weight: 900;
      flex: 0 0 18px;
    }

    code {
      border: 1px solid #cbd5e1;
      border-radius: 5px;
      background: #ffffff;
      color: #17202a;
      padding: 1px 4px;
      font-family: ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace;
      font-size: 12px;
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

    .report-output {
      min-height: 240px;
      max-height: 420px;
      overflow: auto;
      font-family: ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace;
      font-size: 12px;
      line-height: 1.55;
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
          <div class="provider-heading">
            <label>LLM Provider</label>
            <button
              class="info-button"
              id="providerInfoBtn"
              type="button"
              aria-expanded="false"
              aria-controls="providerHelp"
              title="Show provider setup help"
            >i</button>
          </div>
          <div class="segmented" role="radiogroup" aria-label="LLM provider">
            <label>
              <input type="radio" name="providerChoice" value="server" checked>
              <span>Server</span>
            </label>
            <label>
              <input type="radio" name="providerChoice" value="gemini">
              <span>Gemini</span>
            </label>
            <label>
              <input type="radio" name="providerChoice" value="openai">
              <span>GPT</span>
            </label>
            <label>
              <input type="radio" name="providerChoice" value="claude">
              <span>Claude</span>
            </label>
            <label>
              <input type="radio" name="providerChoice" value="ollama">
              <span>Ollama</span>
            </label>
            <label>
              <input type="radio" name="providerChoice" value="mock">
              <span>Mock</span>
            </label>
          </div>
          <div class="provider-meta" id="providerMeta">Server default provider</div>
          <div class="provider-summary" id="providerSummary">
            Server mode uses the backend default. With this local setup, that defaults to Gemini.
          </div>
          <div class="provider-help hidden" id="providerHelp">
            <div class="provider-help-title">
              <span class="help-mark">i</span>
              <span id="providerHelpTitle">How this provider is connected</span>
            </div>
            <div id="providerHelpBody"></div>
          </div>
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
          <h2>Review Score</h2>
          <span class="pill" id="reviewPill">not scored</span>
        </div>
        <div class="panel-body">
          <div class="metric-grid">
            <div class="metric"><b id="reviewQuality">-</b><span>Quality</span></div>
            <div class="metric"><b id="reviewDelta">-</b><span>Delta</span></div>
            <div class="metric"><b id="reviewStructure">-</b><span>Structure</span></div>
            <div class="metric"><b id="reviewFaithfulness">-</b><span>Faithfulness</span></div>
            <div class="metric"><b id="reviewActionability">-</b><span>Actionability</span></div>
          </div>
          <div class="verdict-card" style="margin-top: 10px;">
            <b id="reviewDecision">Not reviewed</b>
            <span id="reviewRationale">Run or load a pipeline to compare original and current text.</span>
          </div>
        </div>
      </section>

      <section>
        <div class="panel-header">
          <h2>Reviewer Report</h2>
          <button id="copyReportBtn" type="button">Copy Report</button>
        </div>
        <div class="panel-body">
          <div class="output report-output empty" id="reportText">
            Run or load a pipeline to generate a reviewer-ready report.
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
      review: null,
      report: null,
      audit: null,
      final: null,
      health: null,
      providerHelpOpen: false,
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
        "copyReportBtn",
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
      $("providerSummary").textContent = providerSummary(provider);
      $("providerFooter").textContent = "Provider: " + provider;
      updateProviderHelp(provider);
    }

    function providerSummary(provider) {
      const runtime = state.health?.provider || "loading";
      if (provider === "server") {
        return runtime === "gemini"
          ? "Recommended: no extra choice needed. Server mode uses the configured Gemini key."
          : `Server mode uses the backend default currently reported as ${runtime}.`;
      }
      if (provider === "gemini") {
        return $("geminiApiKey").value.trim()
          ? "This run will use the Gemini key entered here for this request only."
          : "This run will use the server Gemini key if present; paste another key only to override it.";
      }
      if (provider === "openai") {
        return "Use GPT or an OpenAI-compatible gateway by entering base URL, key, and model.";
      }
      if (provider === "claude") {
        return "Use Claude by entering an Anthropic API key and an enabled model name.";
      }
      if (provider === "ollama") {
        return "Use a local model when Ollama is running and the selected model is pulled.";
      }
      return "Use mock for deterministic offline demos, CI, and baseline comparison.";
    }

    function updateProviderHelp(provider) {
      const help = {
        server: {
          title: "Server default: zero-click Gemini path",
          body: `
            <p>Use this for the simplest reviewer path. The backend reads local <code>.env</code> when it starts.</p>
            <ul>
              <li>Keep <code>LLM_PROVIDER</code> empty and set <code>GEMINI_API_KEY</code>; no-selection runs use Gemini automatically.</li>
              <li>The top-right runtime pill shows the active backend provider after the page loads.</li>
              <li>If no real key exists, backend falls back to <code>mock</code> so the demo always runs.</li>
              <li>For handoff: put keys in <code>.env</code>, never in GitHub, screenshots, logs, or source files.</li>
            </ul>
          `,
        },
        gemini: {
          title: "Gemini: Google AI Studio key",
          body: `
            <p>Get a key from <code>https://aistudio.google.com/app/apikey</code>.</p>
            <ul>
              <li>Personal override: paste the key into <strong>Gemini API Key</strong> below and run the pipeline.</li>
              <li>Shared default: add <code>GEMINI_API_KEY=...</code> to local <code>.env</code>, leave <code>LLM_PROVIDER</code> empty, then restart uvicorn.</li>
              <li>Model field can stay <code>gemini-2.0-flash</code>; change it only if your key/project supports another model.</li>
              <li><code>401 Unauthorized</code>: invalid key, restricted key, copied whitespace, or API not enabled.</li>
              <li><code>429 quota</code>: key is recognized, but the Google project has no available quota for that model.</li>
            </ul>
          `,
        },
        openai: {
          title: "GPT: OpenAI API key",
          body: `
            <p>Create a key from <code>https://platform.openai.com/api-keys</code>.</p>
            <ul>
              <li>Paste it into <strong>API Key</strong>, keep base URL as <code>https://api.openai.com/v1</code>, and choose a model.</li>
              <li>Server env option: <code>OPENAI_API_KEY=...</code>, <code>LLM_PROVIDER=openai</code>, <code>OPENAI_MODEL=gpt-4.1-mini</code>.</li>
              <li>For OpenAI-compatible gateways, use their base URL and model name; keep the same fields.</li>
            </ul>
          `,
        },
        claude: {
          title: "Claude: Anthropic Console key",
          body: `
            <p>Create a key from <code>https://console.anthropic.com/settings/keys</code>.</p>
            <ul>
              <li>Paste it into <strong>Anthropic API Key</strong>, keep base URL as <code>https://api.anthropic.com</code>.</li>
              <li>Server env option: <code>ANTHROPIC_API_KEY=...</code>, <code>LLM_PROVIDER=claude</code>, <code>ANTHROPIC_MODEL=claude-sonnet-4-5</code>.</li>
              <li>If your account has a different model entitlement, replace the model field before running.</li>
            </ul>
          `,
        },
        ollama: {
          title: "Ollama: free local model",
          body: `
            <p>Use this when you want a real LLM without paid API keys.</p>
            <ul>
              <li>Install Ollama, then run <code>ollama pull llama3.2:3b</code>.</li>
              <li>Keep Ollama running; the API should answer at <code>http://127.0.0.1:11434</code>.</li>
              <li>Leave model as <code>llama3.2:3b</code> unless you pulled a different local model.</li>
            </ul>
          `,
        },
        mock: {
          title: "Mock: deterministic offline baseline",
          body: `
            <p>Use this for repeatable grading, tests, and demos when no model is available.</p>
            <ul>
              <li>No key, internet, or local model is required.</li>
              <li>It proves API flow, persistence, traceability, and metrics; it is not a real quality judge.</li>
              <li>Compare it with Ollama/Gemini/GPT/Claude runs to discuss real model behavior.</li>
            </ul>
          `,
        },
      };
      const selected = help[provider] || help.mock;
      $("providerHelpTitle").textContent = selected.title;
      $("providerHelpBody").innerHTML = selected.body;
      renderProviderHelp();
    }

    function toggleProviderHelp() {
      state.providerHelpOpen = !state.providerHelpOpen;
      renderProviderHelp();
    }

    function renderProviderHelp() {
      $("providerHelp").className = state.providerHelpOpen
        ? "provider-help"
        : "provider-help hidden";
      $("providerInfoBtn").setAttribute("aria-expanded", String(state.providerHelpOpen));
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
      state.review = await requestJson("GET", `/api/v1/pipeline/${id}/review`);
      state.report = await requestJson("GET", `/api/v1/pipeline/${id}/report`);
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
      state.review = null;
      state.report = null;
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
        setNotice(friendlyError(error.message), true);
      } finally {
        setBusy(false);
      }
    }

    function friendlyError(message) {
      const text = String(message || "Request failed.");
      if (text.includes("429")) {
        return "Provider quota is exhausted or not enabled for this model. Try Mock, Ollama, another model, or update the provider billing/quota.";
      }
      if (text.includes("401") || text.toLowerCase().includes("unauthorized")) {
        return "Provider key was rejected. Check the API key, project restrictions, and whether the API is enabled.";
      }
      if (text.toLowerCase().includes("ollama")) {
        return "Ollama is not reachable. Start Ollama, pull the selected model, then retry.";
      }
      if (text.toLowerCase().includes("connection") || text.toLowerCase().includes("network")) {
        return "Provider connection failed. Check network access, base URL, and provider availability.";
      }
      return text.length > 220 ? `${text.slice(0, 220).trim()}...` : text;
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
      const review = state.review;
      const report = state.report;
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
      renderReview(review);
      renderReport(report);
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

    function renderReview(review) {
      if (!review) {
        $("reviewQuality").textContent = "-";
        $("reviewDelta").textContent = "-";
        $("reviewStructure").textContent = "-";
        $("reviewFaithfulness").textContent = "-";
        $("reviewActionability").textContent = "-";
        $("reviewPill").textContent = "not scored";
        $("reviewPill").className = "pill";
        $("reviewDecision").textContent = "Not reviewed";
        $("reviewRationale").textContent = "Run or load a pipeline to compare original and current text.";
        return;
      }
      const score = review.current_score || {};
      $("reviewQuality").textContent = formatScore(score.quality_proxy_score);
      $("reviewDelta").textContent = formatSigned(review.quality_delta);
      $("reviewStructure").textContent = formatPercent(score.structure_coverage);
      $("reviewFaithfulness").textContent = formatPercent(score.faithfulness_recall);
      $("reviewActionability").textContent = formatScore(score.actionability_score);
      $("reviewPill").textContent = review.likely_better_than_original ? "likely better" : "needs review";
      $("reviewPill").className = review.likely_better_than_original ? "pill ok" : "pill warn";
      $("reviewDecision").textContent = review.likely_better_than_original
        ? "Likely better than original"
        : "No clear rubric lift";
      $("reviewRationale").textContent = review.decision_rationale;
    }

    function renderReport(report) {
      const output = $("reportText");
      if (!report) {
        output.textContent = "Run or load a pipeline to generate a reviewer-ready report.";
        output.className = "output report-output empty";
        return;
      }
      output.textContent = report.markdown;
      output.className = "output report-output";
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

    function formatScore(value) {
      return Number.isFinite(Number(value)) ? Number(value).toFixed(2) : "-";
    }

    function formatSigned(value) {
      if (!Number.isFinite(Number(value))) {
        return "-";
      }
      const number = Number(value);
      return `${number > 0 ? "+" : ""}${number.toFixed(2)}`;
    }

    function formatPercent(value) {
      return Number.isFinite(Number(value)) ? `${Math.round(Number(value) * 100)}%` : "-";
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

    async function copyReport() {
      if (!state.report?.markdown) {
        setNotice("No report to copy.", true);
        return;
      }
      try {
        await navigator.clipboard.writeText(state.report.markdown);
        setNotice("Reviewer report copied.");
      } catch {
        setNotice("Copy failed. Select the report text manually.", true);
      }
    }

    $("runFullBtn").addEventListener("click", runFullPipeline);
    $("startBtn").addEventListener("click", startOnly);
    $("auditBtn").addEventListener("click", auditRun);
    $("finalizeBtn").addEventListener("click", finalizeRun);
    $("refreshBtn").addEventListener("click", refreshRun);
    $("copyReportBtn").addEventListener("click", copyReport);
    $("resetBtn").addEventListener("click", resetUi);
    $("providerInfoBtn").addEventListener("click", toggleProviderHelp);
    document.querySelectorAll('input[name="providerChoice"]').forEach((input) => {
      input.addEventListener("change", updateProviderUi);
    });
    [
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
      $(id).addEventListener("input", updateProviderUi);
    });

    requestJson("GET", "/health")
      .then((payload) => {
        state.health = payload;
        $("healthPill").textContent = `${payload.provider} - max ${payload.max_iterations}`;
        $("healthPill").className = "pill ok";
        updateProviderUi();
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
