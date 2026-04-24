---
name: sprint-planner
description: Use when planning the execution order of polished requirements in a sprint. Builds a dependency graph from affected_surface and semantic_dependencies fields across all S###-TYPE-###.md files in a sprint folder, detects structural deps (create→read, create→modify, deletes-last), semantic deps (explicit references), and file-level conflicts (same file modified by multiple reqs), then computes parallelizable waves via topological sort. The script is stdlib-only Python. Invoke when the user asks to build or update a sprint roadmap; do NOT invoke for ad-hoc questions about dependencies.
---

# Sprint Planner Skill

## When to invoke this skill

Trigger only when the user explicitly asks for a sprint roadmap — typically via the `/sprint-roadmap-build` or `/sprint-roadmap-update` slash commands. The skill's purpose is to turn a set of polished requirements into a dependency graph and parallelizable execution plan.

Do NOT invoke this skill for:
- Ad-hoc dependency questions ("does F-001 depend on F-002?" — read the files directly).
- Creating or polishing requirements (that is `BO-requirements-polisher`).
- Exploring the code graph (that is the `knowledge-graph-custom-path` MCP).

## What the skill does

1. Runs `plan.py <sprint_number>` which reads all `S{NNN}-TYPE-NNN.md` files in `docs/requirements/sprint-{NNN}/`, parses their frontmatter + `Affected surface` + `Semantic dependencies` sections, builds a dependency graph, detects cycles, resolves file-level conflicts by pushing later-ID requirements to later waves, and writes `_dep-graph.json`.
2. The JSON is the machine-readable output. The slash command that invoked the skill is responsible for turning it into `_roadmap.md` for humans.

## How to invoke

The script is at `~/.claude/skills/sprint-planner/plan.py` (user-global — same skill is reused across all projects).

```bash
python3 ~/.claude/skills/sprint-planner/plan.py <sprint_number>
```

**Arguments:** a single integer (the sprint number). The script zero-pads to 3 digits internally for directory resolution.

**Exit codes:**
- `0` — success. `_dep-graph.json` written with `"ok": true`, waves populated.
- `1` — fatal error (missing sprint dir, no requirement files, parse failures, dependency cycle). `_dep-graph.json` still written with `"ok": false`, cycles and errors populated. Read it for details.
- `2` — bad invocation (missing or non-integer argument).

**Stdout:** one-line machine-parseable summary, e.g.:

```
[plan] status=ok sprint=042 requirements=5 waves=3 edges=3 errors=0 warnings=0 out=/path/to/_dep-graph.json
```

Parse fields as `key=value` pairs.

## Output JSON shape

```json
{
  "sprint": "042",
  "generated_at_unix": 1776863323,
  "ok": true,
  "requirements": [
    {
      "id": "S042-F-001",
      "title": "...",
      "type": "functional",
      "status": "proposed",
      "path": "...",
      "surface": {
        "creates": [{"type": "table", "name": "...", "is_new": true}, ...],
        "modifies": [...],
        "reads": [...],
        "deletes": [...]
      },
      "semantic_dependencies": ["S042-F-003", ...]
    }
  ],
  "edges": [
    {"from_id": "...", "to_id": "...", "kind": "semantic|structural|conflict", "reason": "..."}
  ],
  "waves": [
    {"wave": 1, "phase": "Foundational|Feature|Integration", "requirements": ["...", "..."]}
  ],
  "cycles": [],
  "warnings": [
    {"level": "warn|error", "code": "...", "message": "..."}
  ]
}
```

## How to interpret results for the user

- **`waves`** — the key output. Each wave's `requirements` list can be executed in parallel sessions. Waves must be processed in order (Wave 2 requires Wave 1 complete).
- **`edges`** — the dependency graph. Three kinds:
  - `semantic`: declared in requirement text (highest trust).
  - `structural`: inferred from affected_surface (create→read, create→modify, or deletes-last).
  - `conflict`: same file modified by multiple requirements; the target was deferred to a later wave.
- **`cycles`** — if non-empty, the graph has a cycle and no waves were computed. The user must resolve by editing requirements.
- **`warnings`** — non-fatal issues to surface to the user (unresolved cross-sprint deps, empty surfaces, unknown types).

## When the script fails

If `status=failed` in the stdout summary:
1. Read the `warnings` array in the JSON.
2. If `cycles` is non-empty, tell the user which requirements form the cycle and explain that cycles mean the requirements are contradictory.
3. If `no_sprint_dir`, tell the user to run `/sprint-init` first.
4. If `no_requirements`, tell the user to run `/requirement-polish <sprint>` first.
5. If `bad_frontmatter`, point at the specific file that failed and what was missing.

## Heuristics and limitations

- **Phase labeling** is a heuristic: any wave containing a `data` requirement becomes "Foundational"; a wave entirely of `non-functional` becomes "Integration"; otherwise "Feature". The label is cosmetic — it affects the roadmap's narrative grouping but does not change wave composition.
- **File conflict resolution is lower-ID-first.** Arbitrary but stable. Deferred requirements get a `conflict` edge in the graph for traceability.
- **Cross-sprint semantic dependencies** are noted as warnings but not enforced — the roadmap only orders within the current sprint.
- **Case-insensitive resource matching.** `users` and `Users` are the same table for dependency analysis; names are preserved as written for display.
