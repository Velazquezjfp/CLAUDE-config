---
description: Build the code graph from scratch (full rebuild). Safe to re-run; snapshots the previous graph before swapping.
argument-hint: [optional: project name override]
---

# Build Code Graph

Delegate to the **BO-code-graph-builder-updater** sub-agent via the Task tool to perform a full rebuild of the code graph from the current working tree.

**Project name override (optional):** $ARGUMENTS

## Delegation

Invoke the `BO-code-graph-builder-updater` sub-agent with the following instruction:

> Perform a full rebuild of the code graph.
>
> - Mode: **full** (the default — do not pass `--incremental`).
> - Grammars: read from `./docs/{project}_grammars/`. If the folder is missing or empty, stop and tell the user to generate grammars first.
> - Output: build to `./docs/code-graph/code-graph.new.json` then swap to `./docs/code-graph/code-graph.json` atomically.
> - Project name: use `$ARGUMENTS` if non-empty, otherwise derive from the working directory's parent folder name.
>
> Follow the agent's built-in workflow (resolve project → load grammars → scan in batches of 10–15 → emit to MCP → verify via `get_statistics` → swap → report). Do not call `read_graph`.

## After the agent returns

Surface its report to the user verbatim. Do not re-summarize or add analysis. If the agent stopped and asked for something (missing grammars, MCP connection failure, >5% parse failures), pass the question through unchanged.
