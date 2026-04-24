---
description: Initialize a new sprint folder for requirements. Creates docs/requirements/sprint-{NNN}/ with an _input.md template. If no sprint number is given, auto-selects the next available number. Runs staleness checks on current-state docs so you know if grounding will be reliable.
argument-hint: [optional: sprint_number]
---

# Initialize Sprint

Set up a new sprint folder for the requirements polisher to consume. This command does not invoke any agent — it is a pure scaffolding operation.

**Argument (optional):** $ARGUMENTS — a specific sprint number. If omitted, auto-selects the next available number.

## Steps

1. **Resolve the sprint number.**
   - If `$ARGUMENTS` is a valid integer, use it as the sprint number.
   - If omitted or empty, scan `docs/requirements/` for existing `sprint-NNN/` directories, find the highest `NNN`, and use `highest + 1`. If no sprints exist, use `1`.
   - Zero-pad to 3 digits for the directory name: `sprint-001`, `sprint-042`, etc.

2. **Create the directory.**
   - `mkdir -p docs/requirements/sprint-{NNN}/`.
   - If the directory already exists and contains files, stop and tell the user. Do not overwrite.
   - If the directory already exists but is empty, proceed (allows re-running after a mistake).

3. **Create `_input.md` with a template.**
   - Write the following content to `docs/requirements/sprint-{NNN}/_input.md`:

```markdown
# Sprint {NNN} — Raw Requirements

_One bullet per requirement. Agent will ground against current state (APIs, DB, env vars) and produce polished files when you run `/requirement-polish {NNN}`._

_Tips:_
- _Keep bullets focused — one requirement per bullet._
- _Mention specific tables, endpoints, or env vars when you know them; the agent will verify against current state._
- _For NFRs, include a measurable target (e.g., "p95 latency under 100ms") or the agent will ask._
- _To reference another requirement as a dependency, mention its full compound ID (e.g., "follows on from S041-F-003")._

<!-- Write your raw requirements below this line. -->

```

   - Do not overwrite if `_input.md` already exists (covered by step 2's existence check, but belt-and-suspenders).

4. **Run staleness checks** against project state. Warn but don't block — this is a scaffold, not a gate.
   - Run `git log -1 --format=%ct HEAD` to get the latest commit timestamp.
   - For each of these files, if present, compare mtime to the commit timestamp and warn if older:
     - `docs/api/current.md`
     - `docs/database/current.md`
     - `docs/environment/current.md`
     - `docs/code-graph/code-graph.json`
   - Also run `git status --porcelain`. If non-empty, warn: grounding will reflect committed state only.
   - For each stale doc, suggest the corresponding update command (`/api-doc-update`, `/db-doc-update`, `/env-doc-update`, `/code-graph-update`) so the user can refresh before polishing.

5. **Report.**
   - Confirm the sprint number chosen (especially important if autonumbered).
   - Absolute path of the created directory and `_input.md`.
   - Any staleness warnings, with the suggested remediation commands.
   - Next steps: "Edit `_input.md`, then run `/requirement-polish {NNN}`."
