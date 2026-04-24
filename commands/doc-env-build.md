---
description: Build environment-variable documentation from scratch. Queries the code-graph for env_var entities, reads only the files that reference them, enriches from .env.example for non-sensitive vars, and writes a genesis entry in the current quarter's changelog shard.
argument-hint: [optional: context notes or scope]
---

# Build Environment Documentation

Delegate to the **BO-env-documenter** sub-agent via the Task tool to perform a full build of the environment-variable documentation.

**Context notes (optional):** $ARGUMENTS

## Delegation

Invoke the `BO-env-documenter` sub-agent with the following instruction:

> Perform a full build of the environment-variable documentation.
>
> - Mode: **full** (genesis — treat as first run; all vars in the graph are "added").
> - Graph: read via the `knowledge-graph-custom-path` MCP. Do not read `./docs/code-graph/code-graph.json` as a file.
> - Output: rewrite `./docs/environment/current.md` from scratch, grouped by purpose (Runtime, Server, Database, Cache, Observability, prefix-based groups, Miscellaneous). Append a genesis changelog entry to the current quarter's shard at `./docs/environment/changelog/YYYY-Qn.md`, creating the shard if missing.
> - Never read `.env`. Only `.env.example` (or aliases) may be read, and only for non-sensitive vars.
> - Never emit real values for sensitive vars. When in doubt about sensitivity, treat as sensitive.
>
> Follow the agent's built-in workflow: graph query → source extraction for defaults/types/required → sensitive detection → `.env.example` enrichment → grouping → diff → append → rewrite.

## After the agent returns

Surface the agent's report to the user verbatim. Pass through any warnings (inconsistent defaults, unclear purposes, staleness) without re-summarizing.