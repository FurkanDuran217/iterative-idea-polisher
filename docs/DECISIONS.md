# Architecture Decisions

## 1. Store State, Not Conversation

Each LLM call receives only the current text and the immediate suggestions it needs. Conversation
history is never passed to the provider. The database stores continuity through `tracking_id`,
versions, audits, and call records.

## 2. Mock Provider First

The default provider is deterministic so the reviewer can run the service without credentials.
The OpenAI provider is optional and isolated behind the same interface.

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

## 7. Keep The API Small

The exercise does not require users, auth, queues, or a frontend. The service stays focused on the
pipeline while still adding CI, metrics, and traceability.

