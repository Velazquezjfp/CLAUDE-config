---
description: Build database documentation from scratch. Detects engines in use (relational, vector, search, document, cache), regenerates docs/database/current.md, and writes a genesis entry in the current quarter's changelog shard.
argument-hint: [optional: context notes or scope]
---

# Build Database Documentation

Delegate to the **BO-db-documenter** sub-agent via the Task tool to perform a full build of the database documentation from the current state of the code-graph.

**Context notes (optional):** $ARGUMENTS

## Delegation

Invoke the `BO-db-documenter` sub-agent with the following instruction:

> Perform a full build of the database documentation.
>
> - Mode: **full** (genesis — treat this as the first run; all tables/indexes/collections in the graph are "added").
> - Graph: read via the `knowledge-graph-custom-path` MCP. Do not read `./docs/code-graph/code-graph.json` as a file.
> - Output: rewrite `./docs/database/current.md` from scratch with one section per detected engine. Append a genesis changelog entry to the current quarter's shard at `./docs/database/changelog/YYYY-Qn.md`, creating the shard if missing.
> - No sample rows, real or synthesized.
> - ORM models are authoritative; migrations are secondary references only.
>
> Follow the agent's built-in workflow: engine detection from imports/extends/env-vars, schema extraction from ORM model files, granular diff with critical-change markers, and refusal conditions (staleness warnings, no table entities, >20% unresolved).

## After the agent returns

Surface the agent's report to the user verbatim. Do not re-summarize. If the agent stopped and asked for something, pass the question through unchanged.