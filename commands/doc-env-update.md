---
description: Update environment-variable documentation by diffing the current code-graph against the last docs/environment/current.md. Detects added/removed/modified vars (required status, default, type, sensitive flag) and appends a dated entry to the current quarter's changelog shard.
argument-hint: [optional: context notes or scope]
---

# Update Environment Documentation

Delegate to the **BO-env-documenter** sub-agent via the Task tool to perform an incremental update of the environment-variable documentation.

**Context notes (optional):** $ARGUMENTS

## Delegation

Invoke the `BO-env-documenter` sub-agent with the following instruction:

> Perform an incremental update of the environment-variable documentation.
>
> - Mode: **update** (diff current code-graph state against `./docs/environment/current.md`).
> - Graph: read via the `knowledge-graph-custom-path` MCP. Do not read `./docs/code-graph/code-graph.json` as a file.
> - Previous state: read `./docs/environment/current.md` fully if it exists. If not, treat as genesis.
> - Output: append a dated changelog entry to the current quarter's shard at `./docs/environment/changelog/YYYY-Qn.md` with Added / Modified / Removed sections. For Modified, specify exactly what changed (required status, default, type, sensitive flag). Skip empty sections; skip the entry if nothing changed. Rewrite `./docs/environment/current.md`.
> - Never read any existing changelog shard.
> - Never read `.env`. `.env.example` only, for non-sensitive enrichment.
> - Never emit real values for sensitive vars.
>
> Follow the agent's built-in refusal conditions (staleness warnings, no env_var entities, MCP failures).

## After the agent returns

Surface the agent's report verbatim. If no changes were detected, report that. Pass through warnings unchanged.
