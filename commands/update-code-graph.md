---
description: Update the code graph incrementally from recent git changes. May recommend a full rebuild if the diff contains renames, deletions, or if grammars have changed.
argument-hint: [optional: context or scope notes]
---

# Update Code Graph

Delegate to the **BO-code-graph-builder-updater** sub-agent via the Task tool to perform an incremental update of the code graph based on recent git changes.

**Context notes (optional):** $ARGUMENTS

## Delegation

Invoke the `BO-code-graph-builder-updater` sub-agent with the following instruction:

> Perform an incremental update of the code graph.
>
> - Mode: **incremental** (`--incremental`).
> - Grammars: read from `./docs/{project}_grammars/`. If the folder is missing or empty, stop and tell the user to generate grammars first.
> - Graph: update `./docs/code-graph/code-graph.json` in place via the MCP, after backup.
> - Use `git diff --name-status HEAD~1` to determine the change set.
>
> Follow the agent's built-in refusal rules:
> - If the diff contains `R` (rename), `D` (delete), or `C` (copy) rows, refuse and tell the user to run `/code-graph-build` instead (rename cascades can't be safely handled incrementally).
> - If any grammar file under `./docs/{project}_grammars/` has a newer mtime than the graph file, refuse and tell the user to run `/code-graph-build` instead.
>
> Do not call `read_graph`. Query via `advanced_search` and `search_nodes` only.

## After the agent returns

Surface its report verbatim. If the agent refused incremental mode and recommended a full rebuild, pass that recommendation through — do **not** silently escalate to a full rebuild on the user's behalf.
