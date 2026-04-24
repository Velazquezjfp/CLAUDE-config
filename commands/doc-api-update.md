---
description: Update API documentation by diffing the current code-graph state against the last docs/api/current.md. Appends a dated entry to the current quarter's changelog shard and rewrites current.md.
argument-hint: [optional: context notes or scope]
---

# Update API Documentation

Delegate to the **BO-api-documenter** sub-agent via the Task tool to perform an incremental update of the API documentation.

**Context notes (optional):** $ARGUMENTS

## Delegation

Invoke the `BO-api-documenter` sub-agent with the following instruction:

> Perform an incremental update of the API documentation.
>
> - Mode: **update** (diff current code-graph state against the existing `./docs/api/current.md`).
> - Graph: read via the `knowledge-graph-custom-path` MCP. Do not read `./docs/code-graph/code-graph.json` as a file.
> - Previous state: read `./docs/api/current.md` fully if it exists. If it doesn't exist, treat this as a genesis run (same as `/api-doc-build`).
> - Output: append a dated changelog entry to the current quarter's shard at `./docs/api/changelog/YYYY-Qn.md` (Added / Modified / Removed sections; skip empty sections; skip the entry entirely if nothing changed). Rewrite `./docs/api/current.md` with the new state.
> - Never read any existing changelog shard, not even the current quarter's. Append-only.
> - Examples: source from OpenAPI → test fixtures → deterministic synthesis, in that order. Never invent values.
>
> Follow the agent's built-in workflow and refusal conditions.

## After the agent returns

Surface the agent's report verbatim. If no changes were detected, report that to the user exactly as the agent reported it — don't second-guess. If the agent stopped (graph missing, graph stale, parse failures), pass the question through unchanged.
