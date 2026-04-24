---
description: Add a single new requirement to a sprint. Appends the description to _input.md and runs the polish step on just that item. Useful for capturing one-off ideas mid-sprint without opening _input.md manually.
argument-hint: <sprint_number> "<one-line requirement description>"
---

# Add New Requirement

Append a new raw requirement to `docs/requirements/sprint-{NNN}/_input.md`, then delegate to the **BO-requirements-polisher** sub-agent to polish just that item.

**Arguments:** $ARGUMENTS

The first argument is the sprint number (integer). The remainder, treated as a single quoted string, is the one-line raw requirement description.

## Delegation

Parse `$ARGUMENTS` into `{sprint_number}` and `{description}`. If the description is missing or the sprint number isn't a valid integer, stop and ask for both.

Then:

1. Compute the target directory: `docs/requirements/sprint-$(printf "%03d" {sprint_number})/`.
2. If the directory doesn't exist, create it.
3. If `_input.md` doesn't exist, create it with a one-line header: `# Sprint {NNN} — Raw Requirements\n\n`.
4. Append `- {description}` as a new bullet to `_input.md`. No other modifications to the file.
5. Invoke the `BO-requirements-polisher` sub-agent with the following instruction:

> Polish requirements for sprint {sprint_number}. The newly-appended bullet is the only unprocessed item. Skip anything already polished. Produce the polished file and update `_index.md`.
>
> Grounding sources: `docs/api/current.md`, `docs/database/current.md`, `docs/environment/current.md`, plus the code-graph via `knowledge-graph-custom-path` MCP.
>
> Fixed vocabulary: in `affected_surface`, use only verbs `creates|modifies|reads|deletes` and resource types `table|endpoint|env_var|file|class|function|component|selector|constant`.
>
> Cross-requirement uniqueness: a resource can be in `creates` for at most one requirement. Check existing polished files in this sprint — if any already `creates` a resource this new one would also create, shift the new one to `modifies` instead.
>
> Semantic dependencies are sequencing constraints (B must finish before A can start), not cross-references. Do not declare reciprocal deps, do not list requirements just for context, do not infer deps that aren't stated.
>
> Follow the agent's built-in workflow and refusal conditions.

## After the agent returns

Surface the report verbatim. Confirm the new requirement's ID so the user can reference it going forward.