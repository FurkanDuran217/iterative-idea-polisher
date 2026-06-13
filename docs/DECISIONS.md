# Architecture Decisions

## 1. Store State, Not Conversation

Each LLM call receives only the current text and the immediate suggestions it needs. Conversation
history is never passed to the provider. The database stores continuity through `tracking_id`,
versions, audits, and call records.

## 2. Real Provider When Configured, Mock When Not

If `GEMINI_API_KEY` exists and `LLM_PROVIDER` is not explicitly set, the server defaults to Gemini
so the reviewer can test with a real hosted model immediately. If no real key exists, the
deterministic mock provider remains available so the workflow, tests, and traceability can still be
reviewed without credentials. Gemini, GPT/OpenAI, Claude, Ollama, and OpenAI-compatible adapters
all sit behind the same provider interface.

## 3. Persist LLM Calls

Every LLM call stores provider, prompt type, request hash, raw output, parsed output, latency, and
success/error status. This makes the air-gap behavior inspectable instead of merely asserted.
From `v0.4.0`, each call also stores the exact request payload, prompt version, model name,
provider params, input text version id, and output text version id when a polish call creates one.

## 4. Guard The Loop

`MAX_ITERATIONS` prevents runaway refinement. The finalize endpoint records whether the loop stopped
because the audit returned no suggestions or because the iteration cap was reached.

## 5. Failure Traces Are First-Class

Provider exceptions and empty polish outputs are persisted as failed `llm_calls` before the API
returns a gateway error. That gives reviewers and operators a concrete trace for debugging instead
of a raw stack trace or missing history.

## 6. Evaluate Against Baselines

The deterministic metrics compare the full pipeline with a no-op baseline and a fixed-template
baseline. This keeps the report honest: label coverage proves structure, not real writing quality,
so the docs call out human rubric review as the next evaluation layer.

## 7. Reviewer Console Without Product Bloat

The exercise does not require users, auth, queues, or deployment infrastructure. The UI is a small
reviewer console, not a separate product surface: it exists to make provider selection, audit
results, text versions, metrics, and LLM traces easy to inspect.

