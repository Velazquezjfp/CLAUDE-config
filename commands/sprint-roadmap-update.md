---
description: Update the execution roadmap for a sprint. Re-runs the sprint-planner to recompute waves from the current state of the polished requirements. Use this after running /requirement-polish, /requirement-new, or after manually editing requirement files.
argument-hint: <sprint_number>
---

# Update Sprint Roadmap

Recompute the execution plan for sprint `$ARGUMENTS`. This is functionally identical to `/sprint-roadmap-build` but exists as a separate command so you (and git history) can tell creation from updates at a glance.

## Steps

### 1. Validate arguments

`$ARGUMENTS` must be a positive integer. If not, stop and ask.

### 2. Staleness sanity check

Confirm there's a reason to re-run:

- Resolve the sprint directory: `docs/requirements/sprint-$(printf "%03d" $ARGUMENTS)/`.
- If the directory doesn't exist, tell the user to run `/sprint-init $ARGUMENTS` first and stop.
- If `_dep-graph.json` doesn't exist, this is effectively a first build — tell the user that and proceed as if they ran `/sprint-roadmap-build`.
- If `_dep-graph.json` exists, compare its mtime against every `S{NNN}-TYPE-NNN.md` file in the directory. If none of the requirement files are newer than `_dep-graph.json`, warn the user that the roadmap appears current and ask whether to re-run anyway. If they confirm, proceed. If they decline, stop.

### 3. Run the planner

```bash
python3 ~/.claude/skills/sprint-planner/plan.py $ARGUMENTS
```

Interpret exit codes exactly as in `/sprint-roadmap-build`:

- **2** — bad invocation, surface stderr and stop.
- **1** — script found fatal issues; read `_dep-graph.json`, surface errors, do not write `_roadmap.md`.
- **0** — proceed.

### 4. Regenerate `_roadmap.md`

Same structure and rules as `/sprint-roadmap-build`. Rewrite from scratch; do not try to merge with the previous roadmap.

### 5. Diff-style report to the user

Because this is an update, the user likely wants to know what changed. If a previous `_roadmap.md` existed, compare the new wave composition against the old one and highlight:

- **Requirements that moved waves.** "S042-F-003 moved from Wave 2 to Wave 1" (dependency was removed or resolved).
- **Requirements that newly conflict.** "S042-F-005 now conflicts with S042-F-001 on `services/auth.py` — deferred to Wave 2."
- **New requirements.** IDs that weren't in the previous roadmap.
- **Removed requirements.** IDs in the previous roadmap but not the new one.

If no previous roadmap existed, just report the current state as in `/sprint-roadmap-build`.

Also surface:

- Path to updated `_roadmap.md` and `_dep-graph.json`.
- Any warnings from the JSON.

## Don't

- Don't modify requirement files.
- Don't skip the staleness check — it saves the user from re-running when nothing changed.
- Don't attempt a partial regeneration. The planner always rebuilds the graph from scratch; the roadmap should too.
