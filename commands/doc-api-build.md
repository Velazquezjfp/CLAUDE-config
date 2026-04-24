---
description: Build API documentation from scratch. Queries the code-graph, regenerates docs/api/current.md, and writes a genesis entry in the current quarter's changelog shard.
argument-hint: [optional: context notes or scope]
---

# Build API Documentation

Delegate to the **BO-api-documenter** sub-agent via the Task tool to perform a full build of the API documentation from the current state of the code-graph.

**Context notes (optional):** $ARGUMENTS

## Delegation

Invoke the `BO-api-documenter` sub-agent with the following instruction:

> Perform a full build of the API documentation.
>
> - Mode: **full** (genesis — treat this as the first run; all endpoints in the graph are "added").
> - Graph: read via the `knowledge-graph-custom-path` MCP. Do not read `./docs/code-graph/code-graph.json` as a file.
> - Output: rewrite `./docs/api/current.md` from scratch. Append a genesis changelog entry (all endpoints listed under "Added") to the current quarter's shard at `./docs/api/changelog/YYYY-Qn.md`, creating the shard if missing.
> - Examples: source from OpenAPI → test fixtures → deterministic synthesis, in that order. Never invent values.
>
> Follow the agent's built-in workflow and refusal conditions (stop if the graph is empty, warn if the graph is older than the latest git commit, stop if >20% of endpoints have no resolvable handler file).

## After the agent returns

Surface the agent's report to the user verbatim. Do not re-summarize. If the agent stopped and asked for something (graph missing, graph stale, parse failures), pass the question through unchanged.