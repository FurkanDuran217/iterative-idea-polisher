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

## 4. Guard The Loop

`MAX_ITERATIONS` prevents runaway refinement. The finalize endpoint records whether the loop stopped
because the audit returned no suggestions or because the iteration cap was reached.

## 5. Keep The API Small

The exercise does not require users, auth, queues, or a frontend. The service stays focused on the
pipeline while still adding CI, metrics, and traceability.

