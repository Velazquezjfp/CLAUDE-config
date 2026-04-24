---
description: Implement a polished requirement end-to-end. Reads the requirement file, implements the change strictly within its affected_surface, writes tests for each acceptance criterion, runs them until they pass, and updates the requirement's frontmatter with implemented/tested status. Does not touch git — user commits after review.
argument-hint: <requirement-id>   e.g. S042-F-001
---

# Start Requirement Implementation

Implement requirement **$ARGUMENTS** in the current session. This is the end-to-end implementation flow: plan → code → test → verify → update status. Git operations stay in your hands.

## Arguments

**$ARGUMENTS** — the full compound requirement ID, e.g. `S042-F-001`. Format must be `S{NNN}-{TYPE}-{NNN}`.

## Steps

### 1. Validate and resolve

Parse `$ARGUMENTS`. If the format isn't `S\d{3}-[A-Z]+-\d{3}`, stop and report the expected format.

Derive the sprint number and open the requirement file:
`docs/requirements/sprint-{NNN}/{$ARGUMENTS}.md`

If the file doesn't exist, stop and tell the user: "Requirement $ARGUMENTS not found. Run `/requirement-polish {sprint}` first."

### 2. Read the requirement fully

Read the requirement file fully — it is bounded. Extract:

- **Title, description, acceptance criteria** — what to build.
- **`affected_surface`** (creates / modifies / reads / deletes) — the scope boundary. This is the contract: the implementation may only touch resources listed here.
- **Semantic dependencies** — IDs of other requirements this one depends on. If any are in the current sprint, verify their `status` is `implemented` by reading their frontmatter. If not, warn and ask whether to proceed anyway (the user may be implementing out of order intentionally).
- **Test cases** — the list of test scenarios you'll turn into code.
- **Current status from frontmatter.** If `status: implemented` already, tell the user and ask whether to re-implement (usually no — a re-polish + new requirement is the right answer).

### 3. Ground against current state

Read the three current-state documents if present. These are bounded and fine to read fully:

- `docs/api/current.md` — if the requirement touches endpoints, find them here for context on existing auth, schemas, conventions.
- `docs/database/current.md` — if it touches tables, find them for schema context.
- `docs/environment/current.md` — if it touches env vars, find them for type/sensitivity context.

If a `current.md` file is missing but the requirement touches that domain, warn once and proceed with code-graph queries only.

### 4. Query code-graph for targeted context

Use the `knowledge-graph-custom-path` MCP. **Never call `read_graph`**; only targeted queries:

1. `set_graph_path("./docs/code-graph/code-graph.json")`.
2. `get_statistics` — confirm the graph is populated and fresh enough. If it's missing or clearly stale (older than the latest commit), warn.
3. For each file in `affected_surface.modifies`: `open_nodes` with that file to see what it defines and what imports it. This tells you about ripple effects — if you change a function other files import, those files may need updates too. (They should already appear in `affected_surface` if the requirement is well-scoped — if they don't, that's a scope warning, see step 6.)
4. For each class/function you'll touch directly: `search_nodes` by name to find related entities.

Do not open every file in the codebase. The graph tells you which files matter; read only those.

### 5. Build an implementation plan

Before writing any code, lay out in the session (not as a file — this is conversation-visible):

- Order of changes: new files first, then modifications, deletions last.
- For each affected file, the specific change (new function, modified handler, added column, etc.).
- What tests will be written and how many (one per test case in the requirement).
- Which acceptance criteria map to which tests.

Keep it concise — this is a plan, not a spec. Then start executing.

### 6. Enforce scope: strict with override

For every file you are about to edit, create, or delete, check it against `affected_surface`:

- **File is in `affected_surface.modifies` or `affected_surface.creates`** → proceed.
- **File is in `affected_surface.deletes`** → proceed (only if deleting).
- **File is NOT in `affected_surface`** → **stop before editing.**
  - Report: "Implementation needs to edit `{path}` but it is not in the requirement's `affected_surface`. Reason: {why you thought it needed editing}."
  - Offer three options to the user:
    1. Override once for this file (proceed, and note in the final report that this happened).
    2. Update the requirement (user will re-polish; you'll re-run `/start-requirement` after).
    3. Abort the implementation.
  - Wait for explicit user response before proceeding.

Same check applies to resources (tables, endpoints, env vars) being created or modified — if they're not in the appropriate `affected_surface` list, stop and ask.

**Exception for tests:** files created under `docs/tests/{requirement-id}/` are always in scope. Tests are implicit in every requirement.

### 7. Implement

Write the code. Use normal tool flow — `Read`, `Edit`, `Write`, `Bash` as needed.

Principles:
- Match existing project conventions (inspect neighboring files first).
- Prefer `Edit` over `Write` for existing files; only use `Write` for genuinely new files.
- If your implementation reveals a bug or incomplete spec in the requirement, stop and report — don't silently work around it.
- Don't refactor things not required by the requirement. Even if you see improvements, they're out of scope unless listed in `affected_surface.modifies` with a refactor intent.

### 8. Write tests

Under `docs/tests/{requirement-id}/`, create one Python test file per test case listed in the requirement. File naming: `TC-{requirement-id}-{NN}.py` where `NN` is the test case number (01, 02, ...).

Tests must be:
- **Executable** — `pytest docs/tests/{requirement-id}/` runs them successfully (or fails with real assertions, not `NotImplementedError`).
- **Real** — no `TODO` comments in place of actual assertions. If the acceptance criterion is "returns 201 on valid input," the test actually checks status code 201, not "TODO: check status."
- **Minimal** — one assertion focus per test. Keep each test file short enough that a failure points clearly at which acceptance criterion broke.
- **Independent** — tests should not depend on each other's state. Use fixtures for setup.

If the project already has a `tests/` directory and a testing framework, match that style (pytest fixtures, conftest.py conventions, etc.). Read one or two existing test files for style before writing new ones.

### 9. Run tests

Run: `pytest docs/tests/{requirement-id}/ -v`.

Interpret results:
- **All pass** → proceed to step 10.
- **Some fail** → iterate: diagnose the failure, decide if the bug is in the implementation or the test, fix the right layer, re-run. Don't fix a failing test by weakening its assertion — that's how tests lie.
- **Tests have errors (import failures, setup errors)** → fix the test setup; don't skip.
- **Repeated failures without progress (same test failing the same way after 3 fix attempts)** → stop and report. The requirement may be underspecified or the implementation may need a different approach. Don't loop forever.

### 10. Update requirement frontmatter

Open the requirement file again and update the frontmatter:

```yaml
---
id: S042-F-001
title: ...
type: functional
status: implemented           # was: proposed
created: 2026-04-22T10:00:00Z
implemented_at: 2026-04-23T14:30:00Z       # NEW
tests_passed_at: 2026-04-23T14:35:00Z      # NEW
tests_total: 5                             # NEW
tests_passed: 5                            # NEW
tests_failed: 0                            # NEW
sprint: 042
---
```

Do not modify any other field in the frontmatter. Do not modify the body of the requirement. Do not touch `_index.md` (that's the polisher's job; it'll pick up the new status next time it runs).

### 11. Report

Final summary to the user:

- **Requirement:** ID and title.
- **Files created:** list (including test files).
- **Files modified:** list.
- **Tests:** total / passed / failed.
- **Scope overrides (if any):** files edited outside `affected_surface`, with the reason each was needed. User should consider whether the requirement needs re-polishing to capture the true surface.
- **Pending dependencies (if warned in step 2):** remind the user which were not yet implemented.
- **Next steps:**
  - Review the implementation and tests.
  - `git add` modified + created files.
  - Commit code.
  - Run `/code-graph-update`.
  - Run `/api-doc-update`, `/db-doc-update`, `/env-doc-update` as applicable (the dev command doesn't know which; user decides based on what was touched).
  - Commit the doc updates.
  - Push.

## Hard rules

1. **Never touch git.** No `git add`, no `git commit`, no `git stash`, no branch creation. The user owns the commit boundary.
2. **Never modify files outside `affected_surface`** without explicit user override per invocation.
3. **Never call `read_graph` on the code-graph MCP.** Targeted queries only.
4. **Never skip test writing** to "move faster." Tests are the definition of done.
5. **Never weaken a failing test to make it pass.** Fix the implementation or surface a real problem.
6. **Never update `current.md` files** (API/DB/Env docs). That's the documenters' job, triggered by the user after review.
7. **Never re-polish the requirement** — that's the polisher's job. If a requirement is wrong, stop and tell the user.
8. **Never implement more than one requirement per invocation.** If the user asks for more, decline and suggest running the command per ID.

## When to stop and ask

- Requirement file doesn't exist → suggest `/requirement-polish`.
- Requirement is already `status: implemented` → ask whether to re-implement.
- Scope exceeded (step 6) → present the three options, wait for user response.
- Dependencies not implemented (step 2) → warn and ask whether to proceed.
- Tests failing repeatedly without progress (step 9) → stop and report; user needs to decide.
- Code-graph is clearly stale → warn but proceed if user confirms.
