# Similar-System Analysis

This pass reviewed the project against common LLM engineering tools and patterns as of
2026-06-15. The goal was not to clone a large platform, but to pull the smallest useful ideas into
this hiring-task-sized service.

## Systems Reviewed

| System | Relevant pattern | What this project should borrow |
| --- | --- | --- |
| LangSmith | Tracing, evaluation, prompt testing, deployments in one workflow | Keep every run inspectable and tie evaluation back to the exact trace. |
| Langfuse | Open-source observability, prompt management, datasets, experiments, custom scores | Treat scores, prompt versions, providers, and traces as one product surface. |
| promptfoo | Test-driven prompt development, baseline matrices, CI-friendly reports | Keep deterministic baselines and make reports easy to compare across cases. |
| OpenAI Evals | Reusable eval framework and private evals for workflow-specific patterns | Prefer small, repeatable eval fixtures over one-off manual judgment. |

Sources:

- https://docs.langchain.com/langsmith/home
- https://langfuse.com/docs
- https://www.promptfoo.dev/docs/intro/
- https://github.com/openai/evals

## Findings

The current service already has the core primitives these systems emphasize: trace records,
prompt versions, provider metadata, deterministic mock baselines, and repeatable quality gates.
The gap was that reviewers had to inspect several endpoints to form a handoff judgment.

The highest-leverage improvement is a run-level dossier:

- one endpoint that summarizes whether the run is ready;
- one Markdown report that can be copied into a PR, email, or hiring submission note;
- trace evidence that proves the air-gapped loop actually ran;
- prompt version and provider provenance;
- next checks that keep deterministic scores from pretending to be human judgment.

## Implemented In v0.12.0

- Added `GET /api/v1/pipeline/{tracking_id}/report`.
- Added a Reviewer Report panel to the console.
- Kept deterministic baseline evaluation pinned to Mock.
- Preserved real-provider smoke testing as a separate explicit command.

## Deliberately Not Added

- A full hosted experiment dashboard: too much scope for the exercise.
- User feedback collection: useful later, but the current task is reviewer handoff.
- Cross-provider batch runs from the UI: valuable, but it would spend real API quota too easily.
- LLM-as-judge scoring by default: useful for production, risky for a small deterministic grading
  path unless frozen and cost-controlled.
