# BO Documentation & Requirements Workflow

A pipeline of Claude Code agents, skills, and slash commands that keeps your codebase's documentation, requirements, and roadmap in sync with reality. Built for solo dev work across multiple client projects, optimized for bounded context usage, deterministic outputs, and pre-push discipline.

---

## Why this exists

Most AI-assisted workflows suffer from three problems:
- **Context rot** — agents re-read growing files (changelogs, full code graphs, aggregate requirements) until they OOM or truncate.
- **Drift** — documentation describes what *used* to be; requirements reference fields that no longer exist.
- **Blind parallelism** — "which of these tasks can I work on in parallel?" is a judgment call, not a structured answer.

This workflow addresses all three by enforcing:
- **Bounded reads** — every agent reads only files designed to stay small. Growing files are append-only and never re-read.
- **Structured grounding** — requirements reference the actual current state of APIs/DB/env; implementation stays within a declared `affected_surface`.
- **Deterministic planning** — a stdlib Python script computes parallelizable waves from structured requirement metadata. No LLM judgment in the graph math.

---

## Pipeline overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ONE-TIME PROJECT SETUP                            │
└─────────────────────────────────────────────────────────────────────────────┘

       /grammar-build ─► docs/{project}_grammars/*.json
              │            (regex patterns per language, Context7-verified)
              ▼
       /code-graph-build ─► docs/code-graph/code-graph.json
              │             (entities + relations, via KG MCP)
              ▼
    ┌────────┬────────┬────────┐
    ▼        ▼        ▼        │
/api-doc  /db-doc  /env-doc    │
 -build    -build   -build     │
    │        │        │        │
    ▼        ▼        ▼        │
 docs/api  docs/db  docs/env   │
 current   current  current    │
  .md       .md      .md       │
    └────────┴────────┴────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          PER-SPRINT PLANNING                                │
└─────────────────────────────────────────────────────────────────────────────┘

  /sprint-init [N] ─► docs/requirements/sprint-NNN/_input.md
         │             (scaffold + staleness checks)
         ▼
   [edit _input.md with raw requirement ideas]
         │
         ▼
  /requirement-polish {N}    or   /requirement-new {N} "..."
         │
         ▼
  docs/requirements/sprint-NNN/
    ├── S042-F-001.md        ◄── polished, grounded, structured
    ├── S042-F-002.md
    ├── S042-D-001.md
    └── _index.md            ◄── bounded aggregate for the PM step
         │
         ▼
  /sprint-roadmap-build {N}
         │
         ▼
  docs/requirements/sprint-NNN/
    ├── _dep-graph.json      ◄── machine-readable graph
    └── _roadmap.md          ◄── waves, conflicts, phases

┌─────────────────────────────────────────────────────────────────────────────┐
│                   PER-REQUIREMENT EXECUTION (parallel-safe)                 │
└─────────────────────────────────────────────────────────────────────────────┘

  /start-requirement S042-F-001    (spawn one session per Wave-N requirement)
         │
         ▼
  plan → implement → write tests → run tests → update frontmatter
         │
         ▼
  [USER: review, commit code]
         │
         ▼
  /code-graph-update
         │
         ▼
  /api-doc-update, /db-doc-update, /env-doc-update  (as applicable)
         │
         ▼
  [USER: commit docs, push]
```

---

## Directory layout the pipeline produces

```
your-project/
├── .claude/
│   ├── agents/                        # per-project agent definitions
│   │   ├── BO-project-grammar-builder.md
│   │   ├── BO-code-graph-builder.md
│   │   ├── BO-api-documenter.md
│   │   ├── BO-db-documenter.md
│   │   ├── BO-env-documenter.md
│   │   └── BO-requirements-polisher.md
│   ├── commands/                      # per-project slash commands
│   │   ├── grammar-build.md
│   │   ├── grammar-update.md
│   │   ├── code-graph-build.md
│   │   ├── code-graph-update.md
│   │   ├── api-doc-build.md
│   │   ├── api-doc-update.md
│   │   ├── db-doc-build.md
│   │   ├── db-doc-update.md
│   │   ├── env-doc-build.md
│   │   ├── env-doc-update.md
│   │   ├── sprint-init.md
│   │   ├── requirement-polish.md
│   │   ├── requirement-new.md
│   │   ├── sprint-roadmap-build.md
│   │   ├── sprint-roadmap-update.md
│   │   └── start-requirement.md
│   └── agent-memory/                  # per-project persistent memory
│       ├── project-grammar-builder/
│       ├── api-documenter/
│       ├── db-documenter/
│       ├── env-documenter/
│       ├── requirements-polisher/
│       └── code-graph-builder/
│
└── docs/
    ├── {project}_grammars/            # regex patterns, one per language
    │   ├── python.json
    │   ├── javascript.json
    │   └── ...
    ├── code-graph/
    │   ├── code-graph.json            # KG MCP backing store
    │   └── backups/
    ├── api/
    │   ├── current.md                 # bounded; rewritten each run
    │   └── changelog/
    │       └── YYYY-QN.md             # append-only, never re-read
    ├── database/
    │   ├── current.md
    │   └── changelog/YYYY-QN.md
    ├── environment/
    │   ├── current.md
    │   └── changelog/YYYY-QN.md
    ├── requirements/
    │   ├── sprint-001/
    │   │   ├── _input.md              # user-written raw notes
    │   │   ├── _index.md              # bounded aggregate
    │   │   ├── _dep-graph.json        # from planner script
    │   │   ├── _roadmap.md            # from planner slash command
    │   │   ├── S001-F-001.md          # polished requirements
    │   │   ├── S001-F-002.md
    │   │   └── S001-D-001.md
    │   └── sprint-002/
    │       └── ...
    └── tests/
        └── S001-F-001/                # tests per requirement
            └── TC-S001-F-001-01.py
```

Additionally, one user-global skill lives outside any project:

```
~/.claude/skills/sprint-planner/
├── SKILL.md
└── plan.py                            # stdlib-only Python, reusable
```

---

## The commands, in execution order

Each command below shows: what it does, when to run it, what it expects as input, what it produces, and when to use its `-update` variant instead.

### 1. Grammars

Detect languages and framework versions. Emit regex patterns per language. Rarely re-run.

| Command | When to use | Input | Output |
|---|---|---|---|
| `/grammar-build` | Once per project, at the very start. | Codebase, manifests, lockfiles. | `docs/{project}_grammars/*.json` |
| `/grammar-update` | Only when you add a new language or upgrade a major framework version. Not part of regular work. | Existing grammar files + current codebase. | Updates affected grammar files in place. |

### 2. Code graph

Extract structured entities and relationships from the codebase using the grammar patterns. Backs the `knowledge-graph-custom-path` MCP.

| Command | When to use | Input | Output |
|---|---|---|---|
| `/code-graph-build` | Once per project, after grammars exist. Also whenever you suspect the graph has drifted badly. | Grammar files + full codebase. | `docs/code-graph/code-graph.json` (via KG MCP) |
| `/code-graph-update` | After every commit that touched source code. Part of the regular pre-push flow. | Same inputs; incremental. | Updates entities/relations for changed files. |

### 3. Current-state documentation

Three parallel commands, one per domain. Each pair has the same structure: read via MCP + ground file, rewrite `current.md`, append a changelog entry.

| Command | When to use | Input | Output |
|---|---|---|---|
| `/api-doc-build` | Once per project, after code graph exists. | Code graph (via MCP) + source files for endpoints. | `docs/api/current.md` + `docs/api/changelog/YYYY-QN.md` |
| `/api-doc-update` | After every commit that changed API surface. | Same + previous `current.md`. | Rewrites `current.md`, appends to current-quarter changelog shard. |
| `/db-doc-build` | Once per project. | Code graph + ORM model files. Supports relational, vector, search, document, cache engines. | `docs/database/current.md` + changelog shard |
| `/db-doc-update` | After commits that touched ORM models or schemas. | Same. | Rewrites + appends. |
| `/env-doc-build` | Once per project. | Code graph (`env_var` entities) + source files + `.env.example` (if present). | `docs/environment/current.md` + changelog shard |
| `/env-doc-update` | After commits that added/removed env var reads. | Same. | Rewrites + appends. |

**Rule:** changelog shards (`YYYY-QN.md`) are append-only and never re-read — not even the current quarter. This is what keeps the system bounded.

### 4. Sprint scaffolding

| Command | When to use | Input | Output |
|---|---|---|---|
| `/sprint-init [N]` | Start of a new sprint. `N` is optional — auto-numbers if omitted. | Existing sprint folders (for auto-numbering) + `current.md` files (for staleness checks). | `docs/requirements/sprint-NNN/_input.md` (template) |

No agent delegation — pure filesystem scaffolding plus staleness warnings.

### 5. Requirement polishing

Turn raw notes into structured, grounded, testable per-requirement files.

| Command | When to use | Input | Output |
|---|---|---|---|
| `/requirement-polish {N}` | After you've filled `_input.md` with raw requirement notes. Idempotent: re-running skips already-polished items. | `_input.md` + `current.md` files + code graph. | One `S{NNN}-{TYPE}-{NNN}.md` per raw item + rewritten `_index.md`. |
| `/requirement-new {N} "desc"` | Mid-sprint when you have a single new idea. Appends a bullet to `_input.md` and polishes just that item. | Same. | One new polished requirement + updated `_index.md`. |

**No refine command.** Once polished, a requirement isn't re-processed by an agent. Small edits: you edit the file directly (git tracks it). Substantive changes mid-sprint: write a new requirement that supersedes the old (manually flip the old's `status: superseded`).

### 6. Sprint roadmap

Compute parallelizable execution waves from the polished requirements. Stdlib-Python skill, deterministic.

| Command | When to use | Input | Output |
|---|---|---|---|
| `/sprint-roadmap-build {N}` | After `_input.md` is fully polished, to plan execution. | All `S{NNN}-*.md` files in the sprint folder. | `docs/requirements/sprint-NNN/_dep-graph.json` + `_roadmap.md` |
| `/sprint-roadmap-update {N}` | After adding/polishing new requirements or editing existing ones. Checks staleness first. | Same. | Regenerates both files; reports diffs (wave moves, new conflicts). |

**If the graph has cycles or duplicate creators, `_roadmap.md` is NOT written** — only the JSON, with `ok: false`. Fix the underlying requirements (the JSON points at which ones to edit) and re-run.

### 7. Requirement execution

| Command | When to use | Input | Output |
|---|---|---|---|
| `/start-requirement {id}` | In a fresh session per requirement. Run in parallel sessions for Wave-N IDs from the roadmap. | One polished requirement file + `current.md` grounding + code graph. | Code changes in affected files + tests in `docs/tests/{id}/` + updated frontmatter on the requirement file (`status: implemented`, test counts). |

**No git operations.** The command implements + tests + updates status. You review, commit code, run the updater commands, commit docs, push.

---

## Expected outputs at each stage

Use this table to verify each stage worked before moving to the next.

| Stage | Check these files exist and are non-empty |
|---|---|
| After `/grammar-build` | `docs/{project}_grammars/{language}.json` for each detected language; each contains a `patterns` dict with regex arrays. |
| After `/code-graph-build` | `docs/code-graph/code-graph.json` contains entities with types from the fixed vocabulary (`file`, `function`, `class`, `component`, `endpoint`, `table`, `selector`, `constant`, `env_var`). |
| After `/api-doc-build` | `docs/api/current.md` lists endpoints with schemas; `docs/api/changelog/YYYY-QN.md` has a genesis entry. |
| After `/db-doc-build` | `docs/database/current.md` has one section per detected engine (e.g., "Relational — Postgres"). |
| After `/env-doc-build` | `docs/environment/current.md` has groups (Runtime / Server / Database / etc.); sensitive vars marked with 🔒. |
| After `/sprint-init N` | `docs/requirements/sprint-NNN/_input.md` exists with a template header. |
| After `/requirement-polish N` | One `S{NNN}-{TYPE}-{NNN}.md` per raw input bullet + `_index.md` listing them. Each polished file has valid frontmatter + `## Affected surface` + `## Test cases`. |
| After `/sprint-roadmap-build N` | `_dep-graph.json` with `"ok": true` + `_roadmap.md` with waves. If `ok: false`, fix the errors listed in the JSON's `warnings` array. |
| After `/start-requirement ID` | Modified source files + new tests in `docs/tests/{ID}/` + requirement frontmatter updated to `status: implemented`. No git commits. |

---

## The pre-push flow

Every code change follows this sequence. **One push at the end**, not two.

1. **Write code** — either via `/start-requirement` or manually.
2. **Commit the code changes.** Local only. `git commit -m "..."`
3. **`/code-graph-update`** — the graph now reflects your commit.
4. **`/api-doc-update`** (if APIs changed).
5. **`/db-doc-update`** (if schemas changed).
6. **`/env-doc-update`** (if env vars changed).
7. **Review the doc changes.** Do the diffs look right? If so:
8. **Commit the doc changes.** Separate commit or amended into #2 — your call.
9. **Push.**

Running the documenters *before* pushing means anyone pulling your commits sees code + docs together, never one without the other.

---

## Parallel execution pattern

For waves larger than one:

1. Open `_roadmap.md`. Pick Wave 1's requirement IDs.
2. Spawn one terminal (or tab, or tmux window) per requirement.
3. In each, run `/start-requirement S{NNN}-F-XXX`.
4. Wait for all to finish.
5. Review, commit code in each branch (or single trunk — your workflow).
6. Run `/code-graph-update` once. Run the doc updaters once. Commit docs. Push.
7. Move to Wave 2.

The sprint planner guarantees no two requirements in the same wave modify the same file. If the planner couldn't prove that, the second requirement was deferred to the next wave — surfaced in the roadmap's "Conflicts auto-resolved" section.

---

## When things go wrong

| Symptom | Likely cause | Fix |
|---|---|---|
| `/code-graph-build` fails with "no grammars found" | Grammars never generated. | Run `/grammar-build` first. |
| `/api-doc-build` says `endpoint` entities missing | Code graph is empty or didn't extract endpoints. | Re-run `/code-graph-build`. Check grammars have `api_endpoints` patterns. |
| `/requirement-polish` flags "unresolved resource" | A requirement references a table/endpoint/env_var that doesn't exist in current state and wasn't marked `(new)`. | Either mark it `(new)` in `_input.md` and re-polish, or run the relevant `current.md` updater. |
| `/sprint-roadmap-build` fails with `mutual_semantic_dependency` | Two requirements declare each other as semantic deps. This is always an authoring error. | The error names the two files. Delete the dep from whichever requirement logically comes first. |
| `/sprint-roadmap-build` fails with `duplicate_creator` | Two requirements both declare `creates:` on the same resource. | Pick one to own the `creates` entry; change the other to `modifies` in its `_input.md` and re-polish. |
| `/sprint-roadmap-build` fails with a `cycle` error | Dependency cycle (3+ requirements form a loop). | Identify which dep to break; edit the offending requirement's `## Semantic dependencies`; re-polish. |
| `/start-requirement` stops at "scope exceeded" | Implementation wants to edit a file not in `affected_surface`. | Three options the command offers: one-time override, re-polish the requirement with expanded surface, or abort. |
| `/start-requirement` stops after 3 failing test attempts | Either implementation bug or under-specified acceptance criteria. | Review the transcript; decide whether to fix code, fix test, or re-polish requirement. |
| `current.md` files look stale after several commits | Documenters weren't run. | Run the three `/..-doc-update` commands. Commit. |
| Agent reports "graph is older than latest commit" | Code graph wasn't updated after a commit. | Run `/code-graph-update`. |

---

## Design principles (for the curious)

The following are non-negotiable across the pipeline:

1. **Never read `code-graph.json` as a file.** Query it via the `knowledge-graph-custom-path` MCP only.
2. **Never read changelog shards.** Append-only. Not even the current quarter.
3. **Bounded-read files** (`current.md`, `_index.md`, `_input.md`, one polished requirement at a time) may be read fully.
4. **Fixed vocabularies** — entity types, relation types, `affected_surface` verbs and resource types. No drift, no inference.
5. **User owns git.** No command commits, pushes, or branches.
6. **Deterministic where possible** — graph math in Python, not LLM reasoning.
7. **Agents create; humans maintain.** The pipeline creates artifacts; editing them after is your job + git's.

---

## What this pipeline does not do

Called out honestly, to set expectations:

- **Does not execute CI.** Tests run at implementation time. Long-term test regression monitoring is outside scope — use actual CI.
- **Does not produce README.md** (deliberately deferred — README generation is synthesis-heavy and drifts easily; left to human judgment for now).
- **Does not manage cross-sprint dependencies.** Sprints are independent planning units. Cross-sprint refs in `semantic_dependencies` are noted but not enforced by the roadmap.
- **Does not do deep code understanding.** The code graph is regex-extracted; it captures structure, not semantics. For "what does this function do," read the code.
- **Does not document sample data.** DB docs never emit sample rows, real or synthesized. Schemas only.
- **Does not handle branch-based workflows.** The pipeline assumes trunk-based development; adapt for your branch model if different.
- **Does not update the pipeline's own docs.** This README is hand-maintained.
