---
description: Polish raw requirement notes for a sprint. Reads docs/requirements/sprint-{NNN}/_input.md, grounds each item against current state (APIs, DB, env vars), and produces one polished requirement file per item plus a sprint-level index. Idempotent — already-polished items are skipped.
argument-hint: <sprint_number>
---

# Polish Requirements

Delegate to the **BO-requirements-polisher** sub-agent via the Task tool to process the raw requirements in the specified sprint's `_input.md`.

**Sprint number:** $ARGUMENTS

## Delegation

Invoke the `BO-requirements-polisher` sub-agent with the following instruction:

> Polish requirements for sprint $ARGUMENTS.
>
> - Sprint: **$ARGUMENTS** (zero-pad to 3 digits for the directory name: `docs/requirements/sprint-$(printf "%03d" $ARGUMENTS)/`).
> - Input: read `_input.md` in that directory. If missing, stop and tell the user to create it with raw requirement notes.
> - Grounding sources: `docs/api/current.md`, `docs/database/current.md`, `docs/environment/current.md` (read fully if present), plus the code-graph via `knowledge-graph-custom-path` MCP.
> - Output: produce one polished file per new requirement (filename `S{NNN}-{TYPE}-{NNN}.md`), and rewrite `_index.md` in the sprint folder.
> - Skip any raw item whose polished file already exists in the sprint folder.
> - Fixed vocabulary: in `affected_surface`, use only verbs `creates|modifies|reads|deletes` and resource types `table|endpoint|env_var|file|class|function|component|selector|constant`.
> - Cross-requirement uniqueness: a resource can be in `creates` for at most one requirement. If two raw items both read as creating the same file/table/endpoint, one owns `creates` and the other shifts to `modifies`.
> - Semantic dependencies are sequencing constraints (B must finish before A can start), not cross-references. Do not declare reciprocal deps (A→B and B→A), do not list requirements just for context, and do not infer deps that aren't stated in the raw input. Structural deps are computed by the planner from `affected_surface`.
>
> Follow the agent's built-in workflow and refusal conditions (staleness warnings, missing `_input.md`, unresolved references, empty code-graph).

## After the agent returns

Surface the report verbatim. If unresolved references or ambiguous classifications were flagged, pass them through so the user can address them.
