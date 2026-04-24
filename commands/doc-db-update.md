---
description: Update database documentation by diffing current code-graph state against last docs/database/current.md. Granular changelog categorization (column-level, FK-level, index-level changes) with critical-change markers.
argument-hint: [optional: context notes or scope]
---

# Update Database Documentation

Delegate to the **BO-db-documenter** sub-agent via the Task tool to perform an incremental update of the database documentation.

**Context notes (optional):** $ARGUMENTS

## Delegation

Invoke the `BO-db-documenter` sub-agent with the following instruction:

> Perform an incremental update of the database documentation.
>
> - Mode: **update** (diff current code-graph state against `./docs/database/current.md`).
> - Graph: read via the `knowledge-graph-custom-path` MCP. Do not read `./docs/code-graph/code-graph.json` as a file.
> - Previous state: read `./docs/database/current.md` fully if it exists. If not, treat as a genesis run.
> - Output: append a dated changelog entry to the current quarter's shard at `./docs/database/changelog/YYYY-Qn.md` with granular categorization per engine (Added/Removed tables, per-table column/FK/index changes, with `**[breaking]**` markers on type changes, nullability changes, vector dimension/metric changes, and search mapping type changes). Skip empty sections; skip the entry entirely if nothing changed. Rewrite `./docs/database/current.md`.
> - Never read any existing changelog shard, not even the current quarter's.
> - No sample rows.
> - ORM models are authoritative.
>
> Follow the agent's built-in refusal conditions (staleness warnings, no table entities, >20% unresolved).

## After the agent returns

Surface the agent's report verbatim. If no changes were detected, report that verbatim. Pass through any questions or warnings unchanged.