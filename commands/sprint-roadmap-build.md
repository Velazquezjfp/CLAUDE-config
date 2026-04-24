---
description: Build the execution roadmap for a sprint. Invokes the sprint-planner skill to compute dependency waves and conflicts from polished requirements, then generates a human-readable _roadmap.md alongside the machine-readable _dep-graph.json.
argument-hint: <sprint_number>
---

# Build Sprint Roadmap

Compute the execution plan for sprint `$ARGUMENTS` by running the sprint-planner script, then generate a human-readable roadmap from its JSON output.

## Steps

### 1. Validate arguments

`$ARGUMENTS` must be a positive integer. If not, stop and ask for a sprint number.

### 2. Run the planner script

Execute:

```bash
python3 ~/.claude/skills/sprint-planner/plan.py $ARGUMENTS
```

Capture stdout and exit code.

**If exit code is 2:** bad invocation. Surface the stderr and stop.

**If exit code is 1:** script ran but found fatal issues. The JSON at `docs/requirements/sprint-$(printf "%03d" $ARGUMENTS)/_dep-graph.json` has been written with `ok: false`. Read it, surface the errors (cycles, missing files, bad frontmatter) to the user with specific file references, and stop without writing a roadmap. Do NOT attempt to write `_roadmap.md` when the graph is broken — a stale or empty roadmap is worse than no roadmap.

**If exit code is 0:** proceed to step 3.

### 3. Read the JSON

Read `docs/requirements/sprint-$(printf "%03d" $ARGUMENTS)/_dep-graph.json`. Parse the structure:

- `waves[]` — the parallelizable groups in execution order.
- `edges[]` — the full dependency graph, with `kind` distinguishing semantic / structural / conflict.
- `requirements[]` — full per-req metadata.
- `warnings[]` — non-fatal issues to surface.

### 4. Write `_roadmap.md`

Write `docs/requirements/sprint-$(printf "%03d" $ARGUMENTS)/_roadmap.md` from scratch with this structure:

```markdown
# Sprint {NNN} — Execution Roadmap

_Generated from `_dep-graph.json`. Do not edit manually — regenerate with `/sprint-roadmap-update {NNN}` when requirements change._

**Summary:** {N} requirements across {W} waves. {C} file conflicts auto-resolved.

## Wave 1 — {phase label}

_These requirements have no pending dependencies and can execute in parallel sessions._

- **{id}** — {title} ({type})
  - Affected: creates {n}, modifies {m}, reads {r}, deletes {d}
  - File: `{path}`

- **{id}** — {title} ({type})
  - ...

## Wave 2 — {phase label}

_Runs after Wave 1 completes._

- **{id}** — {title} ({type})
  - Depends on: {comma-separated list of IDs from previous waves that gate this one — derive from edges where to_id == this id and from_id is in Waves 1..N-1}
  - Affected: creates {n}, modifies {m}, reads {r}, deletes {d}
  - File: `{path}`

... (continue for all waves)

## Dependency edges

### Semantic (from requirement text)

- **{from}** → **{to}** — {reason}

### Structural (from affected_surface)

- **{from}** → **{to}** — {reason}

### Conflicts (auto-resolved)

- **{from}** → **{to}** — {reason}

_Conflicts mean the target requirement was pushed to a later wave because it would have modified the same file as the source. Both still execute; they just can't be parallel._

(Omit subsections with no entries.)

## Warnings

- [{level}] {code}: {message}

(Omit section if no warnings.)
```

**Rules for generating the roadmap:**

- **"Depends on" per requirement** — compute from the `edges` array. For each requirement in Wave N (N > 1), list IDs where an edge has `to_id == this.id` and `from_id` is in Wave 1..N-1. If no such edges, omit the "Depends on" line.
- **Surface summary counts** — from `surface.creates.length`, etc. Omit zero-count categories: "Affected: creates 2, modifies 1" (no reads, no deletes mentioned).
- **File path** — from `path` field; show relative if possible, otherwise absolute.
- **Stable ordering** — within each wave, sort by requirement ID. In the edges sections, sort by `from_id` then `to_id`.

### 5. Report to the user

Summarize what was produced:

- Sprint number and number of waves.
- Path to `_roadmap.md` and `_dep-graph.json`.
- If conflicts were auto-resolved, name them explicitly so the user can review whether the ordering is acceptable. Example: "`S042-F-002` was deferred from Wave 1 to Wave 2 due to a file conflict with `S042-F-001` on `services/auth.py`."
- Any warnings from the JSON (cross-sprint deps, empty surfaces).
- Next step: user can run `/sprint-roadmap-update {NNN}` after requirements change, or begin implementing Wave 1 in parallel sessions.

## Don't

- Don't call `read_graph` on the code-graph MCP — this command is about requirements, not code structure.
- Don't modify requirement files — they are the script's input, not this command's output.
- Don't generate a roadmap when the script reported `ok: false`. Surface the errors and stop.
- Don't re-run the script multiple times. One invocation per command.
